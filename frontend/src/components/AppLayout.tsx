import {
  Bell,
  Menu,
} from "lucide-react";

import {
  Outlet,
  useLocation,
} from "react-router";

import {
  useState,
} from "react";

import {
  Sidebar,
} from "./Sidebar";

const pageTitles: Record<
  string,
  string
> = {
  "/": "Overview",
  "/subscribers": "Subscribers",
  "/campaigns": "Campaigns",
  "/campaigns/new":
    "AI Campaign Builder",
};

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const location =
    useLocation();

  const title =
    pageTitles[
      location.pathname
    ] ?? (
      location.pathname.includes(
        "/analytics",
      )
        ? "Campaign Analytics"
        : location.pathname.includes(
              "/edit",
            )
          ? "Edit Campaign"
          : "SmartMail AI"
    );

  return (
    <div className="app-shell">
      <Sidebar
        open={sidebarOpen}
        onClose={() =>
          setSidebarOpen(false)
        }
      />

      <div className="app-main">
        <header className="topbar">
          <button
            type="button"
            className="mobile-menu"
            onClick={() =>
              setSidebarOpen(true)
            }
            aria-label="Open navigation"
          >
            <Menu size={20} />
          </button>

          <div className="topbar-title">
            <span>
              SmartMail AI
            </span>

            <strong>
              {title}
            </strong>
          </div>

          <button
            type="button"
            className="icon-button"
            aria-label="Notifications"
          >
            <Bell size={18} />
          </button>
        </header>

        <main className="page-container">
          <Outlet />
        </main>
      </div>
    </div>
  );
}