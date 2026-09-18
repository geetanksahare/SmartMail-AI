import {
  Activity,
  ArrowUpRight,
  Mail,
  MousePointerClick,
  Send,
  Users,
} from "lucide-react";

import {
  useQueries,
  useQuery,
} from "@tanstack/react-query";

import {
  Link,
} from "react-router";

import {
  getCampaignAnalytics,
  getCampaigns,
  getSubscribers,
} from "../lib/api";

import {
  PageHeader,
} from "../components/PageHeader";

import {
  StatCard,
} from "../components/StatCard";

import {
  Spinner,
} from "../components/Spinner";

import {
  EmptyState,
} from "../components/EmptyState";

import type {
  Analytics,
} from "../types";


export default function DashboardPage() {
  const subscribersQuery =
    useQuery({
      queryKey: [
        "subscribers",
        {
          page: 1,
          page_size: 100,
        },
      ],
      queryFn: () =>
        getSubscribers({
          page: 1,
          page_size: 100,
        }),
    });


  const campaignsQuery =
    useQuery({
      queryKey: [
        "campaigns",
      ],
      queryFn:
        getCampaigns,

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


  const subscribers =
    subscribersQuery.data
      ?.items ?? [];


  const campaigns =
    campaignsQuery.data ??
    [];


  const sentCampaigns =
    campaigns.filter(
      (campaign) =>
        campaign.status ===
        "sent",
    );


  const analyticsQueries =
    useQueries({
      queries:
        sentCampaigns.map(
          (campaign) => ({
            queryKey: [
              "analytics",
              campaign.id,
            ],

            queryFn: () =>
              getCampaignAnalytics(
                campaign.id,
              ),

            staleTime: 30_000,
          }),
        ),
    });


  const analytics =
    analyticsQueries
      .map(
        (query) =>
          query.data,
      )
      .filter(
        (
          item,
        ): item is Analytics =>
          Boolean(item),
      );


  const totalSent =
    analytics.reduce(
      (
        total,
        item,
      ) =>
        total + item.sent,
      0,
    );


  const totalDelivered =
    analytics.reduce(
      (
        total,
        item,
      ) =>
        total +
        item.delivered,
      0,
    );


  const totalOpened =
    analytics.reduce(
      (
        total,
        item,
      ) =>
        total +
        item.opened,
      0,
    );


  const totalClicked =
    analytics.reduce(
      (
        total,
        item,
      ) =>
        total +
        item.clicked,
      0,
    );


  const openRate =
    totalDelivered > 0
      ? Math.round(
          (totalOpened /
            totalDelivered) *
            100,
        )
      : 0;


  const clickRate =
    totalDelivered > 0
      ? Math.round(
          (totalClicked /
            totalDelivered) *
            100,
        )
      : 0;


  const activeSubscribers =
    subscribers.filter(
      (subscriber) =>
        subscriber.status ===
        "active",
    ).length;


  if (
    subscribersQuery.isLoading ||
    campaignsQuery.isLoading
  ) {
    return (
      <div className="center-loader">
        <Spinner size="large" />
      </div>
    );
  }


  if (
    subscribersQuery.isError ||
    campaignsQuery.isError
  ) {
    return (
      <>
        <PageHeader
          eyebrow="Workspace overview"
          title="Dashboard"
          description="Unable to load your workspace data."
        />

        <div className="card">
          <div className="compact-empty">
            <span>
              Please refresh the page or
              sign in again.
            </span>
          </div>
        </div>
      </>
    );
  }


  return (
    <>
      <PageHeader
        eyebrow="Workspace overview"
        title="Good to see you."
        description="A quick view of your audience, campaigns and engagement."
        actions={
          <Link
            to="/campaigns/new"
            className="button primary"
          >
            <Mail size={16} />
            Create campaign
          </Link>
        }
      />


      <section className="stats-grid">
        <StatCard
          label="Subscribers"
          value={
            subscribersQuery.data
              ?.total ?? 0
          }
          helper={`${activeSubscribers} active`}
          icon={Users}
        />

        <StatCard
          label="Messages sent"
          value={totalSent}
          helper="Across sent campaigns"
          icon={Send}
        />

        <StatCard
          label="Open rate"
          value={`${openRate}%`}
          helper="Across delivered mail"
          icon={Activity}
        />

        <StatCard
          label="Click rate"
          value={`${clickRate}%`}
          helper="Across delivered mail"
          icon={
            MousePointerClick
          }
        />
      </section>


      <section className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <div>
              <span className="eyebrow">
                Activity
              </span>

              <h2>
                Recent campaigns
              </h2>
            </div>

            <Link
              to="/campaigns"
              className="text-link"
            >
              View all
              <ArrowUpRight size={15} />
            </Link>
          </div>


          {campaigns.length ===
          0 ? (
            <EmptyState
              title="No campaigns yet"
              description="Create your first AI-assisted newsletter."
              action={
                <Link
                  to="/campaigns/new"
                  className="button primary"
                >
                  Create campaign
                </Link>
              }
            />
          ) : (
            <div className="campaign-list">
              {campaigns
                .slice(0, 6)
                .map(
                  (campaign) => (
                    <div
                      className="campaign-row"
                      key={
                        campaign.id
                      }
                    >
                      <div className="campaign-row-icon">
                        <Mail
                          size={
                            17
                          }
                        />
                      </div>

                      <div className="campaign-row-main">
                        <strong>
                          {
                            campaign.title
                          }
                        </strong>

                        <span>
                          {
                            campaign.subject
                          }
                        </span>
                      </div>

                      <StatusBadge
                        status={
                          campaign.status
                        }
                      />
                    </div>
                  ),
                )}
            </div>
          )}
        </div>


        <div className="card ai-dashboard-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">
                AI workspace
              </span>

              <h2>
                Turn ideas into campaigns
              </h2>
            </div>
          </div>

          <div className="ai-callout">
            <div className="ai-glow">
              ✦
            </div>

            <h3>
              Start with a topic
            </h3>

            <p>
              SmartMail AI generates
              subject lines, preview text,
              newsletter copy and CTAs.
              You review everything before
              sending.
            </p>

            <Link
              to="/campaigns/new"
              className="button secondary"
            >
              Open AI Builder
              <ArrowUpRight
                size={15}
              />
            </Link>
          </div>
        </div>
      </section>
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