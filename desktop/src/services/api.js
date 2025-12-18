import { networkMonitor } from '../developer-toolkit/networkMonitor';

const API_BASE_URL = import.meta.env.DEV ? 'http://127.0.0.1:8765' : '';

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
    // Generic
    get: (endpoint) => monitoredFetch(endpoint),
    post: (endpoint, body) => monitoredFetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    }),

    // Voice
    startVoice: () => monitoredFetch('/voice/start', { method: 'POST' }),
    stopVoice: () => monitoredFetch('/voice/stop', { method: 'POST' }),

    // Tasks
    // Tasks
    fetchTasks: () => monitoredFetch('/tasks/'),
    deleteTask: (id) => monitoredFetch(`/tasks/${id}`, { method: 'DELETE' }),
    updateTask: (id, updates) => monitoredFetch(`/tasks/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
    }),

    // Gmail
    fetchEmails: () => monitoredFetch('/gmail/unread'),
    summarizeEmail: (id) => monitoredFetch(`/gmail/summarize/${id}`, { method: 'POST' }),
    convertEmailToTask: (id) => monitoredFetch(`/gmail/task/${id}`, { method: 'POST' }),

    // Calendar
    // Calendar
    fetchEvents: () => monitoredFetch('/calendar/today'),
    deleteEvent: (id) => monitoredFetch(`/calendar/events/${id}`, { method: 'DELETE' }),

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
    },

    // File System Tree
    getFileTree: async (path = "~", depth = 2) => {
        const response = await fetch(`${API_BASE_URL}/files/tree?path=${encodeURIComponent(path)}&depth=${depth}`);
        if (!response.ok) throw new Error('Failed to fetch file tree');
        return response.json();
    },

    // Fine-Tuning Lab
    finetuneStatus: () => monitoredFetch('/finetune/status'),
    finetunePreview: (limit = 20) => monitoredFetch(`/finetune/dataset/preview?limit=${limit}`),
    finetuneCompare: (prompt) => monitoredFetch('/finetune/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
    }),
    finetuneStyleCompare: (prompt) => monitoredFetch('/finetune/style-compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
    }),
    finetuneExperimentChat: (messages) => monitoredFetch('/finetune/experiment/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages })
    }),
    finetuneExperimentChat: (messages, mode = "haithm_v2") => monitoredFetch('/finetune/experiment/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages, mode })
    }),
    finetuneSaveExperiment: (messages, mode = "haithm_v2") => monitoredFetch('/finetune/experiment/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages, mode })
    }),
    finetuneChat: (model_provider, messages) => monitoredFetch('/finetune/tutor-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_provider, messages })
    })
};

