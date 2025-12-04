import React, { useState, useEffect } from 'react';
import { DollarSign, Cpu, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../../services/api';

const UsageWidget = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState(false);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await api.fetchUsageStats(30);
                setStats(data);
            } catch (error) {
                console.error("Failed to fetch usage stats", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
        // Refresh every minute
        const interval = setInterval(fetchStats, 60000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="animate-pulse bg-hva-card h-40 rounded-2xl"></div>;
    if (!stats) return null;

    return (
        <div className="bg-hva-card p-6 rounded-2xl border border-hva-border-subtle hover:border-hva-accent/30 transition-colors group">
            <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                    <DollarSign size={20} />
                </div>
                <div className="text-right">
                    <span className="text-2xl font-bold text-hva-cream">${stats.total_cost.toFixed(4)}</span>
                    <div className="text-xs text-hva-muted">Total Cost (30d)</div>
                </div>
            </div>

            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-hva-muted">
                    <Cpu size={16} />
                    <span className="text-sm">Tokens</span>
                </div>
                <span className="text-hva-cream font-medium">{(stats.total_tokens / 1000).toFixed(1)}k</span>
            </div>

            {/* Breakdown Toggle */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full mt-2 flex items-center justify-center gap-1 text-xs text-hva-dim hover:text-hva-accent transition-colors"
            >
                {expanded ? 'Hide Details' : 'Show Details'}
                {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>

            {/* Expanded Details */}
            {expanded && (
                <div className="mt-3 space-y-2 border-t border-hva-border-subtle pt-2">
                    {stats.by_model.map((model, idx) => (
                        <div key={idx} className="flex justify-between text-xs">
                            <span className="text-hva-muted truncate w-24" title={model.model}>{model.model}</span>
                            <div className="flex gap-3">
                                <span className="text-hva-dim">{(model.tokens / 1000).toFixed(1)}k</span>
                                <span className="text-hva-cream">${model.cost.toFixed(4)}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default UsageWidget;
