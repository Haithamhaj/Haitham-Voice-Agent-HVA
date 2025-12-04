import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Mic, MicOff } from 'lucide-react';
import { api } from '../services/api';
import { useWebSocketContext } from '../context/WebSocketContext';

const ChatView = () => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'مرحباً هيثم، كيف يمكنني مساعدتك اليوم؟' }
    ]);
    const [input, setInput] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const messagesEndRef = useRef(null);

    const { isListening, toggleListening } = useWebSocketContext();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

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
                        data: response.data // Store rich data
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
                data: response.data // Store rich data
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

    const renderMessageContent = (msg) => {
        // If it's a simple text message
        if (!msg.data) {
            return <p className="leading-relaxed">{msg.content}</p>;
        }

        // If it's an action result with files
        if (msg.data.files && Array.isArray(msg.data.files)) {
            return (
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
            );
        }

        // Default rich rendering
        return (
            <div className="space-y-2">
                <p className="leading-relaxed">{msg.content}</p>
                {msg.data.data && typeof msg.data.data === 'string' && (
                    <pre className="bg-black/20 p-3 rounded-lg text-xs overflow-x-auto text-hva-muted font-mono">
                        {msg.data.data}
                    </pre>
                )}
            </div>
        );
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
                    {messages.map((msg, index) => (
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
                    ))}

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
                    <form onSubmit={handleSend} className="flex gap-3 items-center">
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

                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={isListening ? "تحدث الآن..." : "اكتب رسالتك هنا..."}
                            className="flex-1 bg-hva-card border border-hva-border-subtle rounded-xl px-4 py-3 text-hva-cream focus:outline-none focus:border-hva-accent transition-colors disabled:opacity-50"
                            dir="rtl"
                            disabled={isListening}
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
