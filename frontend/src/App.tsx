import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

interface Classification {
  intent: string;
  confidence: string;
  sentiment: string;
  priority: string;
  recommended_action: string;
  summary: string;
}

interface Routing {
  intent: string;
  priority: string;
  sentiment: string;
  urgency_score: number;
  recommended_action: string;
  route_to: string;
  estimated_resolution: string;
  summary: string;
}

interface AnalysisResult {
  status: string;
  complaint: string;
  classification: Classification;
  routing: Routing;
  total_latency: number;
}

const PRIORITY_COLORS: Record<string, string> = {
  high: '#FF6B6B',
  medium: '#FFA500',
  low: '#50C878',
  none: '#888'
};

const SENTIMENT_COLORS: Record<string, string> = {
  angry: '#FF6B6B',
  frustrated: '#FFA500',
  neutral: '#4A90D9',
  satisfied: '#50C878'
};

const SAMPLE_COMPLAINTS = [
  "My ThinkPad screen cracked after one week and nobody is responding to my emails.",
  "I want a full refund. This laptop has had 3 issues in the first month.",
  "My laptop fan is making a loud grinding noise. I need it repaired immediately.",
  "My order was supposed to arrive 5 days ago and I have no tracking updates.",
  "My ThinkPad is stuck in a boot loop and will not load Windows."
];

function Badge({ label, color }: { label: string; color: string }) {
  return (
    <span style={{
      background: color + '22',
      color: color,
      border: `1px solid ${color}`,
      borderRadius: 6,
      padding: '2px 10px',
      fontSize: 12,
      fontWeight: 600,
      textTransform: 'uppercase',
      letterSpacing: 1
    }}>{label}</span>
  );
}

function App() {
  const [complaint, setComplaint] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyze = async () => {
    if (!complaint.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await axios.post('http://localhost:8000/analyze', {
        complaint,
        model: 'llama3.2'
      });
      setResult(res.data);
    } catch (e) {
      setError('Could not connect to LenServe API. Make sure the backend is running.');
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0F0F0F', color: '#F0F0F0', fontFamily: 'monospace' }}>
      <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 20px' }}>

        <div style={{ marginBottom: 40 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, color: '#E8E8E8', margin: 0 }}>
            LenServe
          </h1>
          <p style={{ color: '#888', marginTop: 6, fontSize: 14 }}>
            AI After-Sales Support Classifier — powered by llama3.2 running locally
          </p>
        </div>

        <div style={{ marginBottom: 24 }}>
          <p style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>Try a sample complaint:</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {SAMPLE_COMPLAINTS.map((s, i) => (
              <button key={i} onClick={() => setComplaint(s)} style={{
                background: '#1A1A1A', border: '1px solid #333',
                borderRadius: 6, padding: '4px 10px',
                color: '#AAA', fontSize: 11, cursor: 'pointer'
              }}>
                Sample {i + 1}
              </button>
            ))}
          </div>
        </div>

        <textarea
          value={complaint}
          onChange={e => setComplaint(e.target.value)}
          placeholder="Paste a customer complaint here..."
          rows={4}
          style={{
            width: '100%', background: '#1A1A1A', border: '1px solid #333',
            borderRadius: 8, padding: 16, color: '#F0F0F0',
            fontSize: 14, resize: 'vertical', outline: 'none',
            boxSizing: 'border-box'
          }}
        />

        <button
          onClick={analyze}
          disabled={loading || !complaint.trim()}
          style={{
            marginTop: 12, width: '100%', padding: '12px 0',
            background: loading ? '#333' : '#4A90D9',
            color: '#fff', border: 'none', borderRadius: 8,
            fontSize: 14, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer',
            fontFamily: 'monospace'
          }}
        >
          {loading ? 'Analyzing...' : 'Analyze Complaint'}
        </button>

        {error && (
          <div style={{ marginTop: 16, padding: 12, background: '#FF6B6B22',
            border: '1px solid #FF6B6B', borderRadius: 8, color: '#FF6B6B', fontSize: 13 }}>
            {error}
          </div>
        )}

        {result && (
          <div style={{ marginTop: 32 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: 0 }}>Analysis Result</h2>
              <span style={{ fontSize: 12, color: '#888' }}>
                {result.total_latency}s latency
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
              <div style={{ background: '#1A1A1A', border: '1px solid #333',
                borderRadius: 8, padding: 16 }}>
                <p style={{ fontSize: 11, color: '#888', margin: '0 0 8px' }}>INTENT</p>
                <p style={{ fontSize: 20, fontWeight: 700, margin: 0, textTransform: 'capitalize' }}>
                  {result.classification.intent}
                </p>
              </div>
              <div style={{ background: '#1A1A1A', border: '1px solid #333',
                borderRadius: 8, padding: 16 }}>
                <p style={{ fontSize: 11, color: '#888', margin: '0 0 8px' }}>ROUTE TO</p>
                <p style={{ fontSize: 16, fontWeight: 700, margin: 0, textTransform: 'capitalize' }}>
                  {result.routing?.route_to?.replace(/_/g, ' ')}
                </p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 12 }}>
              <div style={{ background: '#1A1A1A', border: '1px solid #333',
                borderRadius: 8, padding: 16 }}>
                <p style={{ fontSize: 11, color: '#888', margin: '0 0 8px' }}>PRIORITY</p>
                <Badge label={result.classification.priority}
                  color={PRIORITY_COLORS[result.classification.priority]} />
              </div>
              <div style={{ background: '#1A1A1A', border: '1px solid #333',
                borderRadius: 8, padding: 16 }}>
                <p style={{ fontSize: 11, color: '#888', margin: '0 0 8px' }}>SENTIMENT</p>
                <Badge label={result.classification.sentiment}
                  color={SENTIMENT_COLORS[result.classification.sentiment] || '#888'} />
              </div>
              <div style={{ background: '#1A1A1A', border: '1px solid #333',
                borderRadius: 8, padding: 16 }}>
                <p style={{ fontSize: 11, color: '#888', margin: '0 0 8px' }}>URGENCY</p>
                <p style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>
                  {result.routing?.urgency_score}/10
                </p>
              </div>
            </div>

            <div style={{ background: '#1A1A1A', border: '1px solid #333',
              borderRadius: 8, padding: 16, marginBottom: 12 }}>
              <p style={{ fontSize: 11, color: '#888', margin: '0 0 8px' }}>RECOMMENDED ACTION</p>
              <p style={{ fontSize: 14, margin: 0, lineHeight: 1.6 }}>
                {result.routing?.recommended_action}
              </p>
            </div>

            <div style={{ background: '#1A1A1A', border: '1px solid #333',
              borderRadius: 8, padding: 16, marginBottom: 12 }}>
              <p style={{ fontSize: 11, color: '#888', margin: '0 0 8px' }}>ESTIMATED RESOLUTION</p>
              <p style={{ fontSize: 14, margin: 0 }}>{result.routing?.estimated_resolution}</p>
            </div>

            <div style={{ background: '#1A1A1A', border: '1px solid #333',
              borderRadius: 8, padding: 16 }}>
              <p style={{ fontSize: 11, color: '#888', margin: '0 0 8px' }}>SUMMARY</p>
              <p style={{ fontSize: 14, margin: 0, lineHeight: 1.6 }}>
                {result.classification.summary}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;