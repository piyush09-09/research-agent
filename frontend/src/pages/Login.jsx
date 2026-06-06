import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Logo from "../components/Logo";

export default function Login() {
  const [searchParams] = useSearchParams();
  const [isSignup, setIsSignup] = useState(searchParams.get("mode") === "signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setIsSignup(searchParams.get("mode") === "signup");
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // TODO: Wire to backend auth endpoint
    // For now, simulate login and go to dashboard
    setTimeout(() => {
      localStorage.setItem("token", "demo-token");
      localStorage.setItem("user", JSON.stringify({ name: name || "User", email }));
      setLoading(false);
      navigate("/app");
    }, 800);
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <div onClick={() => navigate("/")} style={{ cursor: "pointer" }}>
            <Logo size={32} />
          </div>
          <h1>{isSignup ? "Create your account" : "Welcome back"}</h1>
          <p className="auth-subtitle">
            {isSignup
              ? "Start researching with AI agents"
              : "Log in to continue your research"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {isSignup && (
            <div className="form-field">
              <label>Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required={isSignup}
              />
            </div>
          )}
          <div className="form-field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>
          <div className="form-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
            />
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? (
              <span className="btn-loading">
                <span className="spinner" />
                {isSignup ? "Creating account..." : "Logging in..."}
              </span>
            ) : isSignup ? (
              "Create Account"
            ) : (
              "Log In"
            )}
          </button>
        </form>

        <div className="auth-switch">
          {isSignup ? (
            <p>
              Already have an account?{" "}
              <button onClick={() => setIsSignup(false)}>Log in</button>
            </p>
          ) : (
            <p>
              Don't have an account?{" "}
              <button onClick={() => setIsSignup(true)}>Sign up</button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}