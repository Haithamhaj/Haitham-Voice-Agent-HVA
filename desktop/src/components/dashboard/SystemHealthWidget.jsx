import React, { useState, useEffect } from 'react';
import { Activity, Cpu, HardDrive, Battery, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';

const SystemHealthWidget = () => {
    const [health, setHealth] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [cleaning, setCleaning] = useState(false);

    const fetchHealth = async () => {
        try {
            const data = await api.get('/system/health');
            setHealth(data);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch health:", err);
            setError("Failed to load system health");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHealth();
        const interval = setInterval(fetchHealth, 5000); // Refresh every 5s
        return () => clearInterval(interval);
    }, []);

    const handleCleanCache = async () => {
        if (!confirm("Are you sure you want to clean system cache?")) return;

        setCleaning(true);
        try {
            // We use the chat endpoint to trigger the tool via the agent for now, 
            // or we could add a direct endpoint. Let's use the agent to keep it consistent.
            // Actually, for a dashboard button, a direct call is better if we exposed it.
            // But we didn't expose clean_cache directly yet.
            // Let's use the chat API to simulate the command "Clean Cache"
            await api.post('/chat/send', { message: "Clean Cache" });
            alert("Cleanup started! Check the chat for details.");
        } catch (err) {
            alert("Failed to start cleanup");
        } finally {
            setCleaning(false);
        }
    };

    if (loading) return <div className="animate-pulse h-48 bg-gray-800/50 rounded-xl"></div>;
    if (error) return <div className="text-red-400 p-4 border border-red-500/30 rounded-xl bg-red-500/10">{error}</div>;
    if (!health) return null;

    const getStatusColor = (status) => {
        if (status === "Healthy") return "text-green-400 bg-green-400/10 border-green-400/20";
        if (status === "Strained") return "text-yellow-400 bg-yellow-400/10 border-yellow-400/20";
        return "text-red-400 bg-red-400/10 border-red-400/20";
    };

    // Parse percentages
    const cpuVal = parseInt(health.cpu.usage);
    const ramVal = parseInt(health.memory.usage);

    return (
        <div className="bg-gray-800/50 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${getStatusColor(health.status)}`}>
                        <Activity className="w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white">System Health</h2>
                        <div className={`text-sm px-2 py-0.5 rounded-full inline-block mt-1 border ${getStatusColor(health.status)}`}>
                            {health.status}
                        </div>
                    </div>
                </div>
                <button onClick={fetchHealth} className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                    <RefreshCw className="w-5 h-5 text-gray-400" />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* CPU */}
                <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-400">
                        <span className="flex items-center gap-2"><Cpu className="w-4 h-4" /> CPU</span>
                        <span>{health.cpu.usage}</span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${cpuVal > 80 ? 'bg-red-500' : 'bg-blue-500'}`}
                            style={{ width: health.cpu.usage }}
                        />
                    </div>
                    <p className="text-xs text-gray-500">{health.cpu.cores} Cores Active</p>
                </div>

                {/* RAM */}
                <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-400">
                        <span className="flex items-center gap-2"><Activity className="w-4 h-4" /> RAM</span>
                        <span>{health.memory.usage}</span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${ramVal > 85 ? 'bg-yellow-500' : 'bg-purple-500'}`}
                            style={{ width: health.memory.usage }}
                        />
                    </div>
                    <p className="text-xs text-gray-500">{health.memory.details}</p>
                </div>

                {/* Disk */}
                <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-400">
                        <span className="flex items-center gap-2"><HardDrive className="w-4 h-4" /> Disk</span>
                        <span>{health.disk.usage}</span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                            style={{ width: health.disk.usage }}
                        />
                    </div>
                    <p className="text-xs text-gray-500">{health.disk.free} Free</p>
                </div>
            </div>

            {/* Recommendations */}
            {(cpuVal > 80 || ramVal > 85) && (
                <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-yellow-500" />
                        <div>
                            <p className="text-sm font-medium text-yellow-200">High Resource Usage Detected</p>
                            <p className="text-xs text-yellow-500/80">System is under heavy load.</p>
                        </div>
                    </div>
                    <button
                        onClick={handleCleanCache}
                        disabled={cleaning}
                        className="px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-200 text-sm rounded-lg transition-colors border border-yellow-500/30"
                    >
                        {cleaning ? "Cleaning..." : "Clean Cache"}
                    </button>
                </div>
            )}
        </div>
    );
};

export default SystemHealthWidget;
