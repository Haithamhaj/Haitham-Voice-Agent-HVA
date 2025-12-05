import React from 'react';
import { HashRouter, Routes, Route, useLocation } from 'react-router-dom';
import TitleBar from './components/layout/TitleBar';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './pages/Dashboard';
import GmailView from './pages/GmailView';
import CalendarView from './pages/CalendarView';
import TasksView from './pages/TasksView';
import SettingsView from './pages/SettingsView';
import ChatView from './pages/ChatView';
import MemoryView from './pages/MemoryView';
import LogsView from './pages/LogsView';
import VoiceOverlay from './components/voice/VoiceOverlay';
import Toast from './components/common/Toast';
import { WebSocketProvider, useWebSocketContext } from './context/WebSocketContext';

const AppContent = () => {
  const { isListening, wsConnected, toggleListening } = useWebSocketContext();
  const location = useLocation();
  const isChatView = location.pathname === '/chat';

  return (
    <div className="flex flex-col h-screen bg-hva-primary text-hva-cream overflow-hidden" dir="rtl">
      <TitleBar />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar isListening={isListening} wsConnected={wsConnected} toggleListening={toggleListening} />

        <main className="flex-1 overflow-auto p-8 bg-hva-primary/30">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<ChatView />} />
            <Route path="/memory" element={<MemoryView />} />
            <Route path="/gmail" element={<GmailView />} />
            <Route path="/calendar" element={<CalendarView />} />
            <Route path="/tasks" element={<TasksView />} />
            <Route path="/settings" element={<SettingsView />} />
            <Route path="/logs" element={<LogsView />} />
          </Routes>
        </main>
      </div>

      {/* Only show overlay if listening AND NOT on chat view */}
      {isListening && !isChatView && <VoiceOverlay onClose={toggleListening} />}
      <Toast />
    </div>
  );
};

import { ChatProvider } from './context/ChatContext';

function App() {
  return (
    <WebSocketProvider>
      <ChatProvider>
        <HashRouter>
          <AppContent />
        </HashRouter>
      </ChatProvider>
    </WebSocketProvider>
  );
}

export default App;
