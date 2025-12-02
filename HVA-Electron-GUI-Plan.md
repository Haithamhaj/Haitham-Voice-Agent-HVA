# 🚀 خطة بناء واجهة HVA الجديدة (Electron + React)

## 📋 نظرة عامة

**الهدف:** تحويل HVA من تطبيق Menu Bar بسيط إلى تطبيق Desktop احترافي بواجهة جميلة.

**التقنيات:**
- **Frontend:** Electron + React + Tailwind CSS
- **Backend:** Python FastAPI (يشتغل كـ Local Server)
- **التواصل:** HTTP REST API + WebSocket (للـ real-time updates)

**النتيجة النهائية:**
- تطبيق `.app` تفتحه بضغطة وحدة
- واجهة جميلة بألوان Imperfect Success
- كل ميزات HVA متاحة من الواجهة
- يشتغل 100% على جهازك (Offline)

---

## 🏗️ هيكل المشروع الجديد

```
Haitham Voice Agent (HVA)/
├── haitham_voice_agent/          # ← الكود الحالي (ما يتغير)
│   ├── dispatcher.py
│   ├── tools/
│   └── ...
│
├── api/                          # ← جديد: FastAPI Backend
│   ├── __init__.py
│   ├── main.py                   # نقطة الدخول للـ API
│   ├── routes/
│   │   ├── voice.py              # endpoints للصوت
│   │   ├── memory.py             # endpoints للذاكرة
│   │   ├── gmail.py              # endpoints للبريد
│   │   ├── calendar.py           # endpoints للتقويم
│   │   ├── tasks.py              # endpoints للمهام
│   │   └── system.py             # endpoints للنظام
│   └── websocket.py              # real-time updates
│
├── desktop/                      # ← جديد: Electron App
│   ├── package.json
│   ├── main.js                   # Electron main process
│   ├── preload.js
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── Sidebar.jsx
│       │   ├── Dashboard.jsx
│       │   ├── MemoryView.jsx
│       │   ├── GmailView.jsx
│       │   ├── CalendarView.jsx
│       │   ├── VoiceButton.jsx
│       │   └── ...
│       └── styles/
│           └── globals.css
│
├── run_app.py                    # ← يتعدل: يشغل API + Electron
└── requirements.txt              # ← يتعدل: نضيف FastAPI
```

---

## 📝 المرحلة 1: إنشاء FastAPI Backend

### الخطوة 1.1: إنشاء ملف API الرئيسي

**📁 الملف:** `api/main.py`

**🤖 Prompt للـ AI:**

```
أنشئ ملف api/main.py لمشروع HVA بالمواصفات التالية:

1. استخدم FastAPI مع CORS مفعل لـ localhost
2. أضف WebSocket endpoint للـ real-time updates
3. اربطه مع الـ dispatcher الموجود في haitham_voice_agent/dispatcher.py
4. أضف health check endpoint
5. أضف endpoint لتشغيل الاستماع الصوتي
6. أضف endpoint لإيقاف الاستماع
7. أضف endpoint لإرسال أمر نصي

الـ dispatcher الحالي يستخدم async ويدعم هذه الـ tools:
- memory (VoiceMemoryTools)
- gmail (ConnectionManager)
- files (FileTools)
- tasks (task_manager)
- system (SystemTools)
- browser (BrowserTools)
- terminal (TerminalTools)
- calendar (CalendarTools)
- drive (DriveTools)

اجعل الـ API يشتغل على port 8765
```

**📄 الكود المتوقع:**

```python
# api/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from haitham_voice_agent.dispatcher import ToolDispatcher
from haitham_voice_agent.tools.voice.stt import STTHandler
from haitham_voice_agent import llm_router

app = FastAPI(title="HVA API", version="2.0")

# CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
dispatcher = ToolDispatcher()
stt_handler = STTHandler()
active_connections: list[WebSocket] = []

# WebSocket Manager
async def broadcast(message: dict):
    for connection in active_connections:
        await connection.send_json(message)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "HVA API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming messages
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.post("/voice/start")
async def start_listening():
    """Start voice listening"""
    await broadcast({"type": "status", "listening": True})
    # Trigger STT
    result = await stt_handler.listen()
    await broadcast({"type": "transcript", "text": result})
    return {"status": "listening"}

@app.post("/voice/stop")
async def stop_listening():
    """Stop voice listening"""
    await broadcast({"type": "status", "listening": False})
    return {"status": "stopped"}

@app.post("/command")
async def send_command(command: dict):
    """Send a text command to HVA"""
    text = command.get("text", "")
    
    # Route through LLM
    plan = await llm_router.route(text)
    
    # Execute plan
    results = []
    for step in plan.get("steps", []):
        result = await dispatcher.dispatch(step)
        results.append(result)
        await broadcast({"type": "step_result", "result": result})
    
    return {"results": results}

@app.get("/memory/stats")
async def get_memory_stats():
    """Get memory system statistics"""
    memory_tool = dispatcher.tools.get("memory")
    if memory_tool:
        stats = await memory_tool.get_stats()
        return stats
    return {"error": "Memory tool not available"}

@app.get("/tasks")
async def get_tasks():
    """Get all tasks"""
    task_tool = dispatcher.tools.get("tasks")
    if task_tool:
        tasks = await task_tool.list_tasks()
        return tasks
    return {"error": "Task tool not available"}

@app.get("/gmail/unread")
async def get_unread_emails():
    """Get unread emails count and preview"""
    gmail_tool = dispatcher.tools.get("gmail")
    if gmail_tool:
        unread = await gmail_tool.get_unread_count()
        return unread
    return {"error": "Gmail tool not available"}

@app.get("/calendar/today")
async def get_today_events():
    """Get today's calendar events"""
    calendar_tool = dispatcher.tools.get("calendar")
    if calendar_tool:
        events = await calendar_tool.get_today_events()
        return events
    return {"error": "Calendar tool not available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)
```

---

### الخطوة 1.2: إنشاء Routes منفصلة

**🤖 Prompt للـ AI:**

```
أنشئ ملفات routes منفصلة في مجلد api/routes/ لمشروع HVA:

1. api/routes/voice.py - للتحكم بالصوت (start, stop, status)
2. api/routes/memory.py - للذاكرة (search, save, get_stats, get_relations)
3. api/routes/gmail.py - للبريد (list, read, reply, unread_count)
4. api/routes/calendar.py - للتقويم (today, week, create_event)
5. api/routes/tasks.py - للمهام (list, create, complete, delete)
6. api/routes/system.py - للنظام (status, modes, organize)

كل route يجب أن:
- يستورد الـ tool المناسب من dispatcher
- يرجع JSON response
- يدعم async
- يرسل updates عبر WebSocket عند الحاجة
```

---

## 📝 المرحلة 2: إنشاء Electron App

### الخطوة 2.1: تهيئة مشروع Electron

**🤖 Prompt للـ AI:**

```
أنشئ مشروع Electron + React في مجلد desktop/ بالمواصفات التالية:

1. استخدم Vite كـ bundler
2. استخدم React 18
3. استخدم Tailwind CSS
4. أضف electron-builder للـ packaging

أنشئ الملفات التالية:
- desktop/package.json
- desktop/main.js (Electron main process)
- desktop/preload.js
- desktop/vite.config.js
- desktop/tailwind.config.js
- desktop/src/main.jsx
- desktop/src/App.jsx
- desktop/index.html

الإعدادات:
- Window size: 1400x900
- Min size: 1000x700
- Frame: false (frameless window)
- Transparent: true (للـ rounded corners)
- Always on top: false
- Resizable: true
```

**📄 الكود المتوقع لـ main.js:**

```javascript
// desktop/main.js
const { app, BrowserWindow, ipcMain, globalShortcut } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let apiProcess;

// Start Python API
function startAPI() {
    const projectRoot = path.join(__dirname, '..');
    apiProcess = spawn('python', ['-m', 'api.main'], {
        cwd: projectRoot,
        env: { ...process.env, PYTHONPATH: projectRoot }
    });
    
    apiProcess.stdout.on('data', (data) => {
        console.log(`API: ${data}`);
    });
    
    apiProcess.stderr.on('data', (data) => {
        console.error(`API Error: ${data}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        frame: false,
        transparent: true,
        vibrancy: 'under-window',
        visualEffectState: 'active',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    // Load React app
    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, 'dist/index.html'));
    }

    // Register global shortcut
    globalShortcut.register('CommandOrControl+Shift+H', () => {
        mainWindow.webContents.send('trigger-voice');
    });
}

app.whenReady().then(() => {
    startAPI();
    
    // Wait for API to start
    setTimeout(createWindow, 2000);
});

app.on('window-all-closed', () => {
    if (apiProcess) apiProcess.kill();
    if (process.platform !== 'darwin') app.quit();
});

// IPC Handlers
ipcMain.handle('minimize', () => mainWindow.minimize());
ipcMain.handle('maximize', () => {
    if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
    } else {
        mainWindow.maximize();
    }
});
ipcMain.handle('close', () => mainWindow.close());
```

---

### الخطوة 2.2: إنشاء المكونات الأساسية

**🤖 Prompt للـ AI:**

```
أنشئ مكونات React لتطبيق HVA Desktop في desktop/src/components/ باستخدام الـ Design System التالي:

الألوان:
--bg-deep: #050a12
--bg-primary: #0a0f1a
--bg-card: #0f1520
--bg-card-hover: #141c2a
--accent: #5d9a9b (Teal)
--accent-light: #7ab8b9
--accent-glow: rgba(93, 154, 155, 0.3)
--text-cream: #f5e6d3
--text-muted: #8a9aaa
--text-dim: #5a6a7a
--border-subtle: rgba(255, 255, 255, 0.06)

الـ Border Radius:
- sm: 12px
- md: 16px
- lg: 24px
- xl: 32px

المكونات المطلوبة:

1. TitleBar.jsx - شريط العنوان مع أزرار التحكم (minimize, maximize, close)
2. Sidebar.jsx - القائمة الجانبية مع navigation
3. Dashboard.jsx - الصفحة الرئيسية مع stats و feature cards
4. VoiceButton.jsx - زر الاستماع مع animation للموجة الصوتية
5. MemoryView.jsx - عرض الذاكرة والعلاقات
6. GmailView.jsx - عرض الرسائل
7. CalendarView.jsx - عرض التقويم
8. TasksView.jsx - عرض المهام
9. SettingsView.jsx - الإعدادات

كل مكون يجب أن:
- يستخدم Tailwind CSS
- يدعم RTL (direction: rtl)
- يتواصل مع API على http://localhost:8765
- يستخدم WebSocket للـ real-time updates
```

---

### الخطوة 2.3: إنشاء App.jsx الرئيسي

**🤖 Prompt للـ AI:**

```
أنشئ ملف desktop/src/App.jsx الرئيسي لتطبيق HVA بالمواصفات التالية:

1. استخدم React Router للتنقل بين الصفحات
2. أضف WebSocket connection للـ real-time updates
3. أضف global state للـ listening status
4. أضف keyboard shortcut listener (Cmd+Shift+H)
5. Layout: TitleBar + Sidebar + Main Content

الصفحات:
- / → Dashboard
- /memory → MemoryView
- /gmail → GmailView
- /calendar → CalendarView
- /tasks → TasksView
- /settings → SettingsView

الـ Design:
- خلفية: bg-deep (#050a12)
- Sidebar على اليمين (RTL)
- Rounded corners على الـ window
```

**📄 الكود المتوقع:**

```jsx
// desktop/src/App.jsx
import { useState, useEffect } from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import TitleBar from './components/TitleBar';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import MemoryView from './components/MemoryView';
import GmailView from './components/GmailView';
import CalendarView from './components/CalendarView';
import TasksView from './components/TasksView';
import SettingsView from './components/SettingsView';
import VoiceOverlay from './components/VoiceOverlay';

function App() {
    const [isListening, setIsListening] = useState(false);
    const [wsConnected, setWsConnected] = useState(false);
    const [notifications, setNotifications] = useState([]);

    // WebSocket Connection
    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8765/ws');
        
        ws.onopen = () => {
            setWsConnected(true);
            console.log('WebSocket Connected');
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'status') {
                setIsListening(data.listening);
            } else if (data.type === 'notification') {
                setNotifications(prev => [...prev, data]);
            }
        };
        
        ws.onclose = () => {
            setWsConnected(false);
            // Reconnect after 3 seconds
            setTimeout(() => {}, 3000);
        };
        
        return () => ws.close();
    }, []);

    // Listen for keyboard shortcut from Electron
    useEffect(() => {
        window.electronAPI?.onTriggerVoice(() => {
            toggleListening();
        });
    }, []);

    const toggleListening = async () => {
        if (isListening) {
            await fetch('http://localhost:8765/voice/stop', { method: 'POST' });
        } else {
            await fetch('http://localhost:8765/voice/start', { method: 'POST' });
        }
    };

    return (
        <HashRouter>
            <div className="h-screen bg-[#050a12] text-[#f5e6d3] overflow-hidden rounded-2xl" dir="rtl">
                <TitleBar />
                
                <div className="flex h-[calc(100vh-40px)]">
                    <main className="flex-1 overflow-auto p-8">
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/memory" element={<MemoryView />} />
                            <Route path="/gmail" element={<GmailView />} />
                            <Route path="/calendar" element={<CalendarView />} />
                            <Route path="/tasks" element={<TasksView />} />
                            <Route path="/settings" element={<SettingsView />} />
                        </Routes>
                    </main>
                    
                    <Sidebar isListening={isListening} wsConnected={wsConnected} />
                </div>
                
                {isListening && <VoiceOverlay onClose={() => toggleListening()} />}
            </div>
        </HashRouter>
    );
}

export default App;
```

---

## 📝 المرحلة 3: ربط كل شي

### الخطوة 3.1: تعديل run_app.py

**🤖 Prompt للـ AI:**

```
عدل ملف run_app.py ليشغل:
1. FastAPI server على port 8765
2. Electron app من مجلد desktop/

يجب أن:
- يشغل الـ API أولاً وينتظر حتى يصير ready
- يشغل Electron بعدها
- يوقف كل شي عند الإغلاق
- يدعم development mode و production mode
```

**📄 الكود المتوقع:**

```python
# run_app.py (Updated)
import sys
import os
import subprocess
import time
import signal
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    processes = []
    
    def cleanup(signum=None, frame=None):
        print("\n🛑 Shutting down HVA...")
        for p in processes:
            if p.poll() is None:
                p.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # 1. Start API Server
    print("🚀 Starting HVA API Server...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "api.main"],
        cwd=project_root,
        env={**os.environ, "PYTHONPATH": str(project_root)}
    )
    processes.append(api_process)
    
    # Wait for API to be ready
    print("⏳ Waiting for API...")
    time.sleep(3)
    
    # 2. Start Electron App
    print("🖥️ Starting HVA Desktop...")
    desktop_dir = project_root / "desktop"
    
    if (desktop_dir / "node_modules").exists():
        electron_process = subprocess.Popen(
            ["npm", "run", "electron"],
            cwd=desktop_dir,
            shell=True
        )
        processes.append(electron_process)
    else:
        print("⚠️ Desktop not built. Run: cd desktop && npm install && npm run build")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            for p in processes:
                if p.poll() is not None:
                    print("⚠️ A process has stopped")
                    cleanup()
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
```

---

### الخطوة 3.2: تحديث requirements.txt

**🤖 Prompt للـ AI:**

```
أضف هذه المكتبات إلى requirements.txt:

fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=12.0
```

---

## 📝 المرحلة 4: بناء التطبيق النهائي

### الخطوة 4.1: بناء Electron للـ Production

**🤖 Prompt للـ AI:**

```
أنشئ script لبناء تطبيق HVA كـ .app file لـ macOS:

1. أضف electron-builder config في desktop/package.json
2. أنشئ script يبني الـ React app
3. يحزم الـ Python backend مع التطبيق
4. ينتج ملف .app جاهز للاستخدام

الاسم: HVA Premium.app
الأيقونة: من مجلد assets/
```

---

## 🎯 ملخص الخطوات

| # | المرحلة | الوقت المتوقع | الصعوبة |
|---|---------|--------------|---------|
| 1.1 | إنشاء api/main.py | 30 دقيقة | متوسط |
| 1.2 | إنشاء routes | 45 دقيقة | متوسط |
| 2.1 | تهيئة Electron | 20 دقيقة | سهل |
| 2.2 | إنشاء components | 2 ساعة | متوسط |
| 2.3 | إنشاء App.jsx | 30 دقيقة | سهل |
| 3.1 | تعديل run_app.py | 15 دقيقة | سهل |
| 3.2 | تحديث requirements | 5 دقائق | سهل |
| 4.1 | Build للـ production | 30 دقيقة | متوسط |

**المجموع: ~5 ساعات**

---

## 🔧 أوامر مفيدة

```bash
# تثبيت dependencies للـ API
cd "/Users/haitham/development/Haitham Voice Agent (HVA)"
pip install fastapi uvicorn websockets

# تهيئة Electron
cd desktop
npm init -y
npm install electron react react-dom react-router-dom
npm install -D vite @vitejs/plugin-react tailwindcss autoprefixer electron-builder

# تشغيل في Development
# Terminal 1:
python -m api.main

# Terminal 2:
cd desktop && npm run dev

# Terminal 3:
cd desktop && npm run electron

# بناء للـ Production
cd desktop && npm run build && npm run package
```

---

## 💡 نصائح للعمل مع AI

1. **ابدأ بملف واحد** - لا تطلب كل شي مرة وحدة
2. **انسخ الأخطاء كاملة** - عشان الـ AI يفهم المشكلة
3. **استخدم `@web`** - إذا واجهت مشكلة جديدة
4. **احفظ checkpoints** - بعد كل ميزة تشتغل
5. **جرب الكود قبل المتابعة** - لا تكمل على كود معطوب

---

## 📎 المرفقات

### Design System (CSS Variables)

```css
:root {
    --bg-deep: #050a12;
    --bg-primary: #0a0f1a;
    --bg-card: #0f1520;
    --bg-card-hover: #141c2a;
    --accent: #5d9a9b;
    --accent-light: #7ab8b9;
    --accent-glow: rgba(93, 154, 155, 0.3);
    --text-cream: #f5e6d3;
    --text-muted: #8a9aaa;
    --text-dim: #5a6a7a;
    --border-subtle: rgba(255, 255, 255, 0.06);
    --radius-sm: 12px;
    --radius-md: 16px;
    --radius-lg: 24px;
    --radius-xl: 32px;
}
```

### Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
    content: ["./src/**/*.{js,jsx}"],
    theme: {
        extend: {
            colors: {
                'hva-deep': '#050a12',
                'hva-primary': '#0a0f1a',
                'hva-card': '#0f1520',
                'hva-card-hover': '#141c2a',
                'hva-accent': '#5d9a9b',
                'hva-accent-light': '#7ab8b9',
                'hva-cream': '#f5e6d3',
                'hva-muted': '#8a9aaa',
                'hva-dim': '#5a6a7a',
            },
            borderRadius: {
                'hva-sm': '12px',
                'hva-md': '16px',
                'hva-lg': '24px',
                'hva-xl': '32px',
            }
        }
    }
}
```

---

## ✅ Checklist

- [ ] المرحلة 1.1: api/main.py
- [ ] المرحلة 1.2: routes/
- [ ] المرحلة 2.1: Electron setup
- [ ] المرحلة 2.2: React components
- [ ] المرحلة 2.3: App.jsx
- [ ] المرحلة 3.1: run_app.py
- [ ] المرحلة 3.2: requirements.txt
- [ ] المرحلة 4.1: Production build
- [ ] اختبار شامل
- [ ] 🎉 Done!

---

**Made with ❤️ for Haitham**

*هذه الخطة تقدر تستخدمها مع Claude أو GPT أو Gemini - كل الـ prompts جاهزة للنسخ*
