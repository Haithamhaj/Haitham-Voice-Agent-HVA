import React, { useState, useEffect } from 'react';
import { History, RotateCcw, ChevronDown, ChevronUp, FileText, AlertCircle } from 'lucide-react';
import { api } from '../../services/api';

const CheckpointsWidget = () => {
    const [checkpoints, setCheckpoints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedId, setExpandedId] = useState(null);
    const [rollingBack, setRollingBack] = useState(null);

    const fetchCheckpoints = async () => {
        try {
            const data = await api.get('/checkpoints/');
            setCheckpoints(data);
        } catch (error) {
            console.error('Failed to fetch checkpoints:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCheckpoints();
        // Poll every 30 seconds
        const interval = setInterval(fetchCheckpoints, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleRollback = async (id) => {
        if (!confirm('Are you sure you want to rollback this operation? This cannot be undone.')) return;

        setRollingBack(id);
        try {
            const result = await api.post(`/checkpoints/${id}/rollback`);
            alert(`Rollback Complete!\nSuccess: ${result.success}\nFailed: ${result.failed}`);
            fetchCheckpoints(); // Refresh list
        } catch (error) {
            alert('Rollback failed: ' + error.message);
        } finally {
            setRollingBack(null);
        }
    };

    const toggleExpand = (id) => {
        setExpandedId(expandedId === id ? null : id);
    };

    const formatDate = (isoString) => {
        return new Date(isoString).toLocaleString('en-US', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    };

    if (loading) return <div className="animate-pulse h-32 bg-hva-card rounded-2xl"></div>;

    return (
        <div className="bg-hva-card rounded-2xl border border-hva-border p-6 h-full flex flex-col shadow-lg shadow-black/20">
            <div className="flex items-center justify-between mb-6 shrink-0">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-hva-accent/10 flex items-center justify-center text-hva-accent border border-hva-accent/20">
                        <History size={22} />
                    </div>
                    <div>
                        <h3 className="text-hva-cream font-semibold text-lg">System History</h3>
                        <p className="text-xs text-hva-muted">Track all system operations and changes</p>
                    </div>
                </div>
                <span className="text-xs text-hva-muted bg-hva-bg px-3 py-1.5 rounded-lg border border-hva-border-subtle font-mono">
                    Last {checkpoints.length} Actions
                </span>
            </div>

            <div className="space-y-4 overflow-y-auto pr-2 custom-scrollbar flex-1 min-h-[300px]">
                {checkpoints.length === 0 ? (
                    <div className="text-center text-hva-muted py-4 text-sm">No history available</div>
                ) : (
                    checkpoints.map((cp) => {
                        // Handle backward compatibility
                        const isLegacy = Array.isArray(cp.data);
                        const operations = isLegacy ? cp.data : (cp.data?.operations || []);
                        const meta = isLegacy ? {} : (cp.data?.meta || {});

                        return (
                            <div key={cp.id} className="bg-hva-bg/50 rounded-xl border border-hva-border-subtle overflow-hidden transition-all hover:border-hva-accent/30">
                                <div
                                    className="p-4 cursor-pointer hover:bg-white/5 transition-colors"
                                    onClick={() => toggleExpand(cp.id)}
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex items-start gap-3">
                                            <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${cp.action_type === 'deep_organize' ? 'bg-blue-500/20 text-blue-400' :
                                                cp.action_type === 'rollback' ? 'bg-orange-500/20 text-orange-400' :
                                                    'bg-hva-accent/20 text-hva-accent'
                                                }`}>
                                                {cp.action_type === 'rollback' ? <RotateCcw size={18} /> : <FileText size={18} />}
                                            </div>
                                            <div>
                                                <div className="text-sm text-hva-cream font-medium leading-tight mb-1">{cp.description}</div>
                                                <div className="text-xs text-hva-muted flex items-center gap-2">
                                                    <span>{formatDate(cp.timestamp)}</span>
                                                    {meta.model && (
                                                        <>
                                                            <span className="w-1 h-1 rounded-full bg-hva-border"></span>
                                                            <span className="text-hva-accent/80">{meta.model}</span>
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                        {expandedId === cp.id ? <ChevronUp size={16} className="text-hva-muted mt-1" /> : <ChevronDown size={16} className="text-hva-muted mt-1" />}
                                    </div>

                                    {/* Badges Row */}
                                    {!isLegacy && (meta.cost !== undefined || meta.tokens !== undefined) && (
                                        <div className="flex items-center gap-2 mt-3 ml-12">
                                            {meta.cost !== undefined && (
                                                <span className="text-[10px] bg-green-500/10 text-green-400 px-2 py-0.5 rounded border border-green-500/20 font-mono">
                                                    ${meta.cost.toFixed(4)}
                                                </span>
                                            )}
                                            {meta.tokens !== undefined && (
                                                <span className="text-[10px] bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded border border-purple-500/20 font-mono">
                                                    {meta.tokens} toks
                                                </span>
                                            )}
                                        </div>
                                    )}
                                </div>

                                {expandedId === cp.id && (
                                    <div className="px-4 pb-4 pt-0 border-t border-hva-border-subtle/50 bg-black/20">
                                        <div className="mt-3 space-y-2">
                                            <div className="text-xs text-hva-muted font-mono bg-black/40 p-2 rounded border border-white/5 max-h-40 overflow-y-auto">
                                                {operations.length > 0 ? (
                                                    operations.map((op, idx) => (
                                                        <div key={idx} className="mb-2 last:mb-0 break-all bg-black/20 p-2 rounded border border-white/5">
                                                            <div className="flex items-center justify-between mb-1">
                                                                <span className="text-[10px] text-hva-muted font-sans bg-white/5 px-1.5 rounded">
                                                                    {op.category || 'General'}
                                                                </span>
                                                            </div>
                                                            <div className="mb-1">
                                                                <span className="text-red-400/80 text-[10px]">FROM:</span> <span className="text-hva-cream/80">{op.src.split('/').pop()}</span>
                                                            </div>
                                                            <div className="mb-1">
                                                                <span className="text-green-400/80 text-[10px]">TO:</span> <span className="text-hva-cream/80">{op.dst.split('/').pop()}</span>
                                                            </div>
                                                            {op.reason && (
                                                                <div className="text-[10px] text-hva-accent/80 mt-1 border-l-2 border-hva-accent/30 pl-2 italic font-sans">
                                                                    "{op.reason}"
                                                                </div>
                                                            )}
                                                        </div>
                                                    ))
                                                ) : (
                                                    <div className="italic opacity-50">No details available</div>
                                                )}
                                            </div>

                                            {cp.action_type !== 'rollback' && (
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleRollback(cp.id);
                                                    }}
                                                    disabled={rollingBack === cp.id}
                                                    className="w-full mt-2 flex items-center justify-center gap-2 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs rounded-lg transition-colors border border-red-500/20 font-medium"
                                                >
                                                    {rollingBack === cp.id ? (
                                                        <span className="animate-spin">⌛</span>
                                                    ) : (
                                                        <RotateCcw size={14} />
                                                    )}
                                                    {rollingBack === cp.id ? 'Rolling back...' : 'Undo this Action'}
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
};

export default CheckpointsWidget;
