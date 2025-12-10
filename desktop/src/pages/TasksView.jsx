import React, { useState, useEffect } from 'react';
import { CheckSquare, Plus, Trash2, CheckCircle2, Circle } from 'lucide-react';
import { api } from '../services/api';

const TasksView = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.fetchTasks()
            .then(data => {
                setTasks(Array.isArray(data) ? data : []);
            })
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-hva-cream flex items-center gap-3">
                        <CheckSquare className="text-green-500" size={32} />
                        المهام
                    </h1>
                    <p className="text-hva-muted mt-1">إدارة قائمة المهام</p>
                </div>
                <button
                    onClick={() => {
                        const title = window.prompt("عنوان المهمة:");
                        if (title) {
                            setLoading(true);
                            api.sendChat(`Add task ${title}`)
                                .then(() => {
                                    // Refresh tasks after short delay to allow backend to process
                                    setTimeout(() => {
                                        api.fetchTasks().then(data => setTasks(Array.isArray(data) ? data : []));
                                        setLoading(false);
                                    }, 1000);
                                })
                                .catch(err => {
                                    console.error(err);
                                    setLoading(false);
                                });
                        }
                    }}
                    className="flex items-center gap-2 bg-hva-accent hover:bg-hva-accent-light text-hva-primary font-bold px-4 py-2 rounded-xl transition-colors">
                    <Plus size={18} />
                    <span>مهمة جديدة</span>
                </button>
            </header>

            <div className="bg-hva-card rounded-2xl border border-hva-border-subtle overflow-hidden">
                {loading ? (
                    <div className="p-8 text-center text-hva-muted">جاري التحميل...</div>
                ) : tasks.length > 0 ? (
                    <div className="divide-y divide-hva-border-subtle">
                        {tasks.map((task, index) => (
                            <div key={index} className="p-4 flex items-center gap-4 hover:bg-hva-card-hover transition-colors group">
                                <button className="text-hva-dim hover:text-green-500 transition-colors">
                                    {task.completed ? <CheckCircle2 size={24} className="text-green-500" /> : <Circle size={24} />}
                                </button>

                                <div className="flex-1">
                                    <h3 className={`font - medium text - lg ${task.completed ? 'text-hva-dim line-through' : 'text-hva-cream'} `}>
                                        {task.title || task.content || "مهمة بدون عنوان"}
                                    </h3>
                                    {task.due_date && (
                                        <p className="text-xs text-hva-muted mt-1">
                                            تستحق في: {new Date(task.due_date).toLocaleDateString()}
                                        </p>
                                    )}
                                </div>

                                <button className="opacity-0 group-hover:opacity-100 p-2 text-hva-dim hover:text-red-500 transition-all">
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="p-12 text-center flex flex-col items-center text-hva-muted">
                        <CheckSquare size={48} className="mb-4 opacity-20" />
                        <p>لا توجد مهام حالياً</p>
                    </div>
                )}
            </div>
        </div >
    );
};

export default TasksView;
