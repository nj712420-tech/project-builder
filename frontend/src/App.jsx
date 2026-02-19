import { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [includeDb, setIncludeDb] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleBuild = async () => {
    if (!prompt) return;
    setIsLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/build', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: prompt, include_db: includeDb }),
      });

      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data.detail || "server error occurred." });
        return;
      }
      setResult(data);
    } catch (error) {
      console.error("Error building project:", error);
      setResult({ error: "Failed to connect to the backend." });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container" style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
      <h1>⚡ AI Project Builder</h1>
      
      {/* --- INPUT SECTION --- */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '30px' }}>
        <textarea 
          rows="4"
          placeholder="What do you want to build? (e.g., A beautiful To-Do list web app with a dark mode theme)"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          style={{ padding: '10px', fontSize: '16px', borderRadius: '5px' }}
        />
        
        <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
          <input 
            type="checkbox" 
            checked={includeDb}
            onChange={(e) => setIncludeDb(e.target.checked)}
          />
          Include SQLite Database
        </label>

        <button 
          onClick={handleBuild} 
          disabled={isLoading}
          style={{ padding: '12px', fontSize: '16px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px' }}
        >
          {isLoading ? 'Building in Cloud...' : 'Go'}
        </button>
      </div>

      {/* --- RESULTS SECTION --- */}
      {result && !result.error && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', textAlign: 'left' }}>
          
          <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '5px', borderLeft: '4px solid #28a745' }}>
            <h3 style={{ marginTop: 0 }}>Explanation</h3>
            <p style={{ margin: 0 }}>{result.explanation}</p>
          </div>

          <div style={{ backgroundColor: '#282c34', color: '#abb2bf', padding: '15px', borderRadius: '5px', overflowX: 'auto' }}>
            <h3 style={{ color: 'white', marginTop: 0 }}>Generated Code</h3>
            <pre style={{ margin: 0, textAlign: 'left', whiteSpace: 'pre' }}>
              <code style={{ fontFamily: 'monospace' }}>{result.code}</code>
            </pre>
          </div>

          {/* --- THE LIVE PREVIEW IFRAME --- */}
          {result.preview_url && (
            <div style={{ backgroundColor: '#f0f0f0', padding: '15px', borderRadius: '5px', border: '1px solid #ccc' }}>
              <h3 style={{ marginTop: 0, color: '#333' }}>Live Web App Preview</h3>
              <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                <a href={`https://${result.preview_url}`} target="_blank" rel="noreferrer" style={{ fontSize: '14px', color: '#007bff', textDecoration: 'none', fontWeight: 'bold' }}>
                  Open App in New Tab ↗
                </a>
              </div>
              {/* This iframe embeds the E2B server directly into your UI */}
              <iframe 
                src={`https://${result.preview_url}`} 
                style={{ width: '100%', height: '500px', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#fff' }}
                title="App Preview"
              />
            </div>
          )}

          {/* Keeping this for debugging server logs (e.g., if Flask crashes) */}
          <div style={{ backgroundColor: '#1e1e1e', color: '#4af626', padding: '15px', borderRadius: '5px', overflowX: 'auto' }}>
            <h3 style={{ color: 'white', marginTop: 0 }}>Live Sandbox Output (Server Logs)</h3>
            <pre style={{ margin: 0, textAlign: 'left', whiteSpace: 'pre-wrap' }}>
              <code style={{ fontFamily: 'monospace' }}>{result.sandbox_output || "No output returned."}</code>
            </pre>
          </div>

        </div>
      )}

      {result?.error && (
        <div style={{ color: 'red', padding: '15px', border: '1px solid red', borderRadius: '5px' }}>
          {result.error}
        </div>
      )}
    </div>
  );
}

export default App;