import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Clock, MapPin, Trash2 } from 'lucide-react';
import { api } from '../services/api';

const CalendarView = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.fetchEvents()
            .then(data => {
                const list = Array.isArray(data) ? data : (data.events || []);
                setEvents(list);
            })
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-hva-cream flex items-center gap-3">
                        <CalendarIcon className="text-blue-500" size={32} />
                        التقويم
                    </h1>
                    <p className="text-hva-muted mt-1">مواعيد اليوم</p>
                </div>
            </header>

            <div className="grid gap-4">
                {loading ? (
                    <div className="text-center text-hva-muted py-8">جاري التحميل...</div>
                ) : events.length > 0 ? (
                    events.map((event, index) => (
                        <div key={index} className="bg-hva-card p-5 rounded-2xl border border-hva-border-subtle flex gap-4 hover:border-blue-500/30 transition-colors">
                            <div className="flex flex-col items-center justify-center bg-hva-primary/50 rounded-xl w-16 h-16 text-blue-400">
                                <span className="text-xs font-bold uppercase">{new Date(typeof event.start === 'string' ? event.start : (event.start?.dateTime || event.start?.date)).toLocaleDateString('en-US', { month: 'short' })}</span>
                                <span className="text-xl font-bold">{new Date(typeof event.start === 'string' ? event.start : (event.start?.dateTime || event.start?.date)).getDate()}</span>
                            </div>

                            <div className="flex-1">
                                <h3 className="text-lg font-bold text-hva-cream mb-1">{event.summary || "بدون عنوان"}</h3>
                                <div className="flex items-center gap-4 text-sm text-hva-muted">
                                    <div className="flex items-center gap-1">
                                        <Clock size={14} />
                                        <span>
                                            {new Date(typeof event.start === 'string' ? event.start : (event.start?.dateTime || event.start?.date)).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                                            {' - '}
                                            {event.end ? new Date(typeof event.end === 'string' ? event.end : (event.end?.dateTime || event.end?.date)).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : ''}
                                        </span>
                                    </div>
                                    {event.location && (
                                        <div className="flex items-center gap-1">
                                            <MapPin size={14} />
                                            <span>{event.location}</span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <button
                                onClick={() => {
                                    if (window.confirm("حذف الموعد من التقويم؟")) {
                                        api.deleteEvent(event.id).then(() => {
                                            setEvents(prev => prev.filter(e => e.id !== event.id));
                                        });
                                    }
                                }}
                                className="p-2 text-hva-muted hover:text-red-500 transition-colors self-center opacity-70 hover:opacity-100"
                            >
                                <Trash2 size={18} />
                            </button>
                        </div>
                    ))
                ) : (
                    <div className="p-12 text-center flex flex-col items-center text-hva-muted bg-hva-card rounded-2xl border border-hva-border-subtle">
                        <CalendarIcon size={48} className="mb-4 opacity-20" />
                        <p>لا توجد مواعيد اليوم</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CalendarView;
