import { useState } from "react";
import { useAuth } from "../App";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      navigate("/");
    } catch {
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", alignItems: "center", justifyContent: "center", backgroundColor: "#0B0A12", padding: "0 24px" }}>
      <div className="glass" style={{ width: "100%", maxWidth: "400px", padding: "32px", boxSizing: "border-box" }}>
        <p style={{ textTransform: "uppercase", letterSpacing: "0.25em", color: "#7C5CFF", fontSize: "12px", margin: 0 }}>AgentOS Fleet</p>
        <h1 style={{ fontSize: "28px", fontWeight: "600", marginTop: "16px", marginBottom: "8px" }}>Sign in to Agent</h1>
        <p style={{ fontSize: "14px", color: "#A39FB8", margin: "0 0 24px 0" }}>
          Access the dashboard of this custom AgentOS agent.
        </p>

        {error && (
          <div style={{ backgroundColor: "rgba(251, 113, 133, 0.1)", border: "1px solid rgba(251, 113, 133, 0.3)", borderRadius: "12px", padding: "12px", color: "#FB7185", fontSize: "14px", marginBottom: "20px" }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <label style={{ display: "block", fontSize: "14px", marginBottom: "6px", color: "#A39FB8" }}>Username or Email</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ width: "100%", padding: "12px", borderRadius: "12px", border: "1px solid rgba(160, 140, 255, 0.14)", backgroundColor: "rgba(0,0,0,0.2)", color: "#F4F2FF", outline: "none", boxSizing: "border-box" }}
              required
              disabled={loading}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "14px", marginBottom: "6px", color: "#A39FB8" }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: "100%", padding: "12px", borderRadius: "12px", border: "1px solid rgba(160, 140, 255, 0.14)", backgroundColor: "rgba(0,0,0,0.2)", color: "#F4F2FF", outline: "none", boxSizing: "border-box" }}
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{ width: "100%", padding: "12px", borderRadius: "12px", backgroundColor: "#7C5CFF", color: "#F4F2FF", border: "none", fontWeight: "600", cursor: "pointer", transition: "background 0.2s" }}
          >
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>

        <div style={{ display: "flex", alignItems: "center", margin: "24px 0", gap: "12px" }}>
          <div style={{ height: "1px", flex: 1, backgroundColor: "rgba(160, 140, 255, 0.14)" }} />
          <span style={{ fontSize: "12px", color: "#A39FB8" }}>or</span>
          <div style={{ height: "1px", flex: 1, backgroundColor: "rgba(160, 140, 255, 0.14)" }} />
        </div>

        <button
          type="button"
          onClick={() => {
            try { localStorage.removeItem("agentos.auth.logged_out"); } catch {}
            window.location.href = "/api/auth/agentos/start/";
          }}
          style={{ display: "block", textDecoration: "none", textAlign: "center", padding: "12px", width: "100%", borderRadius: "12px", border: "1px solid rgba(160, 140, 255, 0.2)", backgroundColor: "rgba(160, 140, 255, 0.05)", color: "#F4F2FF", fontWeight: "600", transition: "background 0.2s", cursor: "pointer" }}
        >
          Login with AgentOS
        </button>
      </div>
    </div>
  );
}
