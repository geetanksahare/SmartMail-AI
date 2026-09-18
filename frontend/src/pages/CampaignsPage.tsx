import {
  BarChart3,
  Edit3,
  Mail,
  Plus,
  Send,
  Trash2,
} from "lucide-react";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  Link,
  useNavigate,
} from "react-router";

import {
  useMemo,
  useState,
} from "react";

import {
  deleteCampaign,
  getCampaigns,
  sendCampaign,
} from "../lib/api";

import {
  PageHeader,
} from "../components/PageHeader";

import {
  Spinner,
} from "../components/Spinner";

import {
  EmptyState,
} from "../components/EmptyState";

import type {
  Campaign,
} from "../types";

type Filter =
  | "all"
  | "draft"
  | "sending"
  | "sent"
  | "failed";

export default function CampaignsPage() {
  const navigate =
    useNavigate();

  const queryClient =
    useQueryClient();

  const campaignsQuery =
    useQuery({
      queryKey: [
        "campaigns",
      ],
      queryFn: getCampaigns,
      refetchInterval: (
        query,
      ) => {
        const active =
          query.state.data?.some(
            (campaign) =>
              campaign.status ===
                "sending" ||
              campaign.status ===
                "scheduled",
          );

        return active
          ? 4000
          : false;
      },
    });

  const [filter, setFilter] =
    useState<Filter>("all");

  const [search, setSearch] =
    useState("");

  const [error, setError] =
    useState("");

  const sendMutation =
    useMutation({
      mutationFn:
        sendCampaign,

      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: [
            "campaigns",
          ],
        });
      },

      onError: (err) => {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to send campaign.",
        );
      },
    });

  const deleteMutation =
    useMutation({
      mutationFn:
        deleteCampaign,

      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: [
            "campaigns",
          ],
        });
      },

      onError: (err) => {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to delete campaign.",
        );
      },
    });

  const campaigns =
    campaignsQuery.data ?? [];

  const filtered =
    useMemo(() => {
      const term =
        search
          .trim()
          .toLowerCase();

      return campaigns.filter(
        (campaign) => {
          const matchesFilter =
            filter === "all" ||
            campaign.status ===
              filter;

          if (!matchesFilter) {
            return false;
          }

          if (!term) {
            return true;
          }

          return (
            campaign.title
              .toLowerCase()
              .includes(term) ||
            campaign.subject
              .toLowerCase()
              .includes(term)
          );
        },
      );
    }, [
      campaigns,
      filter,
      search,
    ]);

  function handleSend(
    campaign: Campaign,
  ) {
    if (
      !window.confirm(
        `Send "${campaign.title}" to all active subscribers?`,
      )
    ) {
      return;
    }

    sendMutation.mutate(
      campaign.id,
    );
  }

  function handleDelete(
    campaign: Campaign,
  ) {
    if (
      !window.confirm(
        `Delete "${campaign.title}"?`,
      )
    ) {
      return;
    }

    deleteMutation.mutate(
      campaign.id,
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Outbound"
        title="Campaigns"
        description="Create, review, send and analyze newsletters."
        actions={
          <Link
            to="/campaigns/new"
            className="button primary"
          >
            <Plus size={16} />
            New campaign
          </Link>
        }
      />

      {error && (
        <div className="form-error page-alert">
          {error}
        </div>
      )}

      <div className="card">
        <div className="campaign-toolbar">
          <div className="search-box">
            <Mail size={16} />

            <input
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value,
                )
              }
              placeholder="Search campaigns..."
            />
          </div>

          <div className="filter-tabs">
            {(
              [
                "all",
                "draft",
                "sending",
                "sent",
                "failed",
              ] as Filter[]
            ).map((item) => (
              <button
                type="button"
                key={item}
                className={
                  filter === item
                    ? "filter-tab active"
                    : "filter-tab"
                }
                onClick={() =>
                  setFilter(item)
                }
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        {campaignsQuery.isLoading ? (
          <div className="center-loader">
            <Spinner size="medium" />
          </div>
        ) : filtered.length ===
          0 ? (
          <EmptyState
            title={
              campaigns.length ===
              0
                ? "No campaigns yet"
                : "No matching campaigns"
            }
            description={
              campaigns.length ===
              0
                ? "Create your first newsletter with the AI Builder."
                : "Try a different search or filter."
            }
            action={
              campaigns.length ===
              0 ? (
                <Link
                  to="/campaigns/new"
                  className="button primary"
                >
                  <Plus size={16} />
                  Create campaign
                </Link>
              ) : undefined
            }
          />
        ) : (
          <div className="campaign-cards">
            {filtered.map(
              (campaign) => (
                <article
                  key={campaign.id}
                  className="campaign-card"
                >
                  <div className="campaign-card-top">
                    <div className="campaign-icon">
                      <Mail size={18} />
                    </div>

                    <StatusBadge
                      status={
                        campaign.status
                      }
                    />
                  </div>

                  <div className="campaign-card-copy">
                    <h3>
                      {
                        campaign.title
                      }
                    </h3>

                    <p>
                      {
                        campaign.subject
                      }
                    </p>

                    {campaign.preview_text && (
                      <span>
                        {
                          campaign.preview_text
                        }
                      </span>
                    )}
                  </div>

                  <div className="campaign-card-meta">
                    <span>
                      Created{" "}
                      {new Date(
                        campaign.created_at,
                      ).toLocaleDateString()}
                    </span>

                    {campaign.sent_at && (
                      <span>
                        Sent{" "}
                        {new Date(
                          campaign.sent_at,
                        ).toLocaleDateString()}
                      </span>
                    )}
                  </div>

                  <div className="campaign-card-actions">
                    {campaign.status ===
                      "draft" && (
                      <>
                        <button
                          type="button"
                          className="button secondary small"
                          onClick={() =>
                            navigate(
                              `/campaigns/${campaign.id}/edit`,
                            )
                          }
                        >
                          <Edit3
                            size={14}
                          />
                          Edit
                        </button>

                        <button
                          type="button"
                          className="button primary small"
                          disabled={
                            sendMutation.isPending
                          }
                          onClick={() =>
                            handleSend(
                              campaign,
                            )
                          }
                        >
                          <Send
                            size={14}
                          />
                          Send
                        </button>
                      </>
                    )}

                    {campaign.status ===
                      "sending" && (
                      <button
                        type="button"
                        className="button secondary small"
                        disabled
                      >
                        Sending...
                      </button>
                    )}

                    {campaign.status ===
                      "failed" && (
                      <button
                        type="button"
                        className="button primary small"
                        disabled={
                          sendMutation.isPending
                        }
                        onClick={() =>
                          handleSend(
                            campaign,
                          )
                        }
                      >
                        <Send
                          size={14}
                        />
                        Retry
                      </button>
                    )}

                    {campaign.status ===
                      "sent" && (
                      <Link
                        to={`/campaigns/${campaign.id}/analytics`}
                        className="button secondary small"
                      >
                        <BarChart3
                          size={14}
                        />
                        Analytics
                      </Link>
                    )}

                    {(campaign.status ===
                      "draft" ||
                      campaign.status ===
                        "failed") && (
                      <button
                        type="button"
                        className="icon-button danger"
                        onClick={() =>
                          handleDelete(
                            campaign,
                          )
                        }
                        aria-label={`Delete ${campaign.title}`}
                      >
                        <Trash2
                          size={15}
                        />
                      </button>
                    )}
                  </div>
                </article>
              ),
            )}
          </div>
        )}
      </div>
    </>
  );
}

function StatusBadge({
  status,
}: {
  status: string;
}) {
  return (
    <span
      className={`status-badge status-${status}`}
    >
      {status}
    </span>
  );
}