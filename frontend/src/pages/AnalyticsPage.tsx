import {
  Activity,
  ArrowLeft,
  BarChart3,
  Bot,
  MousePointerClick,
  Send,
  Sparkles,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";

import type {
  LucideIcon,
} from "lucide-react";

import {
  useMutation,
  useQuery,
} from "@tanstack/react-query";

import {
  Link,
  useParams,
} from "react-router";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  analyzeCampaign,
  getCampaignAnalytics,
  getCampaigns,
} from "../lib/api";

import {
  PageHeader,
} from "../components/PageHeader";

import {
  Spinner,
} from "../components/Spinner";


export default function AnalyticsPage() {
  const { id } =
    useParams();

  const campaignId =
    Number(id);


  const campaignsQuery =
    useQuery({
      queryKey: [
        "campaigns",
      ],
      queryFn:
        getCampaigns,

      staleTime: 0,

      refetchOnWindowFocus:
        true,

      refetchInterval: 10_000,
    });


  const campaign =
    campaignsQuery.data?.find(
      (item) =>
        item.id === campaignId,
    );


  const analyticsQuery =
    useQuery({
      queryKey: [
        "analytics",
        campaignId,
      ],

      queryFn: () =>
        getCampaignAnalytics(
          campaignId,
        ),

      enabled:
        Number.isFinite(
          campaignId,
        ),

      staleTime: 0,

      refetchOnWindowFocus:
        true,

      refetchInterval: (
        query,
      ) => {
        if (
          query.state.status ===
          "error"
        ) {
          return false;
        }

        /*
         * Keep checking for Brevo events.
         *
         * Even after "sent", delivery/open/click
         * events can arrive later.
         */
        return 5000;
      },
    });


  const aiMutation =
    useMutation({
      mutationFn: () =>
        analyzeCampaign(
          campaignId,
        ),
    });


  if (
    campaignsQuery.isLoading ||
    analyticsQuery.isLoading
  ) {
    return (
      <div className="center-loader">
        <Spinner size="large" />
      </div>
    );
  }


  if (
    campaignsQuery.isError ||
    analyticsQuery.isError
  ) {
    return (
      <div className="card">
        <h2>
          Unable to load analytics
        </h2>

        <p className="muted">
          Please refresh the page and
          try again.
        </p>

        <Link
          to="/campaigns"
          className="button secondary"
        >
          <ArrowLeft size={15} />
          Back to campaigns
        </Link>
      </div>
    );
  }


  const analytics =
    analyticsQuery.data;


  if (
    !campaign ||
    !analytics
  ) {
    return (
      <div className="card">
        <h2>
          Analytics unavailable
        </h2>

        <p className="muted">
          The campaign could not be
          loaded.
        </p>

        <Link
          to="/campaigns"
          className="button secondary"
        >
          <ArrowLeft size={15} />
          Back to campaigns
        </Link>
      </div>
    );
  }


  const funnelData = [
    {
      name: "Sent",
      value: analytics.sent,
    },
    {
      name: "Delivered",
      value:
        analytics.delivered,
    },
    {
      name: "Opened",
      value:
        analytics.opened,
    },
    {
      name: "Clicked",
      value:
        analytics.clicked,
    },
  ];


  return (
    <>
      <Link
        to="/campaigns"
        className="back-link"
      >
        <ArrowLeft size={15} />
        Back to campaigns
      </Link>


      <PageHeader
        eyebrow="Campaign performance"
        title={campaign.title}
        description={campaign.subject}
        actions={
          <button
            type="button"
            className="button ai-button"
            onClick={() =>
              aiMutation.mutate()
            }
            disabled={
              aiMutation.isPending
            }
          >
            <Sparkles size={16} />

            {aiMutation.isPending
              ? "Analyzing..."
              : "Analyze with AI"}
          </button>
        }
      />


      <section className="stats-grid">
        <MetricCard
          label="Recipients"
          value={
            analytics.total_recipients
          }
          icon={Users}
        />

        <MetricCard
          label="Delivered"
          value={`${analytics.delivery_rate}%`}
          helper={`${analytics.delivered} delivered`}
          icon={Send}
        />

        <MetricCard
          label="Open rate"
          value={`${analytics.open_rate}%`}
          helper={`${analytics.opened} opened`}
          icon={Activity}
        />

        <MetricCard
          label="Click rate"
          value={`${analytics.click_rate}%`}
          helper={`${analytics.clicked} clicked`}
          icon={
            MousePointerClick
          }
        />
      </section>


      <section className="analytics-grid">
        <div className="card">
          <div className="card-header">
            <div>
              <span className="eyebrow">
                Engagement
              </span>

              <h2>
                Campaign funnel
              </h2>
            </div>

            <span className="live-indicator">
              ● Live
            </span>
          </div>


          <div className="chart-wrap">
            <ResponsiveContainer
              width="100%"
              height={310}
            >
              <LineChart
                data={funnelData}
                margin={{
                  top: 10,
                  right: 10,
                  left: -20,
                  bottom: 0,
                }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e6e9f0"
                />

                <XAxis
                  dataKey="name"
                  tick={{
                    fill: "#667085",
                    fontSize: 12,
                  }}
                />

                <YAxis
                  allowDecimals={
                    false
                  }
                  tick={{
                    fill: "#667085",
                    fontSize: 12,
                  }}
                />

                <Tooltip />

                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#5b5ce2"
                  strokeWidth={3}
                  dot={{
                    r: 5,
                    fill: "#5b5ce2",
                  }}
                  isAnimationActive={
                    true
                  }
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>


        <div className="card">
          <div className="card-header">
            <div>
              <span className="eyebrow">
                Delivery health
              </span>

              <h2>
                Audience journey
              </h2>
            </div>
          </div>


          <div className="health-list">
            <HealthRow
              label="Sent"
              value={
                analytics.sent
              }
              percentage={100}
            />

            <HealthRow
              label="Delivered"
              value={
                analytics.delivered
              }
              percentage={
                analytics.delivery_rate
              }
            />

            <HealthRow
              label="Opened"
              value={
                analytics.opened
              }
              percentage={
                analytics.open_rate
              }
            />

            <HealthRow
              label="Clicked"
              value={
                analytics.clicked
              }
              percentage={
                analytics.click_rate
              }
            />

            <HealthRow
              label="Bounced"
              value={
                analytics.bounced
              }
              percentage={
                analytics.bounce_rate
              }
              danger
            />
          </div>
        </div>
      </section>


      <section className="analytics-summary-grid">
        <MiniMetric
          icon={TrendingUp}
          label="Delivered"
          value={
            analytics.delivered
          }
        />

        <MiniMetric
          icon={BarChart3}
          label="Bounced"
          value={
            analytics.bounced
          }
        />

        <MiniMetric
          icon={Target}
          label="Complaints"
          value={
            analytics.complained
          }
        />

        <MiniMetric
          icon={Bot}
          label="Unsubscribed"
          value={
            analytics.unsubscribed
          }
        />
      </section>


      {aiMutation.data && (
        <section className="ai-analysis-section">
          <div className="ai-analysis-header">
            <div className="ai-heading-icon">
              <Sparkles size={18} />
            </div>

            <div>
              <span className="eyebrow">
                SmartMail AI
              </span>

              <h2>
                Campaign intelligence
              </h2>

              <p>
                AI interpretation based on
                your actual campaign data.
              </p>
            </div>
          </div>


          <div className="ai-summary">
            <span>
              Summary
            </span>

            <p>
              {
                aiMutation.data
                  .summary
              }
            </p>
          </div>


          <div className="analysis-columns">
            <AnalysisCard
              title="Strengths"
              items={
                aiMutation.data
                  .strengths
              }
              tone="positive"
            />

            <AnalysisCard
              title="Issues"
              items={
                aiMutation.data
                  .issues
              }
              tone="warning"
            />

            <AnalysisCard
              title="Recommendations"
              items={
                aiMutation.data
                  .recommendations
              }
              tone="ai"
            />
          </div>
        </section>
      )}
    </>
  );
}


function MetricCard({
  label,
  value,
  helper,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  helper?: string;
  icon: LucideIcon;
}) {
  return (
    <div className="stat-card">
      <div className="stat-card-top">
        <div className="stat-icon">
          <Icon size={18} />
        </div>

        <span>{label}</span>
      </div>

      <strong>{value}</strong>

      {helper && (
        <small>{helper}</small>
      )}
    </div>
  );
}


function HealthRow({
  label,
  value,
  percentage,
  danger = false,
}: {
  label: string;
  value: number;
  percentage?: number;
  danger?: boolean;
}) {
  return (
    <div className="health-row">
      <div className="health-label">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>

      <div className="health-track">
        <span
          className={
            danger
              ? "danger-bar"
              : ""
          }
          style={{
            width: `${Math.min(
              percentage ?? 0,
              100,
            )}%`,
          }}
        />
      </div>

      <small>
        {percentage !== undefined
          ? `${percentage}%`
          : ""}
      </small>
    </div>
  );
}


function MiniMetric({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: number;
}) {
  return (
    <div className="mini-metric">
      <div className="mini-icon">
        <Icon size={17} />
      </div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}


function AnalysisCard({
  title,
  items,
  tone,
}: {
  title: string;
  items: string[];
  tone:
    | "positive"
    | "warning"
    | "ai";
}) {
  return (
    <div className="analysis-card">
      <div
        className={`analysis-dot ${tone}`}
      />

      <h3>{title}</h3>

      {items.length ===
      0 ? (
        <p className="muted">
          Nothing significant detected.
        </p>
      ) : (
        <div className="analysis-list">
          {items.map(
            (
              item,
              index,
            ) => (
              <div
                className="analysis-item"
                key={index}
              >
                {item}
              </div>
            ),
          )}
        </div>
      )}
    </div>
  );
}