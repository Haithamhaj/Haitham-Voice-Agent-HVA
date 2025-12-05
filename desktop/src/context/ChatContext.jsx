import React, { createContext, useContext, useState, useCallback } from 'react';

const ChatContext = createContext(null);

export const useChatContext = () => {
    const context = useContext(ChatContext);
    if (!context) {
        throw new Error('useChatContext must be used within a ChatProvider');
    }
    return context;
};

export const ChatProvider = ({ children }) => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'مرحباً هيثم، كيف يمكنني مساعدتك اليوم؟' }
    ]);
    const [isProcessing, setIsProcessing] = useState(false);

    const addMessage = useCallback((message) => {
        setMessages(prev => [...prev, message]);
    }, []);

    const updateLastMessage = useCallback((updater) => {
        setMessages(prev => {
            const newMsgs = [...prev];
            const lastIndex = newMsgs.length - 1;
            if (lastIndex >= 0) {
                newMsgs[lastIndex] = typeof updater === 'function'
                    ? updater(newMsgs[lastIndex])
                    : updater;
            }
            return newMsgs;
        });
    }, []);

    const clearMessages = useCallback(() => {
        setMessages([{ role: 'assistant', content: 'مرحباً هيثم، كيف يمكنني مساعدتك اليوم؟' }]);
    }, []);

    const value = {
        messages,
        setMessages,
        addMessage,
        updateLastMessage,
        clearMessages,
        isProcessing,
        setIsProcessing
    };

    return (
        <ChatContext.Provider value={value}>
            {children}
        </ChatContext.Provider>
    );
};

export default ChatContext;
