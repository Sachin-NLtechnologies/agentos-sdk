import { useAuth } from "../App";

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#0B0A12", display: "flex", flexDirection: "column" }}>
      <header style={{ borderBottom: "1px solid rgba(160, 140, 255, 0.14)", padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{ width: "12px", height: "12px", borderRadius: "50%", backgroundColor: "#A3E635" }} />
          <h2 style={{ margin: 0, fontSize: "18px", fontWeight: "600" }}>__AGENT_ID__</h2>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <span style={{ fontSize: "14px", color: "#A39FB8" }}>{user?.email} ({user?.role})</span>
          <button
            onClick={logout}
            style={{ padding: "8px 16px", borderRadius: "8px", border: "1px solid rgba(251, 113, 133, 0.3)", backgroundColor: "rgba(251, 113, 133, 0.05)", color: "#FB7185", cursor: "pointer" }}
          >
            Logout
          </button>
        </div>
      </header>

      <main style={{ flex: 1, padding: "40px", display: "flex", justifyContent: "center", alignItems: "center" }}>
        <div className="glass" style={{ width: "100%", maxWidth: "800px", padding: "40px", textAlign: "center" }}>
          <h1 style={{ fontSize: "36px", margin: "0 0 16px 0", color: "#F4F2FF" }}>Welcome to __AGENT_ID__</h1>
          <p style={{ fontSize: "16px", color: "#A39FB8", margin: "0 0 32px 0", lineHeight: "1.6" }}>
            This agent is scaffolded with full Django + Vite capability. Its OIDC SSO authentication, database connection, and platform worker loops are active.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px", marginTop: "24px" }}>
            <div className="glass" style={{ padding: "20px" }}>
              <h3 style={{ margin: "0 0 8px 0", color: "#7C5CFF" }}>Status</h3>
              <p style={{ margin: 0, fontSize: "20px", fontWeight: "bold", color: "#A3E635" }}>ONLINE</p>
            </div>
            <div className="glass" style={{ padding: "20px" }}>
              <h3 style={{ margin: "0 0 8px 0", color: "#7C5CFF" }}>Capabilities</h3>
              <p style={{ margin: 0, fontSize: "16px", color: "#F4F2FF" }}>example</p>
            </div>
            <div className="glass" style={{ padding: "20px" }}>
              <h3 style={{ margin: "0 0 8px 0", color: "#7C5CFF" }}>Local DB</h3>
              <p style={{ margin: 0, fontSize: "16px", color: "#F4F2FF" }}>SQLite</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
