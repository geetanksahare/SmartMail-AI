import {
  ArrowRight,
  LockKeyhole,
  Sparkles,
} from "lucide-react";

import {
  FormEvent,
  useState,
} from "react";

import {
  Link,
  Navigate,
  useNavigate,
} from "react-router";

import {
  useAuth,
} from "../context/AuthContext";

export default function LoginPage() {
  const {
    isAuthenticated,
    signIn,
  } = useAuth();

  const navigate =
    useNavigate();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  if (isAuthenticated) {
    return (
      <Navigate to="/" replace />
    );
  }

  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    setError("");

    if (
      !email.trim() ||
      !password
    ) {
      setError(
        "Enter your email and password.",
      );
      return;
    }

    setLoading(true);

    try {
      await signIn(
        email.trim(),
        password,
      );

      navigate("/", {
        replace: true,
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to sign in.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-layout">
      <section className="auth-showcase">
        <div className="showcase-brand">
          <div className="logo-mark large">
            <Sparkles size={21} />
          </div>

          <strong>
            SmartMail AI
          </strong>
        </div>

        <div className="showcase-content">
          <span className="eyebrow light">
            AI-powered email intelligence
          </span>

          <h1>
            Create smarter
            <br />
            <span>
              email campaigns.
            </span>
          </h1>

          <p>
            Generate newsletters with AI,
            keep human control over every
            draft, and understand exactly
            how your campaigns perform.
          </p>

          <div className="showcase-points">
            <div>
              <strong>
                AI-first
              </strong>

              <span>
                Generate polished campaigns
                in seconds.
              </span>
            </div>

            <div>
              <strong>
                Data-driven
              </strong>

              <span>
                Track delivery, opens and
                clicks in real time.
              </span>
            </div>

            <div>
              <strong>
                Human review
              </strong>

              <span>
                You control the final message
                before it goes out.
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-form-wrap">
          <div className="auth-mobile-brand">
            <div className="logo-mark">
              <Sparkles size={17} />
            </div>

            <strong>
              SmartMail AI
            </strong>
          </div>

          <div className="auth-heading">
            <div className="auth-icon">
              <LockKeyhole size={18} />
            </div>

            <span>
              Welcome back
            </span>

            <h2>
              Sign in to your workspace
            </h2>

            <p>
              Manage your audience,
              campaigns and insights.
            </p>
          </div>

          {error && (
            <div className="form-error">
              {error}
            </div>
          )}

          <form
            className="auth-form"
            onSubmit={submit}
          >
            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(
                    event.target.value,
                  )
                }
                placeholder="you@example.com"
                autoComplete="email"
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(
                    event.target.value,
                  )
                }
                placeholder="Your password"
                autoComplete="current-password"
              />
            </label>

            <button
              type="submit"
              className="button primary full"
              disabled={loading}
            >
              {loading
                ? "Signing in..."
                : "Sign in"}

              {!loading && (
                <ArrowRight size={16} />
              )}
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account?{" "}
            <Link to="/register">
              Create one
            </Link>
          </p>
        </div>
      </section>
    </div>
  );
}