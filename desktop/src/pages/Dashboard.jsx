import React, { useState, useEffect } from 'react';
import { Activity, Clock, Sun } from 'lucide-react';

import { api } from '../services/api';
import UsageWidget from '../components/dashboard/UsageWidget';

const Dashboard = () => {
    const [stats, setStats] = useState({
        tasks: 0,
        emails: 0,
        events: 0
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const [tasksData, gmailData, calendarData] = await Promise.all([
                    api.fetchTasks(),
                    api.fetchEmails(),
                    api.fetchEvents()
                ]);

                setStats({
                    tasks: Array.isArray(tasksData) ? tasksData.length : (tasksData.tasks ? tasksData.tasks.length : 0),
                    emails: gmailData.count || (Array.isArray(gmailData) ? gmailData.length : 0),
                    events: calendarData.count || (Array.isArray(calendarData.events) ? calendarData.events.length : 0)
                });
            } catch (error) {
                console.error("Failed to fetch dashboard stats", error);
            }
        };

        fetchStats();
        // Refresh every minute
        const interval = setInterval(fetchStats, 60000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-5xl font-bold text-hva-cream">صباح الخير، هيثم</h1>
                    <p className="text-hva-muted mt-1">إليك ملخص سريع ليومك</p>
                </div>
                <div className="bg-hva-card p-3 rounded-2xl border border-hva-border-subtle flex items-center gap-3">
                    <Sun className="text-yellow-400" />
                    <span className="text-hva-cream font-medium">24°C مشمس</span>
                </div>
            </header>

            <div className="grid grid-cols-3 gap-6">
                <div className="bg-hva-card p-6 rounded-2xl border border-hva-border-subtle hover:border-hva-accent/30 transition-colors group">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                            <Activity size={20} />
                        </div>
                        <span className="text-2xl font-bold text-hva-cream">{stats.tasks}</span>
                    </div>
                    <h3 className="text-hva-muted font-medium">مهام معلقة</h3>
                </div>

                <div className="bg-hva-card p-6 rounded-2xl border border-hva-border-subtle hover:border-hva-accent/30 transition-colors group">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center text-red-400 group-hover:scale-110 transition-transform">
                            <Activity size={20} />
                        </div>
                        <span className="text-2xl font-bold text-hva-cream">{stats.emails}</span>
                    </div>
                    <h3 className="text-hva-muted font-medium">رسائل غير مقروءة</h3>
                </div>

                <div className="bg-hva-card p-6 rounded-2xl border border-hva-border-subtle hover:border-hva-accent/30 transition-colors group">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 group-hover:scale-110 transition-transform">
                            <Clock size={20} />
                        </div>
                        <span className="text-2xl font-bold text-hva-cream">{stats.events}</span>
                    </div>
                    <h3 className="text-hva-muted font-medium">مواعيد اليوم</h3>
                </div>

                {/* Usage Widget */}
                <UsageWidget />
            </div>

            <div className="bg-hva-card rounded-2xl border border-hva-border-subtle p-6">
                <h2 className="text-xl font-bold text-hva-cream mb-4">نشاط النظام</h2>
                <div className="space-y-4">
                    <div className="flex items-center gap-4 p-3 rounded-xl bg-hva-primary/50">
                        <div className="w-2 h-2 rounded-full bg-green-500"></div>
                        <div className="flex-1">
                            <div className="text-sm text-hva-cream">تم تحديث الذاكرة بنجاح</div>
                            <div className="text-xs text-hva-dim">قبل 5 دقائق</div>
                        </div>
                    </div>
                    <div className="flex items-center gap-4 p-3 rounded-xl bg-hva-primary/50">
                        <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                        <div className="flex-1">
                            <div className="text-sm text-hva-cream">تمت مزامنة البريد الإلكتروني</div>
                            <div className="text-xs text-hva-dim">قبل 15 دقيقة</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
