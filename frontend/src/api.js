import axios from 'axios';

// In your api.js file
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// --- SESSION MANAGEMENT ---
// Check if they already have an ID, if not, generate a new random one
let sessionId = localStorage.getItem('logsleuth_session_id');
if (!sessionId) {
    sessionId = crypto.randomUUID(); 
    localStorage.setItem('logsleuth_session_id', sessionId);
}

// Attach the session ID to the headers
const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'X-Session-ID': sessionId
    }
});

export const logApi = {
    getLogs: async () => {
        const response = await axiosInstance.get('/logs');
        return response.data;
    },
    submitLog: async (rawLog) => {
        const response = await axiosInstance.post('/logs', {
            raw_log: rawLog
        });
        return response.data;
    }
};
