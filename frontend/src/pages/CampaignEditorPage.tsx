import {
  Bot,
  Eye,
  FileText,
  Lightbulb,
  Save,
  Sparkles,
} from "lucide-react";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
  useParams,
} from "react-router";

import {
  createCampaign,
  generateNewsletter,
  getCampaigns,
  updateCampaign,
} from "../lib/api";

import {
  PageHeader,
} from "../components/PageHeader";

import {
  Spinner,
} from "../components/Spinner";

import type {
  CampaignInput,
} from "../types";

type Tone =
  | "professional"
  | "friendly"
  | "casual"
  | "educational"
  | "promotional";

type Length =
  | "short"
  | "medium"
  | "long";

export default function CampaignEditorPage() {
  const params =
    useParams();

  const navigate =
    useNavigate();

  const queryClient =
    useQueryClient();

  const campaignId =
    params.id
      ? Number(params.id)
      : null;

  const editing =
    campaignId !== null &&
    !Number.isNaN(campaignId);

  const campaignsQuery =
    useQuery({
      queryKey: [
        "campaigns",
      ],
      queryFn: getCampaigns,
      enabled: editing,
    });

  const campaign =
    campaignsQuery.data?.find(
      (item) =>
        item.id === campaignId,
    );

  const [title, setTitle] =
    useState("");

  const [subject, setSubject] =
    useState("");

  const [previewText, setPreviewText] =
    useState("");

  const [content, setContent] =
    useState("");

  const [ctaText, setCtaText] =
    useState("");

  const [ctaUrl, setCtaUrl] =
    useState("");

  const [audience, setAudience] =
    useState("");

  const [topic, setTopic] =
    useState("");

  const [tone, setTone] =
    useState<Tone>(
      "professional",
    );

  const [length, setLength] =
    useState<Length>("medium");

  const [keyPoints, setKeyPoints] =
    useState("");

  const [error, setError] =
    useState("");

  const [saved, setSaved] =
    useState(false);

  useEffect(() => {
    if (!campaign) {
      return;
    }

    setTitle(campaign.title);
    setSubject(
      campaign.subject,
    );
    setPreviewText(
      campaign.preview_text ?? "",
    );
    setContent(
      campaign.content,
    );
    setCtaText(
      campaign.cta_text ?? "",
    );
    setCtaUrl(
      campaign.cta_url ?? "",
    );
    setAudience(
      campaign.audience_description ??
        "",
    );
  }, [campaign]);

  const saveMutation =
    useMutation({
      mutationFn: (
        data: CampaignInput,
      ) =>
        editing && campaignId
          ? updateCampaign(
              campaignId,
              data,
            )
          : createCampaign(data),

      onSuccess: async (
        result,
      ) => {
        await queryClient.invalidateQueries(
          {
            queryKey: [
              "campaigns",
            ],
          },
        );

        setSaved(true);

        if (!editing) {
          navigate(
            `/campaigns/${result.id}/edit`,
            {
              replace: true,
            },
          );
        } else {
          window.setTimeout(
            () =>
              setSaved(false),
            2000,
          );
        }
      },

      onError: (err) => {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to save campaign.",
        );
      },
    });

  const generateMutation =
    useMutation({
      mutationFn:
        generateNewsletter,

      onSuccess: (
        result,
      ) => {
        setSubject(
          result.subject,
        );

        setPreviewText(
          result.preview_text,
        );

        setContent(
          result.content,
        );

        setCtaText(
          result.cta_text,
        );

        if (!title.trim()) {
          setTitle(
            topic.trim() ||
              "AI Generated Campaign",
          );
        }
      },

      onError: (err) => {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to generate newsletter.",
        );
      },
    });

  function generate() {
    setError("");

    if (
      !topic.trim() ||
      !audience.trim()
    ) {
      setError(
        "Enter a topic and audience first.",
      );
      return;
    }

    generateMutation.mutate(
      {
        topic: topic.trim(),
        audience:
          audience.trim(),
        tone,
        length,
        key_points:
          keyPoints
            .split("\n")
            .map(
              (item) =>
                item.trim(),
            )
            .filter(Boolean)
            .slice(0, 10),
      },
    );
  }

  function save(
    event: FormEvent,
  ) {
    event.preventDefault();

    setError("");

    if (!title.trim()) {
      setError(
        "Campaign title is required.",
      );
      return;
    }

    if (!subject.trim()) {
      setError(
        "Subject is required.",
      );
      return;
    }

    if (!content.trim()) {
      setError(
        "Newsletter content is required.",
      );
      return;
    }

    const data: CampaignInput =
      {
        title: title.trim(),
        subject: subject.trim(),
        preview_text:
          previewText.trim() ||
          undefined,
        content: content.trim(),
        cta_text:
          ctaText.trim() ||
          undefined,
        cta_url:
          ctaUrl.trim() ||
          undefined,
        audience_description:
          audience.trim() ||
          undefined,
      };

    saveMutation.mutate(data);
  }

  if (
    editing &&
    campaignsQuery.isLoading
  ) {
    return (
      <div className="center-loader">
        <Spinner size="large" />
      </div>
    );
  }

  if (
    editing &&
    !campaign
  ) {
    return (
      <div className="card">
        <h2>
          Campaign not found
        </h2>

        <p className="muted">
          This campaign may have been
          deleted or you may not have
          access to it.
        </p>

        <button
          type="button"
          className="button secondary"
          onClick={() =>
            navigate(
              "/campaigns",
            )
          }
        >
          Back to campaigns
        </button>
      </div>
    );
  }

  if (
    campaign &&
    campaign.status !== "draft"
  ) {
    return (
      <>
        <PageHeader
          eyebrow="Campaign"
          title="Campaign is not editable"
          description={`This campaign is currently ${campaign.status}.`}
        />

        <div className="card">
          <div className="compact-empty">
            <FileText size={20} />

            <span>
              Only draft campaigns can
              be edited.
            </span>
          </div>

          <button
            type="button"
            className="button secondary"
            onClick={() =>
              navigate(
                "/campaigns",
              )
            }
          >
            Back to campaigns
          </button>
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="AI workspace"
        title={
          editing
            ? "Edit campaign"
            : "Build a campaign"
        }
        description="Generate a first draft with AI, review the message yourself, and save it before sending."
      />

      {error && (
        <div className="form-error page-alert">
          {error}
        </div>
      )}

      {saved && (
        <div className="success-alert page-alert">
          Campaign saved successfully.
        </div>
      )}

      <div className="editor-layout">
        <form
          className="card editor-main"
          onSubmit={save}
        >
          <div className="editor-section-heading">
            <div className="section-icon">
              <FileText size={17} />
            </div>

            <div>
              <strong>
                Campaign content
              </strong>

              <span>
                The final message your
                subscribers will receive.
              </span>
            </div>
          </div>

          <label>
            Campaign title
            <input
              value={title}
              onChange={(event) =>
                setTitle(
                  event.target.value,
                )
              }
              placeholder="September product update"
            />
          </label>

          <label>
            Subject line
            <input
              value={subject}
              onChange={(event) =>
                setSubject(
                  event.target.value,
                )
              }
              placeholder="A strong subject line"
            />
          </label>

          <label>
            Preview text
            <input
              value={previewText}
              onChange={(event) =>
                setPreviewText(
                  event.target.value,
                )
              }
              placeholder="Short preview beside the subject"
            />
          </label>

          <label>
            Audience
            <input
              value={audience}
              onChange={(event) =>
                setAudience(
                  event.target.value,
                )
              }
              placeholder="Computer science students"
            />
          </label>

          <label>
            Newsletter content
            <textarea
              className="content-editor"
              value={content}
              onChange={(event) =>
                setContent(
                  event.target.value,
                )
              }
              placeholder="Write or generate your newsletter..."
            />
          </label>

          <div className="two-col">
            <label>
              CTA text
              <input
                value={ctaText}
                onChange={(event) =>
                  setCtaText(
                    event.target.value,
                  )
                }
                placeholder="Try SmartMail AI"
              />
            </label>

            <label>
              CTA URL
              <input
                value={ctaUrl}
                onChange={(event) =>
                  setCtaUrl(
                    event.target.value,
                  )
                }
                placeholder="https://example.com"
              />
            </label>
          </div>

          <div className="editor-actions">
            <button
              type="button"
              className="button secondary"
              onClick={() =>
                navigate(
                  "/campaigns",
                )
              }
            >
              Cancel
            </button>

            <button
              type="submit"
              className="button primary"
              disabled={
                saveMutation.isPending
              }
            >
              <Save size={15} />

              {saveMutation.isPending
                ? "Saving..."
                : "Save draft"}
            </button>
          </div>
        </form>

        <aside className="editor-side">
          <div className="card">
            <div className="editor-section-heading">
              <div className="section-icon ai">
                <Bot size={17} />
              </div>

              <div>
                <strong>
                  Generate with AI
                </strong>

                <span>
                  Gemini with Groq fallback.
                </span>
              </div>
            </div>

            <div className="builder-fields">
              <label>
                Topic
                <input
                  value={topic}
                  onChange={(event) =>
                    setTopic(
                      event.target.value,
                    )
                  }
                  placeholder="What is the newsletter about?"
                />
              </label>

              <label>
                Audience
                <input
                  value={audience}
                  onChange={(event) =>
                    setAudience(
                      event.target.value,
                    )
                  }
                  placeholder="Who is it for?"
                />
              </label>

              <div className="two-col">
                <label>
                  Tone
                  <select
                    value={tone}
                    onChange={(event) =>
                      setTone(
                        event.target.value as Tone,
                      )
                    }
                  >
                    <option value="professional">
                      Professional
                    </option>

                    <option value="friendly">
                      Friendly
                    </option>

                    <option value="casual">
                      Casual
                    </option>

                    <option value="educational">
                      Educational
                    </option>

                    <option value="promotional">
                      Promotional
                    </option>
                  </select>
                </label>

                <label>
                  Length
                  <select
                    value={length}
                    onChange={(event) =>
                      setLength(
                        event.target.value as Length,
                      )
                    }
                  >
                    <option value="short">
                      Short
                    </option>

                    <option value="medium">
                      Medium
                    </option>

                    <option value="long">
                      Long
                    </option>
                  </select>
                </label>
              </div>

              <label>
                Key points
                <textarea
                  rows={5}
                  value={keyPoints}
                  onChange={(event) =>
                    setKeyPoints(
                      event.target.value,
                    )
                  }
                  placeholder={`One point per line
New feature
Important announcement
Call to action`}
                />
              </label>

              <button
                type="button"
                className="button ai-button full"
                onClick={generate}
                disabled={
                  generateMutation.isPending
                }
              >
                <Sparkles size={16} />

                {generateMutation.isPending
                  ? "Generating..."
                  : "Generate newsletter"}
              </button>

              <div className="human-review-note">
                <Lightbulb size={15} />

                <span>
                  AI generates a draft. Review
                  and edit it before sending.
                </span>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="preview-toolbar">
              <div>
                <Eye size={15} />
                Live preview
              </div>

              <span>
                Email
              </span>
            </div>

            <div className="email-preview">
              <div className="email-brand">
                SmartMail AI
              </div>

              <div className="email-subject">
                {subject ||
                  "Your subject line"}
              </div>

              <div className="email-preview-text">
                {previewText ||
                  "Your preview text will appear here."}
              </div>

              <div className="email-divider" />

              <div className="email-content">
                {content ||
                  "Your newsletter content will appear here."}
              </div>

              {ctaText && (
                <div className="email-cta">
                  {ctaText}
                </div>
              )}

              <div className="email-footer">
                You are receiving this
                email from SmartMail AI.
              </div>
            </div>
          </div>
        </aside>
      </div>
    </>
  );
}