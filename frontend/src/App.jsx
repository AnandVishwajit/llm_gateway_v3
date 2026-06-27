import { useState, useEffect } from "react"
import axios from "axios"

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
const API_KEY = "8c7d5b2f1e9a4c6d3f8b7a1e5d9c2f4a8b6e1d3c7f9a2b5d4e8f1c6a3b7d9e201"

const headers = { "X-API-Key": API_KEY }

export default function App() {
  const [stats, setStats] = useState(null)
  const [message, setMessage] = useState("")
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_BASE}/stats`, { headers })
      setStats(res.data)
    } catch (e) {
      console.error("Failed to fetch stats")
    }
  }

  const sendMessage = async () => {
    if (!message.trim()) return
    setLoading(true)
    setError("")
    setResponse(null)
    try {
      const res = await axios.post(`${API_BASE}/chat`, { message }, { headers })
      setResponse(res.data)
      fetchStats()
    } catch (e) {
      if (e.response?.status === 429) {
        setError("Rate limit exceeded. Wait a minute and try again.")
      } else {
        setError("Something went wrong.")
      }
    }
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: 700, margin: "40px auto", fontFamily: "sans-serif", padding: "0 20px" }}>
      <h1 style={{ fontSize: 24, marginBottom: 4 }}>LLM Gateway</h1>
      <p style={{ color: "#666", marginBottom: 32 }}>Semantic caching proxy powered by Groq + pgvector</p>

      {/* Stats */}
      {stats && (
        <div style={{ display: "flex", gap: 16, marginBottom: 32 }}>
          <StatCard label="Cached Entries" value={stats.total_cached_entries} />
          <StatCard label="Tokens Used" value={stats.total_tokens_used} />
          <StatCard label="Tokens Saved" value={stats.total_cached_entries * 50 + " est."} />
        </div>
      )}

      {/* Chat */}
      <div style={{ marginBottom: 16 }}>
        <textarea
          rows={3}
          value={message}
          onChange={e => setMessage(e.target.value)}
          placeholder="Ask something..."
          style={{ width: "100%", padding: 12, fontSize: 15, borderRadius: 8, border: "1px solid #ddd", boxSizing: "border-box" }}
        />
      </div>
      <button
        onClick={sendMessage}
        disabled={loading}
        style={{ padding: "10px 24px", background: "#2563eb", color: "white", border: "none", borderRadius: 8, fontSize: 15, cursor: "pointer" }}
      >
        {loading ? "Thinking..." : "Send"}
      </button>

      {/* Response */}
      {response && (
        <div style={{ marginTop: 24, padding: 16, background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0" }}>
          <div style={{ display: "flex", gap: 12, marginBottom: 8 }}>
            <Badge label={response.cached ? "⚡ Cached" : "🌐 Fresh"} color={response.cached ? "#16a34a" : "#2563eb"} />
            <Badge label={`${response.tokens_used} tokens`} color="#64748b" />
          </div>
          <p style={{ margin: 0, lineHeight: 1.6 }}>{response.response}</p>
        </div>
      )}

      {error && (
        <div style={{ marginTop: 16, padding: 12, background: "#fef2f2", borderRadius: 8, color: "#dc2626" }}>
          {error}
        </div>
      )}
    </div>
  )
}

function StatCard({ label, value }) {
  return (
    <div style={{ flex: 1, padding: 16, background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0" }}>
      <div style={{ fontSize: 24, fontWeight: 700 }}>{value}</div>
      <div style={{ fontSize: 13, color: "#64748b", marginTop: 4 }}>{label}</div>
    </div>
  )
}

function Badge({ label, color }) {
  return (
    <span style={{ padding: "2px 10px", borderRadius: 99, fontSize: 12, background: color, color: "white" }}>
      {label}
    </span>
  )
}