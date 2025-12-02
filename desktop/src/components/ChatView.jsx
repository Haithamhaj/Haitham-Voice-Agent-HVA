import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Mic } from 'lucide-react';

const ChatView = () => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'مرحباً هيثم، كيف يمكنني مساعدتك اليوم؟' }
    ]);
    const [input, setInput] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsProcessing(true);

        try {
            // Send to backend (Assuming a chat endpoint exists or using voice/text endpoint)
            // For now, we'll simulate a response or use a placeholder endpoint if available
            // In a real scenario, we'd POST to /chat or similar

            // Simulating response for UI demo
            setTimeout(() => {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: 'عذراً، ميزة المحادثة النصية قيد التطوير حالياً في الواجهة الخلفية. يرجى استخدام الأوامر الصوتية.'
                }]);
                setIsProcessing(false);
            }, 1000);

        } catch (error) {
            console.error("Chat error:", error);
            setIsProcessing(false);
        }
    };

    return (
        <div className="flex flex-col h-full space-y-4">
            <header>
                <h1 className="text-3xl font-bold text-hva-cream flex items-center gap-3">
                    <Bot className="text-hva-accent" size={32} />
                    المحادثة
                </h1>
                <p className="text-hva-muted mt-1">تحدث مع هيثم كتابياً</p>
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
                                <p className="leading-relaxed">{msg.content}</p>
                            </div>
                        </div>
                    ))}
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
                    <form onSubmit={handleSend} className="flex gap-3">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="اكتب رسالتك هنا..."
                            className="flex-1 bg-hva-card border border-hva-border-subtle rounded-xl px-4 py-3 text-hva-cream focus:outline-none focus:border-hva-accent transition-colors"
                            dir="rtl"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isProcessing}
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
