import React, { useState, useEffect } from 'react';
import { Terminal, Server, RefreshCw, Trash2, AlertCircle, Info, AlertTriangle, X, Stethoscope, Activity, Network, Database, Download, Send } from 'lucide-react';
import { logger, useLogs } from '../services/logger';
import { api } from '../services/api';
import { diagnoseError } from '../services/diagnostics';
import { useNetworkMonitor, networkMonitor } from '../services/networkMonitor';
import { useWebSocket } from '../hooks/useWebSocket';

const LogsView = () => {
    const [activeTab, setActiveTab] = useState('frontend');
    const frontendLogs = useLogs();
    const networkRequests = useNetworkMonitor();
    const [backendLogs, setBackendLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedLog, setSelectedLog] = useState(null);
    const [diagnosis, setDiagnosis] = useState(null);
    const [selectedRequest, setSelectedRequest] = useState(null);

    // State Inspector Data
    const { isListening, wsConnected } = useWebSocket();
    const [memoryStats, setMemoryStats] = useState(null);

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

    const fetchStateData = async () => {
        try {
            const stats = await api.fetchMemoryStats();
            setMemoryStats(stats);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        if (activeTab === 'backend') {
            fetchBackendLogs();
        }
        if (activeTab === 'state') {
            fetchStateData();
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

    const generateReport = () => {
        return {
            timestamp: new Date().toISOString(),
            system: {
                userAgent: navigator.userAgent,
                platform: navigator.platform
            },
            state: {
                wsConnected,
                isListening,
                memoryStats
            },
            logs: {
                frontend: frontendLogs,
                backend: backendLogs
            },
            network: networkRequests
        };
    };

    const exportReport = () => {
        const report = generateReport();
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `hva-debug-report-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const saveReportToAI = async () => {
        try {
            const report = generateReport();
            await api.saveDebugReport(report);
            // Show success toast (using logger for now as we don't have direct toast access here, but logger triggers toast)
            logger.info("تم حفظ التقرير بنجاح! أخبر هيثم لفحصه الآن.");
        } catch (error) {
            console.error("Failed to save report", error);
            logger.error("فشل حفظ التقرير", error.message);
        }
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
                    أدوات المطور
                </h1>
                <div className="flex gap-2">
                    <button
                        onClick={exportReport}
                        className="px-4 py-2 bg-hva-primary/50 hover:bg-hva-primary text-hva-cream rounded-lg border border-hva-border flex items-center gap-2 transition-colors"
                    >
                        <Download size={18} />
                        تصدير تقرير
                    </button>
                    <button
                        onClick={saveReportToAI}
                        className="px-4 py-2 bg-hva-accent hover:bg-hva-accent/90 text-hva-primary font-bold rounded-lg border border-hva-accent flex items-center gap-2 transition-colors"
                    >
                        <Send size={18} />
                        حفظ للتحليل (AI)
                    </button>
                    <div className="flex bg-hva-card rounded-lg p-1 border border-hva-border-subtle">
                        <button onClick={() => setActiveTab('frontend')} className={`px-3 py-2 rounded-md transition-colors flex items-center gap-2 ${activeTab === 'frontend' ? 'bg-hva-accent text-hva-primary font-bold' : 'text-hva-muted hover:text-hva-cream'}`}>
                            <Terminal size={16} /> الواجهة
                        </button>
                        <button onClick={() => setActiveTab('backend')} className={`px-3 py-2 rounded-md transition-colors flex items-center gap-2 ${activeTab === 'backend' ? 'bg-hva-accent text-hva-primary font-bold' : 'text-hva-muted hover:text-hva-cream'}`}>
                            <Server size={16} /> الخادم
                        </button>
                        <button onClick={() => setActiveTab('network')} className={`px-3 py-2 rounded-md transition-colors flex items-center gap-2 ${activeTab === 'network' ? 'bg-hva-accent text-hva-primary font-bold' : 'text-hva-muted hover:text-hva-cream'}`}>
                            <Network size={16} /> الشبكة
                        </button>
                        <button onClick={() => setActiveTab('state')} className={`px-3 py-2 rounded-md transition-colors flex items-center gap-2 ${activeTab === 'state' ? 'bg-hva-accent text-hva-primary font-bold' : 'text-hva-muted hover:text-hva-cream'}`}>
                            <Database size={16} /> الحالة
                        </button>
                    </div>
                </div>
            </header>

            <div className="flex-1 bg-hva-card rounded-2xl border border-hva-border-subtle overflow-hidden flex flex-col">
                {/* Toolbar */}
                <div className="p-4 border-b border-hva-border-subtle flex justify-between items-center bg-hva-primary/30">
                    <div className="flex gap-2">
                        <span className="text-sm text-hva-muted">
                            {activeTab === 'frontend' ? `${frontendLogs.length} سجل` :
                                activeTab === 'network' ? `${networkRequests.length} طلب` :
                                    activeTab === 'backend' ? 'آخر 100 سطر' : 'بيانات حية'}
                        </span>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => {
                                if (activeTab === 'frontend') logger.clear();
                                if (activeTab === 'network') networkMonitor.clear();
                                if (activeTab === 'backend') fetchBackendLogs();
                                if (activeTab === 'state') fetchStateData();
                            }}
                            className="p-2 hover:bg-hva-primary rounded-lg text-hva-muted hover:text-hva-cream transition-colors"
                        >
                            {activeTab === 'backend' || activeTab === 'state' ? <RefreshCw size={18} className={loading ? "animate-spin" : ""} /> : <Trash2 size={18} />}
                        </button>
                    </div>
                </div>

                {/* Content Area */}
                <div className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-2">

                    {/* Frontend Logs */}
                    {activeTab === 'frontend' && (
                        frontendLogs.length === 0 ? <div className="text-center text-hva-muted py-10">لا توجد سجلات</div> :
                            frontendLogs.map(log => (
                                <div key={log.id} onClick={() => handleLogClick(log)} className={`flex gap-3 p-2 rounded transition-colors ${log.level === 'ERROR' || log.level === 'WARN' ? 'hover:bg-hva-primary/40 cursor-pointer' : 'hover:bg-hva-primary/20'}`}>
                                    <span className="text-hva-muted shrink-0 w-24 text-xs">{log.timestamp.split('T')[1].split('.')[0]}</span>
                                    <span className={`shrink-0 w-16 font-bold flex items-center gap-1 ${getLevelColor(log.level)}`}>{getLevelIcon(log.level)}{log.level}</span>
                                    <span className="text-hva-cream break-all">{log.message}</span>
                                </div>
                            ))
                    )}

                    {/* Backend Logs */}
                    {activeTab === 'backend' && (
                        <div className="whitespace-pre-wrap text-hva-cream/80 leading-relaxed dir-ltr text-left">
                            {backendLogs.length > 0 ? backendLogs.join('\n') : "جاري التحميل..."}
                        </div>
                    )}

                    {/* Network Monitor */}
                    {activeTab === 'network' && (
                        networkRequests.length === 0 ? <div className="text-center text-hva-muted py-10">لا توجد طلبات شبكة</div> :
                            <div className="space-y-2">
                                {networkRequests.map(req => (
                                    <div key={req.id} onClick={() => setSelectedRequest(req)} className="flex items-center gap-4 p-3 bg-hva-primary/20 hover:bg-hva-primary/40 rounded-lg cursor-pointer border border-transparent hover:border-hva-border-subtle transition-all">
                                        <span className={`px-2 py-1 rounded text-xs font-bold w-16 text-center ${req.method === 'GET' ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'}`}>{req.method}</span>
                                        <span className="flex-1 text-hva-cream truncate dir-ltr text-left">{req.url.replace('http://127.0.0.1:8765', '')}</span>
                                        <span className={`text-xs font-bold ${req.status === 'error' ? 'text-red-500' : req.status >= 400 ? 'text-red-400' : 'text-green-400'}`}>{req.status}</span>
                                        <span className="text-hva-muted text-xs w-16 text-right">{req.duration ? `${req.duration}ms` : '...'}</span>
                                    </div>
                                ))}
                            </div>
                    )}

                    {/* State Inspector */}
                    {activeTab === 'state' && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-hva-primary/20 p-4 rounded-xl border border-hva-border-subtle">
                                <h3 className="text-hva-accent font-bold mb-4 flex items-center gap-2"><Network size={18} /> WebSocket Status</h3>
                                <div className="space-y-2 text-hva-cream/90">
                                    <div className="flex justify-between"><span className="text-hva-muted">Connected:</span> <span className={wsConnected ? "text-green-400" : "text-red-400"}>{wsConnected ? "Yes" : "No"}</span></div>
                                    <div className="flex justify-between"><span className="text-hva-muted">Listening:</span> <span className={isListening ? "text-green-400" : "text-hva-muted"}>{isListening ? "Active" : "Idle"}</span></div>
                                </div>
                            </div>

                            <div className="bg-hva-primary/20 p-4 rounded-xl border border-hva-border-subtle">
                                <h3 className="text-hva-accent font-bold mb-4 flex items-center gap-2"><Database size={18} /> Memory Stats</h3>
                                {memoryStats ? (
                                    <div className="space-y-2 text-hva-cream/90">
                                        <div className="flex justify-between"><span className="text-hva-muted">Total Memories:</span> <span>{memoryStats.total_memories}</span></div>
                                        <div className="flex justify-between"><span className="text-hva-muted">Collections:</span> <span>{memoryStats.collections?.length || 0}</span></div>
                                    </div>
                                ) : <p className="text-hva-muted">Loading...</p>}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Diagnosis Modal (Existing) */}
            {selectedLog && diagnosis && (
                <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
                    <div className="bg-hva-card border border-hva-border w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90%]">
                        <div className="p-6 border-b border-hva-border flex justify-between items-start bg-hva-primary/50">
                            <div className="flex items-center gap-3">
                                <div className="p-3 rounded-full bg-red-500/20 text-red-500"><Stethoscope size={24} /></div>
                                <div>
                                    <h3 className="text-xl font-bold text-white">تشخيص الخطأ</h3>
                                    <p className="text-hva-muted text-sm mt-1 font-mono">{selectedLog.message}</p>
                                </div>
                            </div>
                            <button onClick={closeDiagnosis} className="text-hva-muted hover:text-white transition-colors"><X size={24} /></button>
                        </div>
                        <div className="p-6 overflow-y-auto space-y-6">
                            <div className="space-y-2">
                                <h4 className="text-hva-accent font-bold flex items-center gap-2"><Activity size={18} /> المشكلة</h4>
                                <p className="text-white text-lg">{diagnosis.title}</p>
                                <p className="text-hva-cream/80">{diagnosis.explanation}</p>
                            </div>
                            {diagnosis.location && (
                                <div className="bg-hva-primary/40 p-4 rounded-xl border border-hva-accent/20">
                                    <h4 className="text-hva-accent font-bold mb-2 flex items-center gap-2"><Terminal size={16} /> موقع الخطأ (Technical Location)</h4>
                                    <div className="font-mono text-sm text-hva-cream/90 dir-ltr text-left space-y-1">
                                        <p><span className="text-hva-muted">File:</span> {diagnosis.location.file}</p>
                                        <p><span className="text-hva-muted">Line:</span> {diagnosis.location.line}</p>
                                        {diagnosis.location.function && <p><span className="text-hva-muted">Function:</span> {diagnosis.location.function}</p>}
                                    </div>
                                </div>
                            )}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="bg-hva-primary/30 p-4 rounded-xl border border-hva-border-subtle"><h4 className="text-yellow-500 font-bold mb-2">السبب المحتمل</h4><p className="text-sm text-hva-cream/80">{diagnosis.cause}</p></div>
                                <div className="bg-hva-primary/30 p-4 rounded-xl border border-hva-border-subtle"><h4 className="text-red-400 font-bold mb-2">التأثير</h4><p className="text-sm text-hva-cream/80">{diagnosis.impact}</p></div>
                            </div>
                            <div className="space-y-3">
                                <h4 className="text-green-400 font-bold">خطوات الحل المقترحة</h4>
                                <ul className="space-y-2">{diagnosis.steps.map((step, index) => (<li key={index} className="flex items-start gap-3 bg-hva-primary/20 p-3 rounded-lg"><span className="flex items-center justify-center w-6 h-6 rounded-full bg-green-500/20 text-green-400 text-xs font-bold shrink-0">{index + 1}</span><span className="text-hva-cream/90 text-sm">{step}</span></li>))}</ul>
                            </div>
                        </div>
                        <div className="p-4 border-t border-hva-border bg-hva-primary/30 flex justify-end">
                            <button onClick={closeDiagnosis} className="px-6 py-2 bg-hva-accent text-hva-primary font-bold rounded-lg hover:bg-hva-accent/90 transition-colors">حسناً، فهمت</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Network Request Details Modal */}
            {selectedRequest && (
                <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
                    <div className="bg-hva-card border border-hva-border w-full max-w-3xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90%]">
                        <div className="p-6 border-b border-hva-border flex justify-between items-center bg-hva-primary/50">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2"><Network size={24} className="text-hva-accent" /> تفاصيل الطلب</h3>
                            <button onClick={() => setSelectedRequest(null)} className="text-hva-muted hover:text-white transition-colors"><X size={24} /></button>
                        </div>
                        <div className="p-6 overflow-y-auto space-y-6 dir-ltr text-left">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-hva-primary/20 p-3 rounded-lg"><span className="text-hva-muted text-xs block uppercase">URL</span><span className="text-hva-cream font-mono break-all">{selectedRequest.url}</span></div>
                                <div className="bg-hva-primary/20 p-3 rounded-lg"><span className="text-hva-muted text-xs block uppercase">Method</span><span className="text-hva-cream font-bold">{selectedRequest.method}</span></div>
                                <div className="bg-hva-primary/20 p-3 rounded-lg"><span className="text-hva-muted text-xs block uppercase">Status</span><span className={`font-bold ${selectedRequest.status === 'error' ? 'text-red-500' : 'text-green-400'}`}>{selectedRequest.status}</span></div>
                                <div className="bg-hva-primary/20 p-3 rounded-lg"><span className="text-hva-muted text-xs block uppercase">Duration</span><span className="text-hva-cream">{selectedRequest.duration}ms</span></div>
                            </div>
                            {selectedRequest.requestBody && (
                                <div>
                                    <h4 className="text-hva-muted text-sm font-bold mb-2 uppercase">Request Body</h4>
                                    <pre className="bg-black/30 p-4 rounded-lg text-xs text-green-400 overflow-x-auto font-mono">{JSON.stringify(selectedRequest.requestBody, null, 2)}</pre>
                                </div>
                            )}
                            {selectedRequest.responseBody && (
                                <div>
                                    <h4 className="text-hva-muted text-sm font-bold mb-2 uppercase">Response Body</h4>
                                    <pre className="bg-black/30 p-4 rounded-lg text-xs text-blue-400 overflow-x-auto font-mono">{JSON.stringify(selectedRequest.responseBody, null, 2)}</pre>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LogsView;
