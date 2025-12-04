
import { networkMonitor } from '../developer-toolkit/networkMonitor';

const API_BASE_URL = 'http://127.0.0.1:8765';

const monitoredFetch = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const method = options.method || 'GET';
    const requestId = networkMonitor.logRequest(url, method, options.body ? JSON.parse(options.body) : null);

    try {
        const response = await fetch(url, options);
        const data = await response.json();
        networkMonitor.logResponse(requestId, response.status, data);
        return data;
    } catch (error) {
        networkMonitor.logError(requestId, error);
        throw error;
    }
};

export const api = {
    // Voice
    startVoice: () => monitoredFetch('/voice/start', { method: 'POST' }),
    stopVoice: () => monitoredFetch('/voice/stop', { method: 'POST' }),

    // Tasks
    fetchTasks: () => monitoredFetch('/tasks/'),

    // Gmail
    fetchEmails: () => monitoredFetch('/gmail/unread'),

    // Calendar
    fetchEvents: () => monitoredFetch('/calendar/today'),

    // Memory
    fetchMemoryStats: () => monitoredFetch('/memory/stats'),
    searchMemory: (query) => monitoredFetch(`/memory/search?query=${encodeURIComponent(query)}`),

    // Chat
    sendChat: (message, command = null, params = null) => monitoredFetch('/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, command, params })
    }),

    // System
    fetchSystemLogs: () => monitoredFetch('/system/logs'),
    saveDebugReport: (report) => monitoredFetch('/system/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(report)
    }),

    // Files
    openFile: async (path) => {
        const response = await fetch(`${API_BASE_URL}/files/open`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path })
        });
        if (!response.ok) throw new Error('Failed to open file');
        return response.json();
    },

    // Usage
    fetchUsageStats: async (days = 30) => {
        const response = await fetch(`${API_BASE_URL}/usage/stats?days=${days}`);
        if (!response.ok) throw new Error('Failed to fetch usage stats');
        return response.json();
    },

    fetchUsageLogs: async (limit = 50) => {
        const response = await fetch(`${API_BASE_URL}/usage/logs?limit=${limit}`);
        if (!response.ok) throw new Error('Failed to fetch usage logs');
        return response.json();
    }
};

