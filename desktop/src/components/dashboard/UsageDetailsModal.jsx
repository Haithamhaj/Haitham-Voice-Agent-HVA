import React, { useState, useEffect } from 'react';
import { X, Calendar, Activity, DollarSign, FileText } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../../services/api';

const UsageDetailsModal = ({ onClose }) => {
    const [stats, setStats] = useState(null);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('chart'); // 'chart' or 'logs'

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsData, logsData] = await Promise.all([
                    api.fetchUsageStats(30),
                    api.fetchUsageLogs(50)
                ]);
                setStats(statsData);
                setLogs(logsData);
            } catch (error) {
                console.error("Failed to fetch usage details", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="bg-hva-card p-8 rounded-2xl border border-hva-border-subtle animate-pulse">
                    <div className="h-6 w-48 bg-hva-border-subtle rounded mb-4"></div>
                    <div className="h-64 w-96 bg-hva-border-subtle rounded"></div>
                </div>
            </div>
        );
    }

    // Prepare chart data
    const chartData = stats?.daily_stats?.map(day => ({
        date: day.date.slice(5), // MM-DD
        cost: day.cost,
        tokens: day.tokens
    })) || [];

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-hva-card w-full max-w-4xl max-h-[90vh] rounded-2xl border border-hva-border-subtle shadow-2xl flex flex-col">
                {/* Header */}
                <div className="p-6 border-b border-hva-border-subtle flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold text-hva-cream flex items-center gap-2">
                            <Activity className="text-purple-400" />
                            تفاصيل الاستهلاك
                        </h2>
                        <p className="text-hva-muted text-sm mt-1">تحليل التكلفة والعمليات لآخر 30 يوم</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                        <X size={24} className="text-hva-muted" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-hva-border-subtle">
                    <button
                        onClick={() => setActiveTab('chart')}
                        className={`flex-1 p-4 text-sm font-medium transition-colors ${activeTab === 'chart' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-hva-muted hover:text-hva-cream'}`}
                    >
                        الرسم البياني (Daily Cost)
                    </button>
                    <button
                        onClick={() => setActiveTab('logs')}
                        className={`flex-1 p-4 text-sm font-medium transition-colors ${activeTab === 'logs' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-hva-muted hover:text-hva-cream'}`}
                    >
                        سجل العمليات (Logs)
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {activeTab === 'chart' ? (
                        <div className="space-y-8">
                            {/* Summary Cards */}
                            <div className="grid grid-cols-3 gap-4">
                                <div className="bg-hva-bg p-4 rounded-xl border border-hva-border-subtle">
                                    <div className="text-hva-muted text-xs mb-1">Total Cost</div>
                                    <div className="text-2xl font-bold text-hva-cream">${stats?.total_cost?.toFixed(4)}</div>
                                </div>
                                <div className="bg-hva-bg p-4 rounded-xl border border-hva-border-subtle">
                                    <div className="text-hva-muted text-xs mb-1">Total Tokens</div>
                                    <div className="text-2xl font-bold text-hva-cream">{(stats?.total_tokens / 1000).toFixed(1)}k</div>
                                </div>
                                <div className="bg-hva-bg p-4 rounded-xl border border-hva-border-subtle">
                                    <div className="text-hva-muted text-xs mb-1">Requests</div>
                                    <div className="text-2xl font-bold text-hva-cream">{stats?.request_count}</div>
                                </div>
                            </div>

                            {/* Chart */}
                            <div className="h-80 w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                        <XAxis dataKey="date" stroke="#666" fontSize={12} />
                                        <YAxis stroke="#666" fontSize={12} tickFormatter={(val) => `$${val}`} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#1a1a1a', borderColor: '#333', borderRadius: '8px' }}
                                            itemStyle={{ color: '#fff' }}
                                            formatter={(value) => [`$${Number(value).toFixed(4)}`, 'Cost']}
                                        />
                                        <Bar dataKey="cost" fill="#a855f7" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="text-hva-muted text-xs border-b border-hva-border-subtle">
                                        <th className="p-3 font-medium">Time</th>
                                        <th className="p-3 font-medium">Model</th>
                                        <th className="p-3 font-medium">Context</th>
                                        <th className="p-3 font-medium text-right">Tokens</th>
                                        <th className="p-3 font-medium text-right">Cost</th>
                                    </tr>
                                </thead>
                                <tbody className="text-sm">
                                    {logs.map((log, idx) => (
                                        <tr key={idx} className="border-b border-hva-border-subtle/50 hover:bg-white/5 transition-colors">
                                            <td className="p-3 text-hva-dim whitespace-nowrap">
                                                {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                <div className="text-[10px] opacity-60">{new Date(log.timestamp).toLocaleDateString()}</div>
                                            </td>
                                            <td className="p-3 text-hva-cream">
                                                <span className={`px-2 py-1 rounded text-xs ${log.model.includes('gpt') ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'}`}>
                                                    {log.model}
                                                </span>
                                            </td>
                                            <td className="p-3 text-hva-dim max-w-xs truncate">
                                                {log.context?.intent || log.context?.method || '-'}
                                                {log.context?.action && <span className="ml-2 text-xs opacity-60">({log.context.action})</span>}
                                            </td>
                                            <td className="p-3 text-right text-hva-dim font-mono">
                                                {log.total_tokens}
                                            </td>
                                            <td className="p-3 text-right text-hva-cream font-mono">
                                                ${log.cost.toFixed(5)}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default UsageDetailsModal;
