import React, { useState, useEffect } from 'react';
import { DollarSign, Cpu, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../../services/api';

import UsageDetailsModal from './UsageDetailsModal';

const UsageWidget = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

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
        // Refresh every 5 seconds (Real-time tracking)
        const interval = setInterval(fetchStats, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="animate-pulse bg-hva-card h-40 rounded-2xl"></div>;
    if (!stats || typeof stats.total_cost === 'undefined') return null;

    return (
        <>
            <div
                onClick={() => setShowModal(true)}
                className="bg-hva-card p-6 rounded-2xl border border-hva-border-subtle hover:border-hva-accent/30 transition-colors group cursor-pointer"
            >
                <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                        <DollarSign size={20} />
                    </div>
                    <div className="text-right">
                        <span className="text-2xl font-bold text-hva-cream">${(stats.total_cost || 0).toFixed(4)}</span>
                        <div className="text-xs text-hva-muted">Total Cost (30d)</div>
                        {/* Cost Breakdown */}
                        <div className="flex items-center justify-end gap-2 mt-1 text-[10px]">
                            <span className="text-blue-400">Gemini: ${(stats.by_model?.filter(m => m.model.includes('gemini')).reduce((acc, curr) => acc + curr.cost, 0) || 0).toFixed(4)}</span>
                            <span className="text-hva-dim">|</span>
                            <span className="text-green-400">GPT: ${(stats.by_model?.filter(m => m.model.includes('gpt')).reduce((acc, curr) => acc + curr.cost, 0) || 0).toFixed(4)}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 text-hva-muted">
                        <Cpu size={16} />
                        <span className="text-sm">Tokens</span>
                    </div>
                    <span className="text-hva-cream font-medium">{((stats.total_tokens || 0) / 1000).toFixed(1)}k</span>
                </div>

                <div className="mt-4 flex items-center justify-center gap-1 text-xs text-hva-dim group-hover:text-hva-accent transition-colors">
                    View Analytics & Logs
                    <ChevronDown size={12} className="-rotate-90" />
                </div>
            </div>

            {showModal && <UsageDetailsModal onClose={() => setShowModal(false)} />}
        </>
    );
};

export default UsageWidget;
