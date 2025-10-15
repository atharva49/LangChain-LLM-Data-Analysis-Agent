import React, { useState } from 'react';

function App() {
  const [question, setQuestion] = useState('What is the total revenue in Texas?');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

  async function ask() {
    setLoading(true);
    setAnswer('');
    try {
      const resp = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const data = await resp.json();
      if (!resp.ok) {
        setAnswer('Error: ' + (data.detail || JSON.stringify(data)));
      } else {
        setAnswer(data.answer);
      }
    } catch (e) {
      setAnswer('Request failed: ' + String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: 800, margin: '40px auto' }}>
      <h1>ChatGPT + SQLite (FastAPI backend)</h1>
      <p>Ask a natural question about the sample sales DB.</p>

      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={3}
        style={{ width: '100%', fontSize: 16 }}
      />

      <div style={{ marginTop: 12 }}>
        <button onClick={ask} disabled={loading} style={{ padding: '8px 16px', fontSize: 16 }}>
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </div>

      <div style={{ marginTop: 20 }}>
        <h3>Answer</h3>
        <pre style={{ background: '#f4f4f4', padding: 12 }}>{answer}</pre>
      </div>
    </div>
  );
}

export default App;
