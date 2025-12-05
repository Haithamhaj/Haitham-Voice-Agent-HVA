import React, { useState, useEffect } from 'react';
import { Activity, Clock, Sun } from 'lucide-react';

import { api } from '../services/api';
import UsageWidget from '../components/dashboard/UsageWidget';
import SystemHealthWidget from '../components/dashboard/SystemHealthWidget';
import FileSystemTree from '../components/dashboard/FileSystemTree';
import CheckpointsWidget from '../components/dashboard/CheckpointsWidget';
import TaskProgressWidget from '../components/dashboard/TaskProgressWidget';

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
        <div className="h-full flex flex-col gap-6 p-6 overflow-y-auto">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-hva-cream mb-1">لوحة التحكم</h1>
                    <p className="text-hva-muted text-sm">نظرة عامة على حالة النظام والأداء</p>
                </div>
                <div className="flex gap-3">
                    <button className="bg-hva-primary/20 hover:bg-hva-primary/30 text-hva-primary px-4 py-2 rounded-xl text-sm font-medium transition-colors">
                        تحديث البيانات
                    </button>
                </div>
            </header>

            <div className="grid grid-cols-12 gap-6">
                {/* Top Row: System Health & Usage (8 cols) + Quick Stats (4 cols) */}
                <div className="col-span-12 lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <SystemHealthWidget />
                    <UsageWidget />
                </div>

                <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-hva-card p-5 rounded-2xl border border-hva-border-subtle hover:border-hva-accent/30 transition-all group flex-1 flex items-center justify-between">
                        <div>
                            <span className="text-3xl font-bold text-hva-cream block mb-1">{stats.emails}</span>
                            <h3 className="text-hva-muted text-sm font-medium">رسائل غير مقروءة</h3>
                        </div>
                        <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center text-red-400 group-hover:scale-110 transition-transform border border-red-500/20">
                            <Activity size={24} />
                        </div>
                    </div>

                    <div className="bg-hva-card p-5 rounded-2xl border border-hva-border-subtle hover:border-hva-accent/30 transition-all group flex-1 flex items-center justify-between">
                        <div>
                            <span className="text-3xl font-bold text-hva-cream block mb-1">{stats.events}</span>
                            <h3 className="text-hva-muted text-sm font-medium">مواعيد اليوم</h3>
                        </div>
                        <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center text-green-400 group-hover:scale-110 transition-transform border border-green-500/20">
                            <Clock size={24} />
                        </div>
                    </div>
                </div>

                {/* Middle Row: Live Activity & History */}
                <div className="col-span-12 grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-[300px]">
                    <TaskProgressWidget />
                    <CheckpointsWidget />
                </div>

                {/* Bottom Row: File System Tree (Full Width) */}
                <div className="col-span-12 min-h-[400px]">
                    <FileSystemTree />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
