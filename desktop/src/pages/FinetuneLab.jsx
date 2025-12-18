import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { FlaskConical, Database, Activity, GitBranch, Send, Bot, FileText, CheckCircle, AlertCircle, Clock, Cpu, Play, Layout } from 'lucide-react';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';

// --- Components ---

const StatusCard = ({ title, status, subtext, icon: Icon }) => (
    <div className="bg-hva-card border border-hva-card-hover p-6 rounded-xl flex items-start gap-4">
        <div className={clsx("p-4 rounded-xl", status ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400")}>
            <Icon size={32} />
        </div>
        <div>
            <h3 className="text-hva-cream font-bold text-lg">{title}</h3>
            <div className={clsx("text-base font-bold mt-1", status ? "text-green-400" : "text-red-400")}>
                {status ? "موجود" : "مفقود"}
            </div>
            <div className="text-sm text-hva-muted mt-2 font-mono break-all">{subtext || "N/A"}</div>
        </div>
    </div>
);

const PipelineStep = ({ step, title, desc, status, isLast }) => (
    <div className="flex-1 relative min-w-[180px]">
        <div className="flex items-center gap-3 mb-3">
            <div className={clsx(
                "w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center font-bold text-base z-10 border-2 transition-all duration-300",
                status === "done" ? "bg-green-500/20 border-green-500 text-green-400 scale-100" :
                    status === "active" ? "bg-blue-500/20 border-blue-500 text-blue-400 animate-pulse scale-110" :
                        "bg-hva-card border-hva-muted text-hva-muted"
            )}>
                {step}
            </div>
            <h4 className={clsx("font-bold text-lg whitespace-nowrap", status === "done" ? "text-green-400" : "text-hva-cream")}>{title}</h4>
        </div>
        <p className="text-sm text-hva-muted pr-14 pl-4 min-h-[3rem] leading-relaxed">{desc}</p>
        {!isLast && (
            <div className={clsx(
                "absolute top-5 right-12 -left-6 h-0.5 transition-colors duration-500",
                status === "done" ? "bg-green-500/50" : "bg-hva-card-hover"
            )} />
        )}
    </div>
);

const ExperimentChat = () => {
    // Dual State for Side-by-Side Comparison
    const [messagesBase, setMessagesBase] = useState([]);
    const [messagesV2, setMessagesV2] = useState([]);

    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const baseEndRef = useRef(null);
    const v2EndRef = useRef(null);

    useEffect(() => {
        baseEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messagesBase]);

    useEffect(() => {
        v2EndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messagesV2]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { role: "user", content: input };

        // Update local UI immediately
        const newHistBase = [...messagesBase, userMsg];
        const newHistV2 = [...messagesV2, userMsg];

        setMessagesBase(newHistBase);
        setMessagesV2(newHistV2);

        setInput("");
        setLoading(true);

        try {
            // Parallel Fetch
            const [resBase, resV2] = await Promise.all([
                api.finetuneExperimentChat(newHistBase, "base").catch(err => ({ role: "assistant", content: `❌ Error: ${err.message}` })),
                api.finetuneExperimentChat(newHistV2, "haithm_v2").catch(err => ({ role: "assistant", content: `❌ Error: ${err.message}` }))
            ]);

            setMessagesBase([...newHistBase, resBase]);
            setMessagesV2([...newHistV2, resV2]);

        } catch (error) {
            console.error("Chat Error", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async (modelName, messages) => {
        if (messages.length === 0) return;
        try {
            const res = await api.finetuneSaveExperiment(messages, modelName);
            alert(`✅ Saved ${modelName} session to:\n${res.path}`);
        } catch (e) {
            console.error(e);
            alert("Failed to save session");
        }
    };

    const handleClear = () => {
        if (window.confirm("مسح المحادثة وبدء جلسة جديدة؟")) {
            setMessagesBase([]);
            setMessagesV2([]);
        }
    };

    // Helper to render a single chat column
    const renderChatColumn = (title, messages, ref, modelKey, borderColor) => (
        <div className={`flex-1 flex flex-col border ${borderColor} rounded-xl bg-black/20 overflow-hidden`}>
            <div className="p-3 bg-hva-primary/50 border-b border-white/10 flex justify-between items-center">
                <span className={`font-bold ${modelKey === 'haithm_v2' ? 'text-green-400' : 'text-gray-400'}`}>{title}</span>
                <button
                    onClick={() => handleSave(modelKey, messages)}
                    disabled={messages.length === 0}
                    className="text-xs bg-hva-card hover:bg-hva-card-hover px-3 py-1 rounded text-hva-muted transition-colors disabled:opacity-50"
                >
                    💾 حفظ
                </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4 h-[500px]">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-hva-muted opacity-30">
                        <p>لا توجد رسائل</p>
                    </div>
                )}
                {messages.map((msg, i) => (
                    <div key={i} className={clsx("flex flex-col max-w-[90%]", msg.role === "user" ? "self-end items-end" : "self-start items-start")}>
                        <div className={clsx("px-4 py-2 rounded-2xl text-sm whitespace-pre-wrap",
                            msg.role === "user" ? "bg-hva-accent text-white rounded-br-none" : "bg-hva-primary border border-hva-card-hover text-hva-cream rounded-bl-none"
                        )}>
                            {msg.content}
                        </div>
                        {msg.metadata && (
                            <span className="text-[10px] text-hva-muted mt-1 px-1">
                                {(msg.metadata.duration * 1000).toFixed(0)}ms
                            </span>
                        )}
                    </div>
                ))}
                <div ref={ref} />
            </div>
        </div>
    );

    return (
        <div className="bg-hva-card border border-hva-card-hover rounded-2xl p-6 shadow-lg mt-8">
            <div className="flex justify-between items-center mb-6">
                <h3 className="font-bold text-hva-cream text-2xl flex items-center gap-3">
                    <Layout size={28} className="text-blue-400" />
                    المحادثة المقارنة (Side-by-Side Experiment)
                </h3>
                <button onClick={handleClear} className="text-red-400 text-sm hover:underline px-3">🗑️ مسح الكل</button>
            </div>

            <div className="flex gap-4 mb-4">
                {renderChatColumn("Base Model (Qwen 3B)", messagesBase, baseEndRef, "base", "border-gray-500/30")}
                {renderChatColumn("Haithm-V2 (LoRA)", messagesV2, v2EndRef, "haithm_v2", "border-green-500/30")}
            </div>

            <form onSubmit={handleSend} className="bg-hva-primary/20 p-4 rounded-xl border border-hva-card-hover/50 flex gap-3">
                <input
                    className="flex-1 bg-hva-primary border border-hva-card-hover rounded-xl px-4 py-3 text-hva-cream focus:border-hva-accent outline-none transition-all"
                    placeholder="اكتب رسالة واحدة للنموذجين..."
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    disabled={loading}
                />
                <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    className="bg-hva-accent hover:bg-hva-accent/80 text-white px-6 rounded-xl font-bold transition-all disabled:opacity-50"
                >
                    {loading ? <Activity className="animate-spin" /> : <Send size={20} />}
                </button>
            </form>
        </div>
    );
};

// --- Main Page ---

const FinetuneLab = () => {
    // State
    const [status, setStatus] = useState(null);
    const [datasetPreview, setDatasetPreview] = useState([]);
    const [loading, setLoading] = useState(true);

    // Comparison State
    const [prompt, setPrompt] = useState("قم بإنشاء ملاحظة عن اجتماع الفريق غداً");
    const [comparisonResult, setComparisonResult] = useState(null);
    const [comparing, setComparing] = useState(false);

    // Chat State
    const [chatModel, setChatModel] = useState("gpt");
    const [chatInput, setChatInput] = useState("");
    const [chatHistory, setChatHistory] = useState([]);
    const [chatLoading, setChatLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // Initial Load
    useEffect(() => {
        loadData();
    }, []);

    // Scroll chat to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [chatHistory]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [statusData, previewData] = await Promise.all([
                api.finetuneStatus(),
                api.finetunePreview()
            ]);
            setStatus(statusData);
            setDatasetPreview(previewData);
        } catch (e) {
            console.error("Failed to load finetune data", e);
        } finally {
            setLoading(false);
        }
    };

    const handleCompare = async () => {
        if (!prompt.trim()) return;
        setComparing(true);
        try {
            const result = await api.finetuneStyleCompare(prompt);
            setComparisonResult(result);
        } catch (e) {
            console.error("Comparison failed", e);
            // Optional: set error state to show in UI
        } finally {
            setComparing(false);
        }
    };

    const handleChatSend = async (e) => {
        e.preventDefault();
        if (!chatInput.trim()) return;

        const newUserMsg = { role: 'user', content: chatInput };
        const newHistory = [...chatHistory, newUserMsg];

        setChatHistory(newHistory);
        setChatInput("");
        setChatLoading(true);

        try {
            const response = await api.finetuneChat(chatModel, newHistory);
            const reply = response.messages[0];
            setChatHistory([...newHistory, reply]);
        } catch (e) {
            console.error("Chat failed", e);
            setChatHistory([...newHistory, { role: 'assistant', content: "عذراً، حدث خطأ في الاتصال بالمدرب." }]);
        } finally {
            setChatLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full text-hva-accent">
                <div className="animate-spin mr-2"><Activity /></div>
                جاري تحميل المختبر...
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-8 pb-20">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-l from-hva-accent to-purple-400 mb-3">
                    مختبر النموذج (Fine-Tuning Lab)
                </h1>
                <p className="text-hva-muted text-xl max-w-4xl">
                    تجربة وتحسين أداء نموذج Qwen 2.5 (3B) باستخدام QLoRA للمهام الخاصة بـ HVA.
                </p>
            </div>

            {/* Pipeline Timeline */}
            <div className="bg-hva-card border border-hva-card-hover rounded-2xl p-8 shadow-lg">
                <h3 className="text-hva-cream font-bold mb-8 flex items-center gap-3 text-xl">
                    <Activity size={24} className="text-blue-400" />
                    مسار العمل (Pipeline)
                </h3>
                <div className="flex gap-6 overflow-x-auto pb-2">
                    <div className="min-w-[200px] flex-1">
                        <PipelineStep
                            step={1}
                            title="جمع البيانات"
                            desc="تجميع السجلات والبيانات من استخدام HVA"
                            status="done"
                        />
                    </div>
                    <div className="min-w-[200px] flex-1">
                        <PipelineStep
                            step={2}
                            title="بناء مجموعة البيانات"
                            desc="تحويل السجلات إلى تنسيق JSONL (Alpaca)"
                            status={status?.dataset_exists ? "done" : "active"}
                        />
                    </div>
                    <div className="min-w-[200px] flex-1">
                        <PipelineStep
                            step={3}
                            title="التدريب (QLoRA)"
                            desc="تحسين النموذج باستخدام Low-Rank Adaptation"
                            status={status?.finetuned_model_exists ? "done" : (status?.dataset_exists ? "active" : "pending")}
                        />
                    </div>
                    <div className="min-w-[200px] flex-1">
                        <PipelineStep
                            step={4}
                            title="النشر والتقييم"
                            desc="دمج النموذج المحسن واختبار الأداء"
                            status={status?.finetuned_model_exists ? "active" : "pending"}
                            isLast
                        />
                    </div>
                </div>
            </div>

            {/* Status Cards - Wider Grid */}
            <div className="grid grid-cols-2 gap-8">
                <StatusCard
                    title="ملف البيانات (Dataset)"
                    status={status?.dataset_exists}
                    subtext={status?.dataset_path}
                    icon={Database}
                />
                <StatusCard
                    title="النموذج المحسن (LoRA)"
                    status={status?.finetuned_model_exists}
                    subtext={status?.finetuned_model_path}
                    icon={Cpu}
                />
            </div>

            {/* Comparison Section - Large */}
            <div className="bg-hva-card border border-hva-card-hover rounded-2xl p-8 shadow-lg">
                <h3 className="font-bold text-hva-cream text-2xl mb-6 flex items-center gap-3">
                    <GitBranch size={28} className="text-purple-400" />
                    مقارنة النماذج: Base vs Haithm-V1 Style
                </h3>

                <div className="flex gap-6 items-end mb-8">
                    <div className="flex-1">
                        <label className="block text-base text-hva-muted mb-3">أدخل نصاً لاختبار النموذج:</label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            className="w-full bg-hva-primary border border-hva-card-hover rounded-xl p-4 text-hva-cream focus:border-hva-accent outline-none text-lg shadow-inner"
                            rows={2}
                        />
                    </div>
                    <button
                        onClick={handleCompare}
                        disabled={comparing}
                        className="bg-hva-accent hover:bg-hva-accent/80 text-white px-8 py-5 rounded-xl font-bold flex items-center gap-3 disabled:opacity-50 text-lg shadow-lg hover:shadow-hva-accent/20 transition-all"
                    >
                        {comparing ? <Activity className="animate-spin" /> : <Play size={24} />}
                        تشغيل المقارنة
                    </button>
                </div>

                <div className="grid grid-cols-2 gap-8 mt-8">
                    {/* Base Model */}
                    <div className="bg-hva-primary/30 rounded-xl p-6 border border-hva-card-hover">
                        <div className="flex justify-between mb-4 items-end">
                            <span className="font-bold text-gray-400 text-lg">Base Model (Qwen 3B)</span>
                            {comparisonResult && <span className="text-hva-muted font-mono">{(comparisonResult.base_runtime_sec * 1000).toFixed(0)}ms</span>}
                        </div>
                        <div className={clsx("whitespace-pre-wrap text-hva-cream text-base font-mono bg-black/20 p-4 rounded-lg leading-relaxed shadow-inner min-h-[100px]", !comparisonResult && "flex items-center justify-center text-hva-muted/50")}>
                            {comparing ? (
                                <div className="flex items-center gap-2"><Activity className="animate-spin" size={16} /> جاري المعالجة...</div>
                            ) : comparisonResult ? (
                                comparisonResult.base_response
                            ) : (
                                "ستظهر إجابة الموديل الأساسي هنا..."
                            )}
                        </div>
                    </div>

                    {/* Finetuned Model */}
                    <div className="bg-hva-primary/30 rounded-xl p-6 border border-green-500/30 relative overflow-hidden">
                        {status?.finetuned_model_exists && (
                            <div className="absolute top-0 right-0 bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded-bl-lg font-bold">نشط</div>
                        )}
                        <div className="flex justify-between mb-4 items-end">
                            <span className="font-bold text-green-400 text-lg">Haithm-V2 (LoRA)</span>
                            {comparisonResult && <span className="text-green-400/70 font-mono">{(comparisonResult.haithm_v1_runtime_sec * 1000).toFixed(0)}ms</span>}
                        </div>

                        <div className={clsx("whitespace-pre-wrap text-hva-cream text-base font-mono bg-black/20 p-4 rounded-lg leading-relaxed shadow-inner min-h-[100px]", !comparisonResult && "flex items-center justify-center text-hva-muted/50")}>
                            {comparing ? (
                                <div className="flex items-center gap-2"><Activity className="animate-spin" size={16} /> جاري المعالجة...</div>
                            ) : comparisonResult ? (
                                comparisonResult.haithm_v1_response && !comparisonResult.haithm_v1_response.startsWith("[Error") ? (
                                    comparisonResult.haithm_v1_response
                                ) : (
                                    <div className="text-red-400 flex items-center gap-2">
                                        <AlertCircle size={20} />
                                        {comparisonResult.haithm_v1_response || "النموذج غير متوفر"}
                                    </div>
                                )
                            ) : (
                                "ستظهر إجابة الموديل المطور هنا..."
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Dataset Preview */}
            <div className="bg-hva-card border border-hva-card-hover rounded-2xl overflow-hidden shadow-lg">
                <div className="p-6 border-b border-hva-card-hover flex justify-between items-center bg-hva-primary/20">
                    <h3 className="font-bold text-hva-cream flex items-center gap-3 text-xl">
                        <FileText size={24} className="text-yellow-400" />
                        معاينة البيانات ({datasetPreview.length} صفوف)
                    </h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-base text-right">
                        <thead className="bg-hva-primary/60 text-hva-muted font-bold">
                            <tr>
                                <th className="p-4 w-1/4">Instruction</th>
                                <th className="p-4 w-1/3">Input (Transcript)</th>
                                <th className="p-4">Output (JSON/Action)</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-hva-card-hover text-hva-cream/90">
                            {datasetPreview.map((row, i) => (
                                <tr key={i} className="hover:bg-hva-card-hover/50 transition-colors">
                                    <td className="p-4 truncate max-w-xs" title={row.instruction}>{row.instruction}</td>
                                    <td className="p-4 truncate max-w-md dir-rtl" title={row.input}>{row.input}</td>
                                    <td className="p-4 truncate max-w-sm font-mono text-sm text-green-300/80" title={row.output}>{row.output}</td>
                                </tr>
                            ))}
                            {datasetPreview.length === 0 && (
                                <tr>
                                    <td colSpan={3} className="p-10 text-center text-hva-muted text-lg">لا توجد بيانات متاحة للعرض حالياً</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Experiment Chat Section */}
            <ExperimentChat />

            {/* Tutor Chat - Bottom Section */}
            <div className="bg-hva-card border border-hva-card-hover rounded-2xl shadow-xl overflow-hidden mt-4">
                <div className="bg-hva-primary/90 p-6 border-b border-hva-card-hover flex justify-between items-center">
                    <div>
                        <h3 className="font-bold text-hva-cream flex items-center gap-3 text-2xl">
                            <Bot size={28} className="text-hva-accent" />
                            المدرب الذكي (Fine-Tuning Tutor)
                        </h3>
                        <p className="text-hva-muted mt-2 text-base">اسأل المدرب عن تفاصيل هذه الصفحة أو عملية التدريب وكيفية قراءة النتائج.</p>
                    </div>
                </div>

                {/* Chat Container - Fixed Height */}
                <div className="h-[500px] flex flex-col relative">
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-hva-primary/30">
                        {chatHistory.length === 0 && (
                            <div className="text-center text-hva-muted/50 text-lg py-20">
                                مرحباً! أنا المدرب الذكي.<br />اسألني عن QLoRA، أو البيانات، أو كيفية قراءة النتائج.
                            </div>
                        )}
                        {chatHistory.map((msg, idx) => (
                            <div key={idx} className={clsx("flex flex-col max-w-[80%]", msg.role === 'user' ? "self-start items-start" : "self-end items-end")}>
                                <div className={clsx(
                                    "px-6 py-4 rounded-3xl text-base whitespace-pre-wrap shadow-sm",
                                    msg.role === 'user'
                                        ? "bg-hva-card-hover text-hva-cream rounded-tr-none mr-auto border border-hva-card-hover"
                                        : "bg-hva-accent/20 text-hva-cream border border-hva-accent/30 rounded-tl-none ml-auto"
                                )}>
                                    {msg.role === 'assistant' ? <ReactMarkdown>{msg.content}</ReactMarkdown> : msg.content}
                                </div>
                                <span className="text-xs text-hva-muted mt-2 px-2 font-medium">
                                    {msg.role === 'user' ? 'أنت' : 'المدرب'}
                                </span>
                            </div>
                        ))}
                        {chatLoading && (
                            <div className="self-end flex items-center gap-2 text-hva-muted text-xs p-4">
                                <div className="w-2.5 h-2.5 bg-hva-accent rounded-full animate-bounce" />
                                <div className="w-2.5 h-2.5 bg-hva-accent rounded-full animate-bounce [animation-delay:0.2s]" />
                                <div className="w-2.5 h-2.5 bg-hva-accent rounded-full animate-bounce [animation-delay:0.4s]" />
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Bar */}
                    <div className="p-6 bg-hva-card border-t border-hva-card-hover">
                        <form onSubmit={handleChatSend} className="relative flex gap-4">
                            <div className="relative">
                                <select
                                    value={chatModel}
                                    onChange={(e) => setChatModel(e.target.value)}
                                    className="h-full appearance-none bg-hva-primary text-sm text-hva-muted border border-hva-card-hover rounded-xl px-4 pr-8 focus:border-hva-accent outline-none cursor-pointer hover:bg-hva-card-hover transition-colors"
                                >
                                    <option value="gpt">GPT-4o</option>
                                    <option value="gemini">Gemini</option>
                                </select>
                                <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none text-hva-muted">
                                    <Bot size={14} />
                                </div>
                            </div>

                            <input
                                type="text"
                                value={chatInput}
                                onChange={(e) => setChatInput(e.target.value)}
                                placeholder="اكتب سؤالك هنا..."
                                className="flex-1 bg-hva-primary border border-hva-card-hover rounded-xl px-6 py-4 text-base text-hva-cream focus:border-hva-accent outline-none shadow-inner transition-all"
                                disabled={chatLoading}
                            />
                            <button
                                type="submit"
                                disabled={chatLoading || !chatInput.trim()}
                                className="bg-hva-accent hover:bg-hva-accent/80 text-white px-8 rounded-xl font-bold flex items-center gap-2 disabled:opacity-50 shadow-lg hover:shadow-hva-accent/20 transition-all"
                            >
                                <Send size={20} />
                                إرسال
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div >
    );
};

export default FinetuneLab;
