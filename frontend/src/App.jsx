import { useState, useEffect, useRef } from 'react';
import { logApi } from './api';
import { AlertCircle, CheckCircle2, Clock, ShieldAlert, Upload } from 'lucide-react';

function App() {
  const [logs, setLogs] = useState([]);
  const [inputLog, setInputLog] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  
  // Reference to trigger the hidden file input
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const loadRandomSample = async () => {
    try {
      const response = await fetch('/sample.txt');
      const text = await response.text();
      
      const logBlocks = text.match(/---LOG_START[\s\S]*?---LOG_END---/g);
      
      if (logBlocks && logBlocks.length > 0) {
        const randomIndex = Math.floor(Math.random() * logBlocks.length);
        let selectedLog = logBlocks[randomIndex];
        
        selectedLog = selectedLog
          .replace(/---LOG_START.*?---\n?/, '') 
          .replace(/\n?---LOG_END---/, '')      
          .trim();

        setInputLog(selectedLog);
        setError(null);
      } else {
        setError("Could not parse log format. Check sample.txt structure.");
      }
    } catch (err) {
      console.error("Could not load sample logs:", err);
      setError("Failed to load sample data file.");
    }
  };

  // Handles the file upload directly in the browser
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Optional: Prevent massive files from freezing the browser text area (e.g., limit to 2MB)
    if (file.size > 2 * 1024 * 1024) {
      setError("File is too large. Please upload a log file smaller than 2MB.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setInputLog(e.target.result);
      setError(null);
    };
    reader.onerror = () => {
      setError("Failed to read the uploaded file.");
    };
    reader.readAsText(file);
    
    // Reset input so the same file can be selected again if needed
    event.target.value = null;
  };

  const fetchLogs = async () => {
    try {
      const data = await logApi.getLogs();
      setLogs(data);
    } catch (err) {
      console.error("Failed to fetch logs:", err);
    }
  };

  const handleAnalyze = async () => {
    if (inputLog.trim().length < 10) {
      setError("Log must be at least 10 characters long.");
      return;
    }
    
    setIsAnalyzing(true);
    setError(null);

    try {
      await logApi.submitLog(inputLog);
      setInputLog('');
      await fetchLogs(); 
    } catch (err) {
      setError(err.response?.data?.detail?.[0]?.msg || err.response?.data?.detail || "Failed to analyze log.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getSeverityBadge = (severity) => {
    const colors = {
      Critical: "bg-red-100 text-red-800 border-red-200",
      Warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
      Info: "bg-blue-100 text-blue-800 border-blue-200"
    };
    return colors[severity] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <ShieldAlert className="text-indigo-600" />
            LogSleuth
          </h1>
          <p className="text-gray-500 mt-1">AI-Powered Log Anomaly Detector</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
          <h2 className="text-lg font-semibold">New Analysis</h2>
          {error && (
            <div className="p-3 bg-red-50 text-red-700 rounded-md text-sm border border-red-100">
              {error}
            </div>
          )}
          
          <textarea
            value={inputLog}
            onChange={(e) => setInputLog(e.target.value)}
            placeholder="Paste raw server log here..."
            className="w-full h-48 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
          />
          
          {/* Button Container */}
          <div className="flex gap-4 flex-wrap">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2 transition-colors"
            >
              {isAnalyzing ? <Clock className="animate-spin w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
              {isAnalyzing ? 'Analyzing with Groq...' : 'Analyze Log'}
            </button>
            
            <button
              onClick={loadRandomSample}
              disabled={isAnalyzing}
              className="bg-white text-indigo-600 border border-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-50 disabled:opacity-50 flex items-center gap-2 transition-colors font-medium"
            >
              Load Sample Log
            </button>

            {/* Hidden file input */}
            <input 
              type="file" 
              accept=".txt,.log,.csv" 
              className="hidden" 
              ref={fileInputRef}
              onChange={handleFileUpload}
            />
            
            {/* Upload Button */}
            <button
              onClick={() => fileInputRef.current.click()}
              disabled={isAnalyzing}
              className="bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 disabled:opacity-50 flex items-center gap-2 transition-colors font-medium ml-auto"
            >
              <Upload className="w-4 h-4" />
              Upload File
            </button>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="p-4 font-semibold text-gray-600">Status</th>
                <th className="p-4 font-semibold text-gray-600">Severity</th>
                <th className="p-4 font-semibold text-gray-600">Root Cause</th>
                <th className="p-4 font-semibold text-gray-600">Suggested Fix</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="p-4">
                    {log.status === 'success' ? (
                      <CheckCircle2 className="text-green-500 w-5 h-5" />
                    ) : (
                      <AlertCircle className="text-red-500 w-5 h-5" />
                    )}
                  </td>
                  <td className="p-4">
                    {log.severity && (
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${getSeverityBadge(log.severity)}`}>
                        {log.severity}
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-gray-700">{log.root_cause || '-'}</td>
                  <td className="p-4 text-gray-700">{log.suggested_fix || '-'}</td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan="4" className="p-8 text-center text-gray-500">
                    No logs analyzed yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
      </div>
    </div>
  );
}

export default App;