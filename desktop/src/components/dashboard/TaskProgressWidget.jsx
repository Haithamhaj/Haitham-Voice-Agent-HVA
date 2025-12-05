import React, { useState, useEffect, useRef } from 'react';
import { Activity, CheckCircle, Clock, SkipForward, Cpu, Zap } from 'lucide-react';

const TaskProgressWidget = () => {
    const [logs, setLogs] = useState([]);
    const [activeLLM, setActiveLLM] = useState(null);
    const ws = useRef(null);
    const logsEndRef = useRef(null);

    useEffect(() => {
        const connect = () => {
            ws.current = new WebSocket('ws://127.0.0.1:8765/ws');

            ws.current.onopen = () => {
                console.log('TaskProgressWidget connected');
            };

            ws.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };

            ws.current.onclose = () => {
                console.log('TaskProgressWidget disconnected, reconnecting...');
                setTimeout(connect, 3000);
            };
        };

        connect();
        return () => ws.current?.close();
    }, []);

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    const handleMessage = (data) => {
        const timestamp = new Date().toLocaleTimeString();

        if (data.type === 'llm_start') {
            setActiveLLM({
                model: data.model,
                task: data.task,
                details: data.details,
                startTime: Date.now()
            });
            addLog({ type: 'info', message: `🤖 ${data.model} started: ${data.task}`, timestamp });
        } else if (data.type === 'llm_end') {
            setActiveLLM(null);
            addLog({
                type: 'success',
                message: `✅ ${data.model} finished (Cost: $${data.cost?.toFixed(4) || '0.0000'})`,
                timestamp
            });
        } else if (data.type === 'task_progress') {
            addLog({
                type: data.status === 'skipped' ? 'skip' : 'process',
                message: `${data.file}: ${data.details}`,
                status: data.status,
                timestamp
            });
        } else if (data.type === 'log') {
            addLog({ type: 'info', message: data.message, timestamp });
        }
    };

    const addLog = (log) => {
        setLogs(prev => [...prev.slice(-50), log]); // Keep last 50 logs
    };

    return (
        <div className="bg-hva-card rounded-2xl border border-hva-border p-6 h-full flex flex-col shadow-lg shadow-black/20">
            <div className="flex items-center justify-between mb-4 shrink-0">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20">
                        <Activity size={22} />
                    </div>
                    <div>
                        <h3 className="text-hva-cream font-semibold text-lg">Live Activity</h3>
                        <p className="text-xs text-hva-muted">Real-time system operations</p>
                    </div>
                </div>
                {activeLLM && (
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/10 border border-purple-500/20 rounded-lg animate-pulse">
                        <Cpu size={14} className="text-purple-400" />
                        <span className="text-xs font-medium text-purple-300">
                            {activeLLM.model} Working...
                        </span>
                    </div>
                )}
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-2 min-h-[200px]">
                {logs.length === 0 ? (
                    <div className="text-center text-hva-muted py-8 text-sm italic">
                        Waiting for tasks...
                    </div>
                ) : (
                    logs.map((log, idx) => (
                        <div key={idx} className={`p-3 rounded-lg border text-sm flex items-start gap-3 ${log.type === 'success' ? 'bg-green-500/5 border-green-500/10 text-green-300' :
                                log.type === 'skip' ? 'bg-gray-500/5 border-gray-500/10 text-gray-400' :
                                    'bg-hva-bg/50 border-hva-border-subtle text-hva-cream'
                            }`}>
                            <div className="mt-0.5 shrink-0">
                                {log.type === 'success' ? <CheckCircle size={16} className="text-green-400" /> :
                                    log.type === 'skip' ? <SkipForward size={16} className="text-gray-400" /> :
                                        log.message.includes('Gemini') || log.message.includes('GPT') ? <Zap size={16} className="text-yellow-400" /> :
                                            <Clock size={16} className="text-blue-400" />}
                            </div>
                            <div className="flex-1">
                                <div className="leading-relaxed">{log.message}</div>
                                <div className="text-[10px] opacity-50 mt-1 font-mono">{log.timestamp}</div>
                            </div>
                        </div>
                    ))
                )}
                <div ref={logsEndRef} />
            </div>
        </div>
    );
};

export default TaskProgressWidget;
