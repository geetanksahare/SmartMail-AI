import {
  BarChart3,
  LayoutDashboard,
  LogOut,
  Mail,
  Sparkles,
  Users,
} from "lucide-react";

import {
  NavLink,
  useNavigate,
} from "react-router";

import {
  useAuth,
} from "../context/AuthContext";

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const navigation = [
  {
    label: "Overview",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Subscribers",
    path: "/subscribers",
    icon: Users,
  },
  {
    label: "Campaigns",
    path: "/campaigns",
    icon: Mail,
  },
  {
    label: "AI Builder",
    path: "/campaigns/new",
    icon: Sparkles,
  },
];

export function Sidebar({
  open,
  onClose,
}: SidebarProps) {
  const {
    signOut,
  } = useAuth();

  const navigate =
    useNavigate();

  function logout() {
    signOut();
    navigate("/login");
  }

  return (
    <>
      {open && (
        <div
          className="mobile-backdrop"
          onClick={onClose}
        />
      )}

      <aside
        className={`sidebar ${
          open
            ? "sidebar-open"
            : ""
        }`}
      >
        <div className="sidebar-brand">
          <div className="logo-mark">
            <Sparkles size={18} />
          </div>

          <div className="brand-wordmark">
            <strong>
              SmartMail
            </strong>

            <span>AI</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <span className="sidebar-label">
            Workspace
          </span>

          {navigation.map(
            ({
              label,
              path,
              icon: Icon,
            }) => (
              <NavLink
                key={path}
                to={path}
                end={path === "/"}
                onClick={onClose}
                className={({
                  isActive,
                }) =>
                  `sidebar-link ${
                    isActive
                      ? "active"
                      : ""
                  }`
                }
              >
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            ),
          )}
        </nav>

        <div className="sidebar-spacer" />

        <button
          type="button"
          className="sidebar-link logout-link"
          onClick={logout}
        >
          <LogOut size={18} />
          <span>Sign out</span>
        </button>

        <div className="sidebar-footer">
          <div className="sidebar-footer-icon">
            <BarChart3 size={15} />
          </div>

          <div>
            <strong>
              Campaign intelligence
            </strong>

            <span>
              SmartMail AI
            </span>
          </div>
        </div>
      </aside>
    </>
  );
}