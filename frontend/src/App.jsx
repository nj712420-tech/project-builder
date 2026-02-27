// import { useState } from 'react';
// import './App.css';

// function App() {
//   const [prompt, setPrompt] = useState('');
//   const [includeDb, setIncludeDb] = useState(false);
//   const [isLoading, setIsLoading] = useState(false);
//   const [result, setResult] = useState(null);

//   const handleBuild = async () => {
//     if (!prompt) return;
//     setIsLoading(true);
//     setResult(null);

//     try {
//       const response = await fetch('http://127.0.0.1:8000/api/v1/build', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ prompt: prompt, include_db: includeDb }),
//       });

//       const data = await response.json();
//       if (!response.ok) {
//         setResult({ error: data.detail || "server error occurred." });
//         return;
//       }
//       setResult(data);
//     } catch (error) {
//       console.error("Error building project:", error);
//       setResult({ error: "Failed to connect to the backend." });
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="container" style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
//       <h1>⚡ AI Project Builder</h1>
      
//       {/* --- INPUT SECTION --- */}
//       <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '30px' }}>
//         <textarea 
//           rows="4"
//           placeholder="What do you want to build? (e.g., A beautiful To-Do list web app with a dark mode theme)"
//           value={prompt}
//           onChange={(e) => setPrompt(e.target.value)}
//           style={{ padding: '10px', fontSize: '16px', borderRadius: '5px' }}
//         />
        
//         <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
//           <input 
//             type="checkbox" 
//             checked={includeDb}
//             onChange={(e) => setIncludeDb(e.target.checked)}
//           />
//           Include SQLite Database
//         </label>

//         <button 
//           onClick={handleBuild} 
//           disabled={isLoading}
//           style={{ padding: '12px', fontSize: '16px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px' }}
//         >
//           {isLoading ? 'Building in Cloud...' : 'Go'}
//         </button>
//       </div>

//       {/* --- RESULTS SECTION --- */}
//       {result && !result.error && (
//         <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', textAlign: 'left' }}>
          
//           <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '5px', borderLeft: '4px solid #28a745' }}>
//             <h3 style={{ marginTop: 0 }}>Explanation</h3>
//             <p style={{ margin: 0 }}>{result.explanation}</p>
//           </div>

//           <div style={{ backgroundColor: '#282c34', color: '#abb2bf', padding: '15px', borderRadius: '5px', overflowX: 'auto' }}>
//             <h3 style={{ color: 'white', marginTop: 0 }}>Generated Code</h3>
//             <pre style={{ margin: 0, textAlign: 'left', whiteSpace: 'pre' }}>
//               <code style={{ fontFamily: 'monospace' }}>{result.code}</code>
//             </pre>
//           </div>

//           {/* --- THE LIVE PREVIEW IFRAME --- */}
//           {result.preview_url && (
//             <div style={{ backgroundColor: '#f0f0f0', padding: '15px', borderRadius: '5px', border: '1px solid #ccc' }}>
//               <h3 style={{ marginTop: 0, color: '#333' }}>Live Web App Preview</h3>
//               <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
//                 <a href={`https://${result.preview_url}`} target="_blank" rel="noreferrer" style={{ fontSize: '14px', color: '#007bff', textDecoration: 'none', fontWeight: 'bold' }}>
//                   Open App in New Tab ↗
//                 </a>
//               </div>
//               {/* This iframe embeds the E2B server directly into your UI */}
//               <iframe 
//                 src={`https://${result.preview_url}`} 
//                 style={{ width: '100%', height: '500px', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: '#fff' }}
//                 title="App Preview"
//               />
//             </div>
//           )}

//           {/* Keeping this for debugging server logs (e.g., if Flask crashes) */}
//           <div style={{ backgroundColor: '#1e1e1e', color: '#4af626', padding: '15px', borderRadius: '5px', overflowX: 'auto' }}>
//             <h3 style={{ color: 'white', marginTop: 0 }}>Live Sandbox Output (Server Logs)</h3>
//             <pre style={{ margin: 0, textAlign: 'left', whiteSpace: 'pre-wrap' }}>
//               <code style={{ fontFamily: 'monospace' }}>{result.sandbox_output || "No output returned."}</code>
//             </pre>
//           </div>

//         </div>
//       )}

//       {result?.error && (
//         <div style={{ color: 'red', padding: '15px', border: '1px solid red', borderRadius: '5px' }}>
//           {result.error}
//         </div>
//       )}
//     </div>
//   );
// }

// export default App;


import { useState } from 'react';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import { Play, Download, Code, Eye, Terminal, AlertCircle } from 'lucide-react';

function App() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('preview');

  const handleBuild = async () => {
    setLoading(true);
    setResult(null); // Clear previous results
    try {
      const response = await fetch('/api/v1/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, include_db: false }),
      });
      const data = await response.json();
      setResult(data);
      
      // Automatically switch to error view if build failed
      if (data.status === 'error') {
        setActiveTab('preview');
      }
    } catch (error) {
      console.error(error);
      setResult({ 
        status: 'error', 
        error: 'Failed to connect to backend. Is the Python server running?' 
      });
    }
    setLoading(false);
  };

  const handleDownload = async () => {
    // SAFETY CHECK: Only run if files exist
    if (!result?.files) return;
    
    const zip = new JSZip();
    Object.entries(result.files).forEach(([filename, content]) => {
      zip.file(filename, content);
    });

    const blob = await zip.generateAsync({ type: 'blob' });
    saveAs(blob, 'ai-project.zip');
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* HEADER */}
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-blue-600 rounded-lg shadow-lg shadow-blue-500/50">
            <Terminal className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">AI Project Architect</h1>
        </div>

        {/* INPUT */}
        <div className="bg-gray-800 rounded-xl p-6 shadow-2xl border border-gray-700">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your full-stack app (e.g., 'A Kanban board with drag-and-drop')..."
            className="w-full h-32 bg-gray-900 border border-gray-700 rounded-lg p-4 text-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all resize-none"
          />
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleBuild}
              disabled={loading}
              className={`flex items-center space-x-2 px-8 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 ${
                loading ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-500/30'
              }`}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Architecting...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Build Project</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* RESULTS AREA */}
        {result && (
          <div className="space-y-6">
            
            {/* TAB CONTROLS */}
            <div className="flex justify-between items-center bg-gray-800 p-2 rounded-lg border border-gray-700">
              <div className="flex space-x-2">
                <button
                  onClick={() => setActiveTab('preview')}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${
                    activeTab === 'preview' ? 'bg-blue-600 text-white shadow-md' : 'text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  <Eye className="w-4 h-4" />
                  <span>Live Preview</span>
                </button>
                
                {/* Disable Code Tab if Error */}
                <button
                  onClick={() => result.status === 'success' && setActiveTab('code')}
                  disabled={result.status !== 'success'}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${
                    activeTab === 'code' 
                      ? 'bg-blue-600 text-white shadow-md' 
                      : result.status === 'success' 
                        ? 'text-gray-400 hover:text-white hover:bg-gray-700'
                        : 'text-gray-600 cursor-not-allowed'
                  }`}
                >
                  <Code className="w-4 h-4" />
                  <span>Source Code</span>
                </button>
              </div>

              {/* DOWNLOAD BUTTON (Only show on success) */}
              {result.status === 'success' && (
                <button
                  onClick={handleDownload}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-md font-medium transition-all shadow-lg shadow-green-500/20"
                >
                  <Download className="w-4 h-4" />
                  <span>Download .zip</span>
                </button>
              )}
            </div>

            {/* TAB 1: PREVIEW */}
            {activeTab === 'preview' && (
              <div className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700 h-[600px] shadow-2xl relative">
                {result.status === 'error' ? (
                  <div className="p-8 text-red-400 font-mono flex flex-col items-center justify-center h-full text-center">
                    <AlertCircle className="w-16 h-16 mb-4 opacity-50" />
                    <h3 className="text-2xl font-bold mb-2">Build Failed</h3>
                    <p className="max-w-md text-gray-400 mb-6">{result.error}</p>
                    <div className="w-full max-w-2xl bg-gray-900 rounded-lg p-4 overflow-auto max-h-64 text-left text-xs text-red-300 border border-red-900/50">
                      <pre>{result.sandbox_output || "No server logs available."}</pre>
                    </div>
                  </div>
                ) : (
                  <iframe
                    // FIX: Ensure URL starts with https:// to prevent local loop
                    src={result.preview_url.startsWith('http') ? result.preview_url : `https://${result.preview_url}`}
                    className="w-full h-full bg-white"
                    title="App Preview"
                    sandbox="allow-scripts allow-same-origin allow-forms"
                  />
                )}
              </div>
            )}

            {/* TAB 2: CODE EXPLORER (Protected) */}
            {activeTab === 'code' && result.files && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 h-[600px]">
                {/* File List */}
                <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 overflow-y-auto col-span-1">
                  <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Project Files</h3>
                  <ul className="space-y-2">
                    {Object.keys(result.files).map((filename) => (
                      <li key={filename} className="flex items-center space-x-2 text-sm font-mono text-blue-400 p-2 bg-gray-900/50 rounded border border-gray-800">
                        <span>📄</span>
                        <span className="truncate" title={filename}>{filename}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Code Viewer */}
                <div className="bg-gray-900 rounded-xl p-4 border border-gray-700 overflow-auto col-span-3 font-mono text-sm text-gray-300">
                  {Object.entries(result.files).map(([filename, content]) => (
                    <div key={filename} className="mb-12">
                      <div className="flex items-center justify-between border-b border-gray-800 pb-2 mb-4">
                        <span className="text-green-400 font-bold">{filename}</span>
                        <span className="text-xs text-gray-600">{content.split('\n').length} lines</span>
                      </div>
                      <pre className="whitespace-pre-wrap leading-relaxed opacity-90">{content}</pre>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* EXPLANATION CARD */}
            <div className="bg-gray-800 rounded-xl p-6 border-l-4 border-blue-500 shadow-lg">
              <h3 className="text-lg font-semibold text-white mb-2 flex items-center">
                <Terminal className="w-5 h-5 mr-2 text-blue-400" />
                Architect's Notes
              </h3>
              <p className="text-gray-300 leading-relaxed text-sm">
                {result.explanation}
              </p>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}

export default App;