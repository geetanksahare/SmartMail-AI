import {
  ArrowRight,
  Sparkles,
  UserRoundPlus,
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

export default function RegisterPage() {
  const {
    isAuthenticated,
    signUp,
  } = useAuth();

  const navigate =
    useNavigate();

  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

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

    if (!name.trim()) {
      setError(
        "Name is required.",
      );
      return;
    }

    if (!email.trim()) {
      setError(
        "Email is required.",
      );
      return;
    }

    if (
      password.length < 8
    ) {
      setError(
        "Password must contain at least 8 characters.",
      );
      return;
    }

    if (
      password !==
      confirmPassword
    ) {
      setError(
        "Passwords do not match.",
      );
      return;
    }

    setLoading(true);

    try {
      await signUp(
        name.trim(),
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
          : "Unable to create account.",
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
            Build better campaigns
          </span>

          <h1>
            Your email
            <br />
            <span>
              command center.
            </span>
          </h1>

          <p>
            Create AI-assisted newsletters,
            deliver them through a reliable
            background pipeline, and turn
            campaign activity into insights.
          </p>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-form-wrap">
          <div className="auth-heading">
            <div className="auth-icon">
              <UserRoundPlus size={18} />
            </div>

            <span>
              Get started
            </span>

            <h2>
              Create your workspace
            </h2>

            <p>
              Your account gives you a
              private campaign workspace.
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
              Full name
              <input
                value={name}
                onChange={(event) =>
                  setName(
                    event.target.value,
                  )
                }
                placeholder="Your name"
                autoComplete="name"
              />
            </label>

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
                placeholder="At least 8 characters"
                autoComplete="new-password"
              />
            </label>

            <label>
              Confirm password
              <input
                type="password"
                value={
                  confirmPassword
                }
                onChange={(event) =>
                  setConfirmPassword(
                    event.target.value,
                  )
                }
                placeholder="Repeat your password"
                autoComplete="new-password"
              />
            </label>

            <button
              type="submit"
              className="button primary full"
              disabled={loading}
            >
              {loading
                ? "Creating workspace..."
                : "Create account"}

              {!loading && (
                <ArrowRight size={16} />
              )}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account?{" "}
            <Link to="/login">
              Sign in
            </Link>
          </p>
        </div>
      </section>
    </div>
  );
}