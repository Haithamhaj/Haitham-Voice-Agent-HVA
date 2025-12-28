import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Brain, Mail, Calendar, CheckSquare, Settings, Mic, MessageSquare, Activity, FlaskConical, Library } from 'lucide-react';
import clsx from 'clsx';

const Sidebar = ({ isListening, wsConnected, toggleListening }) => {
    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'الرئيسية' },
        { path: '/chat', icon: MessageSquare, label: 'المحادثة' },
        { path: '/memory', icon: Brain, label: 'الذاكرة' },
        { path: '/knowledge', icon: Library, label: 'استوديو المعرفة' },
        { path: '/finetune-lab', icon: FlaskConical, label: 'مختبر النموذج' },
        { path: '/gmail', icon: Mail, label: 'البريد' },
        { path: '/calendar', icon: Calendar, label: 'التقويم' },
        { path: '/tasks', icon: CheckSquare, label: 'المهام' },
        { path: '/logs', icon: Activity, label: 'السجلات' },
        { path: '/settings', icon: Settings, label: 'الإعدادات' },
    ];

    return (
        <div className="w-64 bg-hva-card border-l border-hva-card-hover flex flex-col h-full">
            <div className="p-6 flex flex-col items-center border-b border-hva-card-hover">
                <button
                    onClick={toggleListening}
                    className={clsx(
                        "w-16 h-16 rounded-full flex items-center justify-center mb-3 transition-all duration-300 cursor-pointer hover:scale-105 active:scale-95",
                        isListening ? "bg-red-500/20 text-red-500 animate-pulse shadow-[0_0_20px_rgba(239,68,68,0.4)]" : "bg-hva-accent/20 text-hva-accent hover:bg-hva-accent/30"
                    )}
                >
                    <Mic size={32} />
                </button>
                <h2 className="text-hva-cream font-bold text-lg">HVA Premium</h2>
                <div className="flex items-center gap-2 mt-1">
                    <div className={clsx("w-2 h-2 rounded-full", wsConnected ? "bg-green-500" : "bg-red-500")}></div>
                    <span className="text-xs text-hva-muted">{wsConnected ? "متصل" : "غير متصل"}</span>
                </div>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => clsx(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200",
                            isActive
                                ? "bg-hva-accent/10 text-hva-accent shadow-sm"
                                : "text-hva-muted hover:bg-hva-card-hover hover:text-hva-cream"
                        )}
                    >
                        <item.icon size={20} />
                        <span className="font-medium">{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-hva-card-hover">
                <div className="bg-hva-primary/50 rounded-xl p-3">
                    <div className="text-xs text-hva-dim mb-1">حالة النظام</div>
                    <div className="flex items-center justify-between text-sm text-hva-cream">
                        <span>الذاكرة</span>
                        <span className="text-green-400">نشط</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
