import React, { useEffect, useRef } from 'react';
import { Send, User, Bot, Mic, MicOff } from 'lucide-react';
import { api } from '../services/api';
import { useWebSocketContext } from '../context/WebSocketContext';
import { useChatContext } from '../context/ChatContext';

const ChatView = () => {
    const { messages, setMessages, isProcessing, setIsProcessing } = useChatContext();
    const [input, setInput] = React.useState('');
    const messagesEndRef = useRef(null);

    const { isListening, toggleListening, lastLog } = useWebSocketContext();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Handle incoming logs
    useEffect(() => {
        if (lastLog) {
            setMessages(prev => {
                const lastMsg = prev[prev.length - 1];
                // If last message is a log, update it to avoid clutter
                if (lastMsg && lastMsg.role === 'system' && lastMsg.type === 'log') {
                    const newMsgs = [...prev];
                    newMsgs[newMsgs.length - 1] = {
                        role: 'system',
                        content: lastLog.message,
                        type: 'log',
                        timestamp: lastLog.timestamp
                    };
                    return newMsgs;
                }
                // Otherwise add new log message
                return [...prev, {
                    role: 'system',
                    content: lastLog.message,
                    type: 'log',
                    timestamp: lastLog.timestamp
                }];
            });
        }
    }, [lastLog, setMessages]);

    const handleVoiceToggle = async () => {
        if (isListening) {
            await toggleListening();
            return;
        }

        try {
            // Start listening
            const result = await toggleListening();

            if (result && result.transcript) {
                const transcript = result.transcript;

                // Add user message
                const userMessage = { role: 'user', content: transcript };
                setMessages(prev => [...prev, userMessage]);
                setIsProcessing(true);

                // Send to Chat API
                try {
                    const response = await api.sendChat(transcript);
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: response.response,
                        data: response.data, // Store rich data
                        model: response.model // Store model name
                    }]);
                } catch (error) {
                    console.error("Chat error:", error);
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: 'عذراً، حدث خطأ في معالجة الأمر.'
                    }]);
                } finally {
                    setIsProcessing(false);
                }
            } else {
                // Handle empty transcript
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: 'عذراً، لم أسمع شيئاً. هل يمكنك التحدث مرة أخرى؟'
                }]);
            }
        } catch (error) {
            console.error("Voice error:", error);
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsProcessing(true);

        try {
            const response = await api.sendChat(input);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.response,
                data: response.data, // Store rich data
                model: response.model // Store model name
            }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'عذراً، حدث خطأ في الاتصال.'
            }]);
        } finally {
            setIsProcessing(false);
        }
    };

    const getModelBadgeColor = (model) => {
        if (!model) return 'bg-gray-500/20 text-gray-400';
        if (model.includes('Local') || model.includes('Qwen')) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
        if (model.includes('GPT')) return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
        if (model.includes('Gemini')) return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
        return 'bg-hva-accent/20 text-hva-accent border-hva-accent/30';
    };

    const handleConfirm = async (msgData) => {
        if (!msgData || !msgData.command) return;

        // Add user confirmation message
        const userMessage = { role: 'user', content: 'موافق' };
        setMessages(prev => [...prev, userMessage]);
        setIsProcessing(true);

        try {
            // Send direct command with confirmed=True
            const response = await api.sendChat(
                "موافق",
                msgData.command,
                { ...msgData.params, confirmed: true }
            );

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.response,
                data: response.data,
                model: response.model
            }]);
        } catch (error) {
            console.error("Confirm error:", error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'عذراً، حدث خطأ أثناء التنفيذ.'
            }]);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleReject = () => {
        const userMessage = { role: 'user', content: 'إلغاء' };
        setMessages(prev => [...prev, userMessage]);

        setTimeout(() => {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'تم إلغاء العملية.',
                model: 'System'
            }]);
        }, 500);
    };

    const renderMessageContent = (msg) => {
        const content = (
            <>
                {/* If it's a simple text message */}
                {!msg.data && <p className="leading-relaxed">{msg.content}</p>}

                {/* Confirmation Request */}
                {msg.data && msg.data.status === 'confirmation_required' && (
                    <div className="space-y-4">
                        <div className="bg-yellow-500/10 border border-yellow-500/30 p-4 rounded-xl">
                            <p className="text-yellow-200 font-medium mb-2">⚠️ تأكيد العملية</p>
                            <p className="text-white/90 leading-relaxed">{msg.data.message}</p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => handleConfirm(msg.data)}
                                className="flex-1 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 py-2 rounded-lg transition-colors font-medium"
                            >
                                موافق
                            </button>
                            <button
                                onClick={handleReject}
                                className="flex-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 py-2 rounded-lg transition-colors font-medium"
                            >
                                إلغاء
                            </button>
                        </div>
                    </div>
                )}

                {/* If it's an action result with files */}
                {msg.data && msg.data.files && Array.isArray(msg.data.files) && (
                    <div className="space-y-3">
                        <p className="leading-relaxed font-medium border-b border-white/10 pb-2 mb-2">
                            {msg.content}
                        </p>
                        <div className="grid gap-2">
                            {msg.data.files.map((file, i) => (
                                <div
                                    key={i}
                                    onClick={() => api.openFile(file.path)}
                                    className="flex items-center gap-3 bg-black/20 p-3 rounded-lg hover:bg-black/30 transition-colors cursor-pointer group"
                                >
                                    <div className={`w-8 h-8 rounded flex items-center justify-center transition-transform group-hover:scale-110 ${file.type === 'directory' || file.extension === 'DIR'
                                        ? 'bg-blue-500/20 text-blue-400'
                                        : 'bg-hva-accent/20 text-hva-accent'
                                        }`}>
                                        {file.type === 'directory' || file.extension === 'DIR'
                                            ? <span className="text-xs font-bold">DIR</span>
                                            : <span className="text-xs font-bold">{file.extension?.replace('.', '') || 'FILE'}</span>
                                        }
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium truncate text-white group-hover:text-hva-accent transition-colors">{file.name}</p>
                                        <p className="text-xs text-hva-muted">{file.size_human} • {file.path}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Organization Plan Visualization */}
                {msg.data && msg.data.type === 'organization_plan' && (
                    <div className="space-y-4">
                        <div className="bg-blue-500/10 border border-blue-500/30 p-4 rounded-xl">
                            <p className="text-blue-200 font-medium mb-2">📋 خطة التنظيم المقترحة</p>
                            <p className="text-white/90 leading-relaxed mb-4">{msg.data.message}</p>

                            <div className="space-y-2 max-h-60 overflow-y-auto custom-scrollbar pr-2">
                                {msg.data.plan.changes.map((change, i) => (
                                    <div key={i} className="bg-black/20 p-3 rounded-lg text-sm">
                                        <div className="flex items-center gap-2 text-hva-muted mb-1">
                                            <span className="w-2 h-2 rounded-full bg-red-400"></span>
                                            <span className="truncate" dir="ltr">{change.original_path.split('/').pop()}</span>
                                        </div>
                                        <div className="flex items-center gap-2 text-emerald-400 font-medium">
                                            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                                            <span className="truncate" dir="ltr">{change.category}/{change.new_filename}</span>
                                        </div>
                                        <p className="text-xs text-hva-muted mt-1 mr-4">{change.reason}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {msg.data.status === 'confirmation_required' && (
                            <div className="flex gap-3">
                                <button
                                    onClick={() => handleConfirm(msg.data)}
                                    className="flex-1 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 py-2 rounded-lg transition-colors font-medium"
                                >
                                    تنفيذ الخطة
                                </button>
                                <button
                                    onClick={handleReject}
                                    className="flex-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 py-2 rounded-lg transition-colors font-medium"
                                >
                                    إلغاء
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Default rich rendering (skip if confirmation or files or plan) */}
                {msg.data && !msg.data.files && msg.data.status !== 'confirmation_required' && msg.data.type !== 'organization_plan' && (
                    <div className="space-y-2">
                        <p className="leading-relaxed">{msg.content}</p>
                        {msg.data.data && typeof msg.data.data === 'string' && (
                            <pre className="bg-black/20 p-3 rounded-lg text-xs overflow-x-auto text-hva-muted font-mono">
                                {msg.data.data}
                            </pre>
                        )}
                    </div>
                )}
            </>
        );

        return (
            <div className="flex flex-col gap-2">
                {content}
                {msg.model && (
                    <div className={`self-end text-[10px] px-2 py-0.5 rounded-full border ${getModelBadgeColor(msg.model)} font-medium mt-1`}>
                        {msg.model}
                    </div>
                )}
            </div>
        );
    };

    const textareaRef = useRef(null);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
        }
    }, [input]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend(e);
        }
    };

    return (
        <div className="flex flex-col h-full space-y-4">
            <header>
                <h1 className="text-5xl font-bold text-hva-cream flex items-center gap-3">
                    <Bot className="text-hva-accent" size={32} />
                    المحادثة
                </h1>
                <p className="text-hva-muted mt-1">تحدث مع هيثم كتابياً أو صوتياً</p>
            </header>

            <div className="flex-1 bg-hva-card rounded-2xl border border-hva-border-subtle overflow-hidden flex flex-col">
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.map((msg, index) => {
                        if (msg.role === 'system') {
                            return (
                                <div key={index} className="flex w-full justify-center my-2 animate-fade-in">
                                    <div className="bg-black/40 border border-white/10 px-4 py-2 rounded-full flex items-center gap-2 text-xs text-hva-muted font-mono">
                                        <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse"></div>
                                        {msg.content}
                                    </div>
                                </div>
                            );
                        }
                        return (
                            <div key={index} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-hva-accent text-hva-primary' : 'bg-hva-primary text-hva-accent'
                                    }`}>
                                    {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                                </div>
                                <div className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'user'
                                    ? 'bg-hva-accent/10 text-hva-cream rounded-tr-none'
                                    : 'bg-hva-primary/50 text-hva-cream rounded-tl-none'
                                    }`}>
                                    {renderMessageContent(msg)}
                                </div>
                            </div>
                        );
                    })}

                    {/* Voice Listening Indicator */}
                    {isListening && (
                        <div className="flex gap-4 flex-row-reverse animate-pulse">
                            <div className="w-10 h-10 rounded-full bg-red-500/20 text-red-500 flex items-center justify-center shrink-0 border border-red-500/50">
                                <Mic size={20} />
                            </div>
                            <div className="bg-red-500/10 text-red-400 p-4 rounded-2xl rounded-tr-none border border-red-500/20">
                                <p className="leading-relaxed">جاري الاستماع...</p>
                            </div>
                        </div>
                    )}

                    {isProcessing && (
                        <div className="flex gap-4">
                            <div className="w-10 h-10 rounded-full bg-hva-primary text-hva-accent flex items-center justify-center shrink-0">
                                <Bot size={20} />
                            </div>
                            <div className="bg-hva-primary/50 p-4 rounded-2xl rounded-tl-none flex gap-2 items-center">
                                <div className="w-2 h-2 bg-hva-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-2 h-2 bg-hva-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-2 h-2 bg-hva-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="p-4 bg-hva-primary/30 border-t border-hva-border-subtle">
                    <form onSubmit={handleSend} className="flex gap-3 items-end">
                        <button
                            type="button"
                            onClick={handleVoiceToggle}
                            className={`p-3 rounded-xl transition-all duration-300 ${isListening
                                ? 'bg-red-500 text-white shadow-[0_0_15px_rgba(239,68,68,0.5)] animate-pulse'
                                : 'bg-hva-primary hover:bg-hva-primary/80 text-hva-muted hover:text-hva-cream border border-hva-border-subtle'
                                }`}
                            title={isListening ? "إيقاف الاستماع" : "بدء التحدث"}
                        >
                            {isListening ? <MicOff size={20} /> : <Mic size={20} />}
                        </button>

                        <textarea
                            ref={textareaRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={isListening ? "تحدث الآن..." : "اكتب رسالتك هنا... (Shift+Enter لسطر جديد)"}
                            className="flex-1 bg-hva-card border border-hva-border-subtle rounded-xl px-4 py-3 text-hva-cream focus:outline-none focus:border-hva-accent transition-colors disabled:opacity-50 resize-none max-h-[200px] overflow-y-auto min-h-[50px]"
                            dir="rtl"
                            disabled={isListening}
                            rows={1}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isProcessing || isListening}
                            className="bg-hva-accent hover:bg-hva-accent-light text-hva-primary p-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Send size={20} className={isProcessing ? "opacity-0" : ""} />
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ChatView;
