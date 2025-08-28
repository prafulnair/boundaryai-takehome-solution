import { useState } from "react";

export default function GenerateSurveyButton({ onLoaded }) {
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    const description = window.prompt(
      "Describe your survey (e.g., 'Customer satisfaction for an online store')"
    );
    if (!description) return;
    setLoading(true);
    try {
      const base = process.env.REACT_APP_API_BASE || "http://localhost:8000";
      const res = await fetch(`${base}/api/surveys/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      onLoaded?.(data); // { id, title, questions[], cached }
    } catch (e) {
      console.error(e);
      alert("Failed to generate survey. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      className="ml-3 rounded-md bg-purple-600 text-white px-3 py-2 disabled:opacity-60"
      onClick={handleClick}
      disabled={loading}
    >
      {loading ? "Generating…" : "Generate Survey"}
    </button>
  );
}