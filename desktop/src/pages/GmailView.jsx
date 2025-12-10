import React, { useState, useEffect } from 'react';
import { Mail, RefreshCw, ExternalLink, Star } from 'lucide-react';
import { api } from '../services/api';

const GmailView = () => {
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchEmails = () => {
        setLoading(true);
        api.fetchEmails()
            .then(data => {
                // Handle different response structures based on API implementation
                const list = Array.isArray(data) ? data : (data.messages || []);
                setEmails(list);
            })
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchEmails();
    }, []);

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-hva-cream flex items-center gap-3">
                        <Mail className="text-red-500" size={32} />
                        البريد الإلكتروني
                    </h1>
                    <p className="text-hva-muted mt-1">الرسائل غير المقروءة</p>
                </div>
                <button
                    onClick={fetchEmails}
                    className="p-2 bg-hva-card hover:bg-hva-card-hover rounded-lg text-hva-cream transition-colors"
                >
                    <RefreshCw size={20} className={loading ? "animate-spin" : ""} />
                </button>
            </header>

            <div className="bg-hva-card rounded-2xl border border-hva-border-subtle overflow-hidden">
                {loading ? (
                    <div className="p-8 text-center text-hva-muted">جاري التحميل...</div>
                ) : emails.length > 0 ? (
                    <div className="divide-y divide-hva-border-subtle">
                        {emails.map((email, index) => (
                            <div key={index} className="p-4 hover:bg-hva-card-hover transition-colors cursor-pointer group">
                                <div className="flex items-center justify-between mb-1">
                                    <h3 className="font-bold text-hva-cream group-hover:text-hva-accent transition-colors">
                                        {email.subject || "بدون عنوان"}
                                    </h3>
                                    <span className="text-xs text-hva-dim">{email.date || "الآن"}</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <p className="text-sm text-hva-muted truncate max-w-[80%]">
                                        {email.snippet || email.sender || "لا يوجد معاينة"}
                                    </p>
                                    <Star size={16} className="text-hva-dim hover:text-yellow-400 cursor-pointer" />
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="p-12 text-center flex flex-col items-center text-hva-muted">
                        <Mail size={48} className="mb-4 opacity-20" />
                        <p>لا توجد رسائل جديدة</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GmailView;
