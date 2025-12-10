import React, { useState, useEffect } from 'react';
import { X, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { logger } from '../../developer-toolkit/logger';

const Toast = () => {
    const [toasts, setToasts] = useState([]);

    useEffect(() => {
        const unsubscribe = logger.subscribeErrors((log) => {
            addToast(log.message, 'error');
        });

        const handleNotification = (e) => {
            const { message, level } = e.detail;
            addToast(message, level === 'error' ? 'error' : level === 'success' ? 'success' : 'info');
        };

        window.addEventListener('hva-notification', handleNotification);

        return () => {
            unsubscribe();
            window.removeEventListener('hva-notification', handleNotification);
        };
    }, []);

    const addToast = (message, type = 'info') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
        setTimeout(() => removeToast(id), 5000);
    };

    const removeToast = (id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    };

    if (toasts.length === 0) return null;

    return (
        <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
            {toasts.map(toast => (
                <div
                    key={toast.id}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg min-w-[300px] animate-in slide-in-from-right duration-300 ${toast.type === 'error' ? 'bg-red-500 text-white' :
                        toast.type === 'success' ? 'bg-green-500 text-white' :
                            'bg-hva-card text-hva-cream border border-hva-border'
                        }`}
                >
                    {toast.type === 'error' && <AlertCircle size={20} />}
                    {toast.type === 'success' && <CheckCircle size={20} />}
                    {toast.type === 'info' && <Info size={20} />}

                    <p className="flex-1 text-sm font-medium">{toast.message}</p>

                    <button onClick={() => removeToast(toast.id)} className="opacity-70 hover:opacity-100">
                        <X size={16} />
                    </button>
                </div>
            ))}
        </div>
    );
};

export default Toast;
