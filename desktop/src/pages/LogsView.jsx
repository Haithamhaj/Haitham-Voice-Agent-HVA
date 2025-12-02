import React, { useState, useEffect } from 'react';
import { Terminal, Server, RefreshCw, Trash2, AlertCircle, Info, AlertTriangle, X, Stethoscope, Activity } from 'lucide-react';
import { logger, useLogs } from '../services/logger';
import { api } from '../services/api';
import { diagnoseError } from '../services/diagnostics';

const LogsView = () => {
    const [activeTab, setActiveTab] = useState('frontend');
    const frontendLogs = useLogs();
    const [backendLogs, setBackendLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedLog, setSelectedLog] = useState(null);
    const [diagnosis, setDiagnosis] = useState(null);

    const fetchBackendLogs = async () => {
        setLoading(true);
        try {
            const logs = await api.fetchSystemLogs();
            setBackendLogs(logs);
        } catch (error) {
            console.error("Failed to fetch backend logs", error);
            logger.error("Failed to fetch backend logs", error.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab === 'backend') {
            fetchBackendLogs();
        }
    }, [activeTab]);

    const handleLogClick = (log) => {
        if (log.level === 'ERROR' || log.level === 'WARN') {
            const diag = diagnoseError(log);
            setSelectedLog(log);
            setDiagnosis(diag);
        }
    };

    const closeDiagnosis = () => {
        setSelectedLog(null);
        setDiagnosis(null);
    };

    const getLevelColor = (level) => {
        switch (level) {
            case 'ERROR': return 'text-red-500';
            case 'WARN': return 'text-yellow-500';
            case 'INFO': return 'text-blue-400';
            default: return 'text-hva-muted';
        }
    };

    const getLevelIcon = (level) => {
        switch (level) {
            case 'ERROR': return <AlertCircle size={16} />;
            case 'WARN': return <AlertTriangle size={16} />;
            case 'INFO': return <Info size={16} />;
            default: return <Info size={16} />;
        }
    };

    return (
        <div className="flex flex-col h-full space-y-4 relative">
            <header className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-hva-cream flex items-center gap-3">
                    <Terminal className="text-hva-accent" size={32} />
                    سجلات النظام
                </h1>
                <div className="flex bg-hva-card rounded-lg p-1 border border-hva-border-subtle">
                    <button
                        onClick={() => setActiveTab('frontend')}
                        className={`px-4 py-2 rounded-md transition-colors flex items-center gap-2 ${activeTab === 'frontend' ? 'bg-hva-accent text-hva-primary font-bold' : 'text-hva-muted hover:text-hva-cream'}`}
                    >
                        <Terminal size={16} />
                        الواجهة
                    </button>
                    <button
                        onClick={() => setActiveTab('backend')}
                        className={`px-4 py-2 rounded-md transition-colors flex items-center gap-2 ${activeTab === 'backend' ? 'bg-hva-accent text-hva-primary font-bold' : 'text-hva-muted hover:text-hva-cream'}`}
                    >
                        <Server size={16} />
                        الخادم
                    </button>
                </div>
            </header>

            <div className="flex-1 bg-hva-card rounded-2xl border border-hva-border-subtle overflow-hidden flex flex-col">
                <div className="p-4 border-b border-hva-border-subtle flex justify-between items-center bg-hva-primary/30">
                    <div className="flex gap-2">
                        <span className="text-sm text-hva-muted">
                            {activeTab === 'frontend' ? `${frontendLogs.length} سجل` : 'آخر 100 سطر'}
                        </span>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={activeTab === 'frontend' ? () => logger.clear() : fetchBackendLogs}
                            className="p-2 hover:bg-hva-primary rounded-lg text-hva-muted hover:text-hva-cream transition-colors"
                            title={activeTab === 'frontend' ? "مسح السجلات" : "تحديث"}
                        >
                            {activeTab === 'frontend' ? <Trash2 size={18} /> : <RefreshCw size={18} className={loading ? "animate-spin" : ""} />}
                        </button>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-2">
                    {activeTab === 'frontend' ? (
                        frontendLogs.length === 0 ? (
                            <div className="text-center text-hva-muted py-10">لا توجد سجلات حالياً</div>
                        ) : (
                            frontendLogs.map(log => (
                                <div
                                    key={log.id}
                                    onClick={() => handleLogClick(log)}
                                    className={`flex gap-3 p-2 rounded transition-colors ${log.level === 'ERROR' || log.level === 'WARN' ? 'hover:bg-hva-primary/40 cursor-pointer' : 'hover:bg-hva-primary/20'}`}
                                >
                                    <span className="text-hva-muted shrink-0 w-24 text-xs">{log.timestamp.split('T')[1].split('.')[0]}</span>
                                    <span className={`shrink-0 w-16 font-bold flex items-center gap-1 ${getLevelColor(log.level)}`}>
                                        {getLevelIcon(log.level)}
                                        {log.level}
                                    </span>
                                    <span className="text-hva-cream break-all">{log.message}</span>
                                    {log.details && <span className="text-hva-muted text-xs italic">{JSON.stringify(log.details)}</span>}
                                </div>
                            ))
                        )
                    ) : (
                        <div className="whitespace-pre-wrap text-hva-cream/80 leading-relaxed">
                            {backendLogs.length > 0 ? backendLogs.join('\n') : "جاري التحميل..."}
                        </div>
                    )}
                </div>
            </div>

            {/* Diagnosis Modal */}
            {selectedLog && diagnosis && (
                <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
                    <div className="bg-hva-card border border-hva-border w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90%]">
                        <div className="p-6 border-b border-hva-border flex justify-between items-start bg-hva-primary/50">
                            <div className="flex items-center gap-3">
                                <div className="p-3 rounded-full bg-red-500/20 text-red-500">
                                    <Stethoscope size={24} />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-white">تشخيص الخطأ</h3>
                                    <p className="text-hva-muted text-sm mt-1 font-mono">{selectedLog.message}</p>
                                </div>
                            </div>
                            <button onClick={closeDiagnosis} className="text-hva-muted hover:text-white transition-colors">
                                <X size={24} />
                            </button>
                        </div>

                        <div className="p-6 overflow-y-auto space-y-6">
                            <div className="space-y-2">
                                <h4 className="text-hva-accent font-bold flex items-center gap-2">
                                    <Activity size={18} />
                                    المشكلة
                                </h4>
                                <p className="text-white text-lg">{diagnosis.title}</p>
                                <p className="text-hva-cream/80">{diagnosis.explanation}</p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="bg-hva-primary/30 p-4 rounded-xl border border-hva-border-subtle">
                                    <h4 className="text-yellow-500 font-bold mb-2">السبب المحتمل</h4>
                                    <p className="text-sm text-hva-cream/80">{diagnosis.cause}</p>
                                </div>
                                <div className="bg-hva-primary/30 p-4 rounded-xl border border-hva-border-subtle">
                                    <h4 className="text-red-400 font-bold mb-2">التأثير</h4>
                                    <p className="text-sm text-hva-cream/80">{diagnosis.impact}</p>
                                </div>
                            </div>

                            <div className="space-y-3">
                                <h4 className="text-green-400 font-bold">خطوات الحل المقترحة</h4>
                                <ul className="space-y-2">
                                    {diagnosis.steps.map((step, index) => (
                                        <li key={index} className="flex items-start gap-3 bg-hva-primary/20 p-3 rounded-lg">
                                            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-green-500/20 text-green-400 text-xs font-bold shrink-0">
                                                {index + 1}
                                            </span>
                                            <span className="text-hva-cream/90 text-sm">{step}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        <div className="p-4 border-t border-hva-border bg-hva-primary/30 flex justify-end">
                            <button
                                onClick={closeDiagnosis}
                                className="px-6 py-2 bg-hva-accent text-hva-primary font-bold rounded-lg hover:bg-hva-accent/90 transition-colors"
                            >
                                حسناً، فهمت
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LogsView;
