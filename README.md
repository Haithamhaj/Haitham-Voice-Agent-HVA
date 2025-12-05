Of course. As an expert technical writer for the Haitham Voice Agent project, I will update the README.md to accurately reflect the current state of the codebase.

Here is the full, updated `README.md` content:

# Haitham Voice Agent (HVA) 🎤🤖

<div dir="rtl">

**وكيل صوتي ذكي لنظام macOS مع توجيه هجين للذكاء الاصطناعي، ذاكرة حية، وعي كامل بالنظام، وتكامل عميق مع خدمات Google.**

</div>

A voice-operated automation agent for macOS with hybrid LLM routing, a living memory system, full system awareness, and deep Google Suite integration.

> [!NOTE]
> **Status: Production Ready (v2.0)** 🚀
> The system has undergone a major architectural refactoring to introduce a **Client-Server Architecture** using **FastAPI** (Backend) and **Electron + React** (Frontend), ensuring a modern, responsive, and beautiful user experience.

---

## 📋 جدول المحتويات | Table of Contents

- [نظرة عامة | Overview](#-نظرة-عامة--overview)
- [المميزات الرئيسية | Key Features](#-المميزات-الرئيسية--key-features)
- [البنية المعمارية | Architecture](#-البنية-المعمارية--architecture)
- [الوحدات والأدوات | Modules & Tools](#-الوحدات-والأدوات--modules--tools)
- [أدوات المطور | Developer Toolkit](#-أدوات-المطور--developer-toolkit)
- [نظام الأمان | Safety System](#-نظام-الأمان--safety-system)
- [التثبيت والإعداد | Installation & Setup](#-التثبيت-والإعداد--installation--setup)
- [الاستخدام | Usage](#-الاستخدام--usage)
- [تتبع التكلفة والميزانية | Cost Tracking & Budgeting](#-تتبع-التكلفة-والميزانية--cost-tracking--budgeting)
- [استكشاف الأخطاء | Troubleshooting](#-استكشاف-الأخطاء--troubleshooting)

---

## 🌟 نظرة عامة | Overview

<div dir="rtl">

**Haitham Voice Agent (HVA)** هو وكيل صوتي ذكي مصمم خصيصاً لنظام macOS، يجمع بين قوة الذكاء الاصطناعي المتقدم والتحكم الصوتي الطبيعي. يدعم النظام اللغتين العربية والإنجليزية، ويستخدم استراتيجية توجيه ذكية متعددة الطبقات، ونظام "ذاكرة حية" يجمع بين قواعد البيانات العلائقية، الموجهة، والمتجهة لفهم السياق والعلاقات.

</div>

**Haitham Voice Agent (HVA)** is an intelligent voice-operated automation agent for macOS. It combines advanced AI with natural voice control, supporting both Arabic and English. The system uses a multi-layered, deterministic routing strategy and a "Living Memory" system that merges graph, vector, and relational databases to understand context and relationships.

### 🎯 الأهداف الأساسية | Core Objectives

- ✅ **Voice-to-Action Automation**: تحويل الأوامر الصوتية إلى إجراءات تلقائية.
- ✅ **Deterministic Routing**: اختيار النموذج الصحيح للمهمة بناءً على البيانات الوصفية، وليس عبر LLM آخر.
- ✅ **Living Memory System**: ذاكرة موحدة (Graph + Vector + SQL) تفهم العلاقات، المفاهيم، والحقائق.
- ✅ **System Awareness**: فهم عميق للجهاز، التطبيقات، والملفات.
- ✅ **Executive Personas**: أدوات متخصصة (سكرتير، مستشار) لإدارة المهام وتقديم الرؤى.
- ✅ **Full Google Integration**: ربط كامل مع Gmail, Calendar, Drive (Unified OAuth & Keychain).
- ✅ **Proactive Notifications**: نظام تنبيهات ذكي للمواعيد والإيميلات الهامة.
- ✅ **Safety First**: نظام أمان متعدد الطبقات يمنع الإجراءات المدمرة.

---

## ✨ المميزات الرئيسية | Key Features

### 🧠 التوجيه الذكي والحتمي | Intelligent & Deterministic Routing

<div dir="rtl">

بنية توجيه من 4 طبقات تضمن الدقة والكفاءة والتكلفة المثلى:
1.  **Intent Router**: يتعرف فوراً على الأوامر العربية الأساسية (مثل "احفظ ملاحظة") لتجاوز LLM بالكامل.
2.  **Ollama Orchestrator**: يعمل كطبقة وسطى لتوجيه الطلبات بين النماذج المحلية والسحابية.
3.  **LLM Router**: يوجه المهام استراتيجياً: **Gemini** للمستندات والتحليل، و **GPT** للتخطيط والأدوات (JSON).
4.  **Model Router**: الطبقة النهائية التي تختار النموذج الأمثل (مثل Flash مقابل Pro) بناءً على بيانات وصفية للمهمة (الجودة، التكلفة، المخاطر)، مما يضمن أفضل أداء بأقل تكلفة.

</div>

A 4-layer routing architecture ensures accuracy, efficiency, and cost-optimization:
1.  **Intent Router**: Instantly catches core Arabic commands (e.g., "save note") to bypass the LLM entirely for speed and reliability.
2.  **Ollama Orchestrator**: Acts as a middleware to route requests between local and cloud LLMs.
3.  **LLM Router**: Strategically routes tasks: **Gemini** for documents/analysis, **GPT** for planning/tools (JSON).
4.  **Model Router**: The final layer that deterministically chooses the best model variant (e.g., Flash vs. Pro) based on task metadata (quality, cost, risk), ensuring optimal performance at the lowest price.

### 🧑‍💼 السكرتير التنفيذي والمستشار النزيه | Executive Secretary & Honest Advisor

<div dir="rtl">

شخصيات الذكاء الاصطناعي المدمجة التي تعمل مع الذاكرة الحية:
*   **السكرتير (Secretary)**: "المنفذ". يدير المهام، والمشاريع، والملاحظات، وينظم مساحات العمل.
*   **المستشار (Advisor)**: "المفكر". يقدم رؤى، ويتحقق من سلامة الإجراءات المقترحة، ويراقب موارد النظام.

</div>

Integrated AI personas that work with the Living Memory:
*   **Secretary**: The "doer." Manages tasks, projects, notes, and organizes workspaces.
*   **Advisor**: The "thinker." Provides insights, validates proposed actions for safety, and monitors system resources.

### 💾 الذاكرة الحية | Living Memory (Graph + Vector + SQL)

<div dir="rtl">

تم توحيد نظام الذاكرة ليعمل كـ "عقل واحد" مترابط:
*   **Graph Store**: يفهم **العلاقات** بين الكيانات (مثل "مشروع ألف" مرتبط بـ "ملف التقرير" و "اجتماع الغد").
*   **Vector Store**: يبحث عن **المفاهيم** والأفكار (بحث دلالي للعثور على المعلومات بالمعنى).
*   **SQLite Store**: يخزن **الحقائق** بشكل منظم (الملاحظات، المهام، البيانات الوصفية).
*   **Transactional Logic**: يضمن نزاهة البيانات (Data Integrity) عبر التراجع التلقائي عند الخطأ.

</div>

The memory system is unified to act as a single, interconnected "brain":
*   **Graph Store**: Understands **relationships** between entities (e.g., "Project Alpha" is linked to "report.pdf" and "tomorrow's meeting").
*   **Vector Store**: Searches for **concepts** and ideas using semantic search.
*   **SQLite Store**: Stores structured **facts** like notes, tasks, and metadata.
*   **Transactional Logic**: Ensures data integrity via automatic rollback on failure.

### 📧 تكامل Gmail المتقدم | Advanced Gmail Integration

<div dir="rtl">

- **اتصال ذكي**: تبديل تلقائي بين **Gmail API** (الأساسي) و **IMAP** (الاحتياطي) لضمان استمرارية الخدمة.
- **تخزين آمن**: استخدام **macOS Keychain** لتخزين مفاتيح التشفير بشكل آمن.
- **مساعد LLM**: استخدام **Gemini** لتلخيص الرسائل واستخراج الإجراءات، و **GPT** لتوليد ردود ذكية.

</div>

- **Intelligent Connection**: Auto-switches between **Gmail API** (primary) and **IMAP** (fallback) for maximum uptime.
- **Secure Storage**: Uses **macOS Keychain** for secure encryption key storage.
- **LLM Helpers**: Leverages **Gemini** for summarization and action extraction, and **GPT** for generating smart replies.

### 🖥️ الوعي بالنظام والتحكم | System Awareness & Control

<div dir="rtl">

- **نظام 3 طبقات**: (ملف تعريف النظام، فهرس سريع، بحث عميق) لمعرفة كل شيء عن جهازك.
- **المنظم الذكي**: أدوات لتنظيف سطح المكتب وتنظيم مجلد التنزيلات تلقائياً.
- **إدارة مساحة العمل**: إنشاء وإدارة هياكل مجلدات المشاريع تلقائياً.

</div>

- **3-Layer System**: (System Profile, Quick Index, Deep Search) to know everything about your machine.
- **Smart Organizer**:
    - **Auto-Cleanup (72-Hour Rule)**: Automatically moves files older than 72 hours from `Downloads` to `Documents`, keeping your Downloads folder fresh.
    - **Strict Organization Rules**:
        - **Apps (`.app`)**: Moved to `~/Applications`.
        - **Installers (`.dmg`, `.pkg`)**: Moved to `~/Software`.
        - **Documents**: Moved to `~/Documents/{Category}` based on content.
    - **Content-Based Sorting**: Uses LLM to read file content and sort into granular subfolders (e.g., `Financials/Invoices` vs `Financials/Personal`).
    - **Context-Aware**: Distinguishes between Work and Personal documents.
    - **Deep Documents Organizer (v2.3)**:
        - **Visual Plan**: Shows a "Before -> After" tree visualization in Chat before making changes.
        - **Smart Renaming**: Renames files based on content (e.g., `scan01.pdf` -> `Invoice_Google_Oct.pdf`).
        - **Dry Run Mode**: Generates a "Change Plan" for your review before touching any file.
        - **Time Machine (Checkpoints)**: Every organization action is saved. You can say "Undo" to reverse all changes instantly.
- **Adaptive Learning (The "Mentor" Strategy)** 🎓:
    - **Digital Fingerprint (SHA-256)**: Every file gets a unique cryptographic hash for precise tracking across moves/renames.
    - **Learning from Manual Moves**: When you manually move a file, the system logs it as a "learning event" with confidence = 1.0.
    - **Confidence-Based Categorization**: 
        - **High Confidence (≥0.8)**: Applies learned pattern automatically (zero LLM cost).
        - **Medium Confidence (0.5-0.8)**: Falls back to LLM categorization.
        - **Low Confidence (<0.5)**: Uses LLM with extra validation.
    - **Passive Feedback Loop**: 
        - System tracks files organized using learned patterns.
        - If file stays in place → confidence +0.1 (you approved).
        - If file is moved again → confidence -0.3 (you corrected).
    - **Self-Improving**: The more you use it, the smarter it gets at predicting YOUR preferences (not generic AI guesses).
    - **Database**: All learning events stored in `learning_events` table with full audit trail.
- **Knowledge Tree (Dashboard)**:
    - **Real-Time Visualization**: A live, interactive file tree widget on the dashboard.
    - **Lazy Loading**: Efficiently browses the entire file system without performance lag.
    - **Direct Access**: Click to open files or folders instantly.
- **Tokenization Tracker**:
    - **Cost Monitoring**: Real-time tracking of token usage and costs for all models (GPT-4o, Gemini, Local).
    - **Dashboard Widget**: Visualizes spending and token count directly in the UI.
    - **Enhanced Analytics**:
        - **Daily Charts**: Visual bar charts showing daily cost trends.
        - **Detailed Logs**: Granular log table showing every request (Time, Model, Context, Cost).
    - **Detailed Breakdown**: Granular view of usage by model type (Gemini vs GPT) directly on the dashboard card.
- **Workspace Manager**: Automatically creates and manages project folder structures.
- **System Sentry (v2.4)**:
    - **Real-Time Monitoring**: Tracks CPU, RAM, Disk, and Battery health.
    - **Resource Hogs**: Identifies apps slowing down your Mac.
    - **Smart Cleanup**: Cleans system cache and temporary files to boost performance (with confirmation).
    - **Self-Healing (Integrity Check)**: Runs a comprehensive system verification at startup (`verify_integrity.py`) to prevent crashes before they happen.
- **System Health Dashboard**:
    - **Live Widget**: Visualizes system stats with progress bars and status badges.
    - **Smart Alerts**: Warns you when the system is strained and suggests fixes.
- **System History (Time Machine)**:
    - **Visual Timeline**: View a detailed history of all system operations (file moves, organization).
    - **Metadata Tracking**: See exactly which AI model was used, the cost, and token usage for each action.
    - **Instant Rollback**: Undo any operation with a single click, restoring files to their original locations.

### 🧠 Intelligent Memory & Organization
- **Deep Organization**: AI-powered analysis to rename and categorize files based on content.
- **Simple Organization (Free)**: Rule-based organization by file type (Images, Docs, etc.) with zero cost.
- **Safety Layer**: `OptimizationGuard` prevents re-analyzing unchanged files, ensuring $0.00 cost for duplicate runs.
- **Vector Memory**: Semantic search for all your notes and documents.
- **Graph Database**: Tracks relationships between files, projects, and concepts.

### 💰 Cost Transparency
- **Real-time Tracking**: See exact costs for every operation.
- **Detailed Breakdown**: View separate costs for **Gemini** (Analysis - Blue) and **GPT** (Reasoning - Green) in the dashboard.
- **Budget Safety**: System alerts or blocks redundant expensive operations.

### 🤖 ترقيات الذكاء (v1.1 - v1.7) | Intelligence Upgrades
<div dir="rtl">

- **Smart Feedback Agent**: نظام "نكز" ذكي في الموجز الصباحي يذكرك بالمشاريع المتوقفة باحترام وتدرج.
- **Clarification Agent**: لا يفشل عند الغموض! يستخدم حلقة ذكية (Robust Loop) للتوضيح حتى 3 محاولات. إذا قلت "ذكرني"، سيسألك "بماذا؟" ويسمع إجابتك.
- **Idea Agent**: حول أفكارك الخام إلى مشاريع منظمة. قل "عندي فكرة..." وسيقوم بإنشاء خطة مشروع كاملة (باستخدام **GPT-5 Mini** للسرعة والتكلفة).
- **iPhone Sync**: اربط هاتفك بالوكيل! قل لـ Siri: "Add task to HVA Inbox" وسيظهر في ذاكرة HVA فوراً.
- **Smart Calendar**: فهم كامل للوقت ("غداً"، "الاثنين القادم") وفحص ذكي للتوفر ("هل أنا مشغول؟").
- **Premium GUI**: واجهة فخمة (Dark Mode) مع مؤشر ذكاء حي يظهر من يفكر الآن (Ollama vs GPT).
- **Timezone-Aware Scheduling**: يفهم "اجتماع الساعة 5 بتوقيت القاهرة" ويحسب فرق التوقيت تلقائياً ليحجز الموعد الصحيح.
- **System Modes**: تفعيل "وضع الاجتماع" (كتم الصوت)، "وضع العمل" (تركيز)، أو "وضع الراحة" (استرخاء) بأمر صوتي واحد.
*   **Performance Optimization (v2.1)**: الانتقال إلى **Qwen 2.5 (3B)** كموديل محلي أساسي بعد اختبارات أثبتت دقة عالية وسرعة استجابة (1.2s) مقارنة بـ 7B.

</div>

- **Smart Feedback Agent**: Intelligent "nudge" system in morning briefing for stale projects.
- **Clarification Agent**: Handles ambiguity gracefully with a robust retry loop (Max 3 attempts). If you say "Remind me", it asks "About what?" and listens for your answer.
- **Idea Agent**: Turns raw ideas into structured projects. Say "I have an idea..." and it creates a full project spec (using **GPT-5 Mini** for speed/cost).
- **iPhone Sync**: Connect your phone! Tell Siri "Add task to HVA Inbox" and it syncs to HVA memory instantly.
- **Smart Calendar**: Natural language date parsing ("tomorrow", "next Mon") and smart availability checks ("Am I free?").
- **Premium GUI (v1.9)**: Stunning Dark Mode interface with live "Active Agent" indicators, simulated depth, and polished interactions.
- **Desktop Experience**: Native macOS App Bundle (`HVA Premium.app`) for one-click launch.
- **Smart File Listing**: Ask "Show files in Downloads" to get a categorized list (Today, Yesterday, Older) directly in the chat.
- **Timezone-Aware Scheduling**: Smartly handles "Meeting at 5pm Cairo time" by calculating the correct time difference relative to your local timezone.
- **System Modes**: Activate "Meeting Mode" (Mute/DND), "Work Mode" (Focus), or "Chill Mode" (Relax) with a single voice command.
*   **Performance Optimization (v2.1)**: Switched to **Qwen 2.5 (3B)** as the primary local model after rigorous testing proved high accuracy with 3x faster response (1.2s) compared to 7B.

### 📱 تطبيق شريط القوائم وواجهة المستخدم | Menu Bar App & GUI

<div dir="rtl">

- **اختصار عالمي**: `⌘⇧H` (Cmd+Shift+H) لبدء الاستماع من أي مكان.
- **Premium Dashboard**: لوحة تحكم تعرض حالة النظام، الطقس، والمهام.
- **Live Logs Widget**: نافذة حية تعرض "تفكير" النظام لحظة بلحظة (LLM Events) وتقدم المهام.
- **Memory View (v2.5)**: واجهة بصرية مذهلة لاستعراض الذاكرة الحية بطبقاتها الثلاث (SQL, Vector, Graph) مع رسوم بيانية تفاعلية وشروحات توضيحية.
- **Gmail & Calendar**: واجهات مخصصة لعرض الرسائل والمواعيد.
- **Active Agent Indicator**: مؤشر حي يظهر لك "عقل" النظام وهو يعمل (تحليل، تفكير سحابي، تنفيذ أدوات).
- **إجراءات سريعة**: أزرار للوصول السريع للموجز الصباحي والتقويم.

</div>

- **Global Hotkey**: `⌘⇧H` (Cmd+Shift+H) to start listening from anywhere.
- **Premium Dashboard**: A dynamic grid layout displaying System Health, Usage, Quick Stats, and a detailed System History timeline.
- **Live Logs Widget**: Real-time visibility into the agent's brain. Watch as it thinks (LLM), executes tools, and processes files with live status updates.
- **Memory View (v2.5)**: A stunning 3D-inspired visualization of the Living Memory.
    - **Structured Layer**: Bar charts showing file/note distribution.
    - **Semantic Layer**: Scatter plot visualizing concept embeddings.
    - **Associative Layer**: Animated neural network graph showing node relationships.
- **Gmail & Calendar**: Dedicated views for emails and events.
- **Active Agent Indicator**: Live indicator showing the system's "brain" at work (Analyzing, Cloud Thinking, Tool Execution).
- **Quick Actions**: Buttons for instant access to Morning Briefing and Calendar.
- **Copy/Paste Support**: Right-click on chat bubbles to copy text, or use full context menu in the input field.

---

## 🏗️ البنية المعمارية | Architecture

### 📊 تدفق النظام | System Flow

```
┌───────────────┐      ┌──────────────────┐
│  Electron UI  │ ◄──► │   FastAPI API    │
│ (React/Vite)  │      │ (Python Server)  │
└───────┬───────┘      └────────┬─────────┘
        │                       │
        ▼                       ▼
┌───────────────┐      ┌──────────────────┐
│  User Voice   │      │ System Awareness │
│               │      │ (Profile/Index)  │
└───────┬───────┘      └────────┬─────────┘
        │                       │
        ▼                       │
┌───────────────┐               │
│ Unified STT   │ ◄─────────────┘
│(Google/Whisper)│
└───────┬───────┘
        ▼
┌───────────────┐
│ Intent Router │
│ (Rule-based)  │
└───────┬───────┘
        ▼
┌───────────────┐
│  LLM Routing  │
│(Ollama/LLM/Model)│
└───────┬───────┘
        ▼
┌───────────────┐
│  Dispatcher   │
│ (Tool Execution)│
└───────┬───────┘
        ▼
┌───────────────────────────────────────────────┐
│                    Tools Layer                │
├───────────────────────────────────────────────┤
│ Secretary │ Advisor │ Files │ Gmail │ Terminal │
│           │         │       │       │          │
└───────────┴────┬────┴───────┴───────┴──────────┘
                 │
                 ▼
┌───────────────────────────────────────────────┐
│               Living Memory Layer             │
│        (Graph ◀─── Manager ───▶ Vector/SQL)   │
└───────────────────────────────────────────────┘
```

### 🗂️ هيكل المشروع | Project Structure

```
haitham_voice_agent/
├── api/                         # 🆕 FastAPI Backend
│   ├── main.py                  # API Entry Point (WebSocket + REST)
│   └── routes/                  # API Routes (Voice, Memory, Gmail, etc.)
├── desktop/                     # 🆕 Electron + React Frontend
│   ├── src/                     # React Components (Dashboard, Sidebar, etc.)
│   ├── main.js                  # Electron Main Process
│   └── package.json             # Build & Packaging Config
├── haitham_voice_agent/         # Core Logic
│   ├── dispatcher.py            # Task Dispatcher
│   ├── memory/                  # Living Memory System
│   └── tools/                   # Tools (Gmail, Calendar, etc.)
├── run_app.py                   # Unified Launcher (Dev Mode)
└── requirements.txt             # Python Dependencies
```

---

## 🚀 التشغيل (Startup)

<div dir="rtl">

الطريقة المعتمدة لتشغيل النظام هي تشغيل الخادم يدوياً ثم فتح التطبيق.

1.  **تشغيل الخادم (Backend)**:
    افتح التيرمينال في مجلد المشروع ونفذ الملف التالي:
    ```bash
    ./start_hva.sh
    ```
    *سيقوم هذا السكربت بتفعيل البيئة الافتراضية وتشغيل الخادم.*

2.  **تشغيل التطبيق (Frontend)**:
    بمجرد أن يعمل الخادم، افتح تطبيق **HVA Premium** من سطح المكتب.

</div>

## 🛠️ التثبيت (لأول مرة فقط) | Installation

<div dir="rtl">

1.  **تجهيز البيئة**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **إعداد الملفات**:
    تأكد من وجود ملف `.env` وملفات `client_secret.json` في المجلد الرئيسي.

</div>

---

## 📚 الوحدات والأدوات | Modules & Tools

A high-level overview of the key components in the HVA ecosystem:

| Module / Tool             | Description                                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Core Orchestration**    | `dispatcher.py`: Handles the main application loop and routes tasks to the correct tools.               |
| **Backend API**           | `api/`: FastAPI server exposing HVA capabilities via REST and WebSockets (Port 8765, Bound to 0.0.0.0). |
| **Frontend GUI**          | `desktop/`: Modern Electron + React application for a premium user experience (Connects via localhost). |


---

## 🔧 استكشاف الأخطاء (Troubleshooting)

### Common Issues

1.  **Failed to Fetch / Network Error**:
    *   **Cause**: The frontend cannot connect to the backend.
    *   **Solution**: Ensure the backend is running. If using the packaged app, check that `hva_backend` is listening on port 8765 (`lsof -i :8765`). Ensure you are using the latest version with `0.0.0.0` binding.

2.  **Permission Denied (Microphone/Network)**:
    *   **Cause**: macOS security restrictions (Hardened Runtime).
    *   **Solution**: The app must be signed with correct entitlements (`com.apple.security.network.client`, `device.audio-input`). Re-download the latest release or rebuild with `npm run package`.

3.  **App Crashes on Launch**:
    *   **Cause**: Backend failed to spawn or path issue.
    *   **Solution**: Check `/tmp/hva_backend.log` for errors. Ensure the `hva_backend` executable is correctly placed in `Contents/Resources`.
| **Unified Voice Engine**  | `tools/voice/`: Manages all Speech-to-Text (STT) and Text-to-Speech (TTS) operations.                    |
| **System Awareness**      | `tools/system_awareness/`: Discovers and indexes files, apps, and system specifications.                |

---

## 🛠️ أدوات المطور | Developer Toolkit

<div dir="rtl">

يحتوي HVA على مجموعة أدوات مدمجة للمطورين لتسهيل عملية التطوير وتصحيح الأخطاء:

*   **Network Monitor**: مراقبة حية لجميع طلبات API وتفاصيلها (Request/Response).
*   **Smart Diagnostics**: تحليل ذكي للأخطاء مع تحديد الملف والسطر (Source Location) واقتراح الحلول.
*   **State Inspector**: مراقبة حالة WebSocket والذاكرة في الوقت الفعلي.
*   **Debug Export**: تصدير تقرير شامل عن حالة النظام والسجلات بضغطة زر.

[📄 اقرأ الدليل الكامل لأدوات المطور (DEVELOPER_TOOLKIT.md)](DEVELOPER_TOOLKIT.md)

</div>

HVA includes a built-in Developer Toolkit to streamline development and debugging:

*   **Network Monitor**: Live monitoring of all API requests and details.
*   **Smart Diagnostics**: Intelligent error analysis with source location (File/Line) and solution recommendations.
*   **State Inspector**: Real-time monitoring of WebSocket status and memory.
*   **Debug Export**: One-click export of a comprehensive system state and log report.

[📄 Read the full Developer Toolkit Guide (DEVELOPER_TOOLKIT.md)](DEVELOPER_TOOLKIT.md)

---

## 🔒 نظام الأمان | Safety System

<div dir="rtl">

تم تعزيز المشروع بنظام أمان متقدم:

*   **🚦 Traffic Light Terminal**:
    *   **🟢 أخضر**: أوامر آمنة (`ls`, `pwd`) تنفذ فوراً.
    *   **🟡 أصفر**: أوامر مقيدة (`git`, `pip`) تطلب تأكيداً.
    *   **🔴 أحمر**: أوامر خطرة (`rm -rf`, `sudo`) محظورة تماماً.
*   **🏖️ Smart User Sandbox**:
    *   يمنع الوصول لأي ملف خارج مجلد المستخدم (`~/`).
    *   يحظر المجلدات الحساسة (`.ssh`, `Library`) حتى داخل مجلد المستخدم.
*   **🔐 Secure Credential Store**:
    *   يستخدم **macOS Keychain** لتخزين بيانات اعتماد Google API بشكل آمن.

</div>

The project is fortified with an advanced security system:

*   **🚦 Traffic Light Terminal**:
    *   **🟢 Green**: Safe, read-only commands (`ls`, `pwd`) execute immediately.
    *   **🟡 Yellow**: Restricted commands with side-effects (`git`, `pip`) require confirmation.
    *   **🔴 Red**: Dangerous commands (`rm -rf`, `sudo`) are strictly blocked.
*   **🏖️ Smart User Sandbox**:
    *   Blocks file access outside the user's home directory (`~/`).
    *   Blacklists sensitive folders (`.ssh`, `Library`) even within the home directory.
*   **🔐 Secure Credential Store**:
    *   Uses **macOS Keychain** to securely store Google API credentials.
*   **🛡️ Action Confirmation (New)**:
    *   **Destructive Actions**: Operations like moving, deleting, or renaming files now trigger a **Confirmation UI**.
    *   **Approve/Reject**: You must explicitly click "Approve" (موافق) or "Reject" (إلغاء) to proceed.
    *   **Direct Execution**: Once approved, the system executes the command directly with a high-priority flag.

### 🧠 Advanced Memory & Organization (v2.2)

<div dir="rtl">

*   **Project Registry**: نظام مركزي لإدارة المشاريع (`projects.json`) يمنع تشتت الملفات.
*   **Graph Store**: قاعدة بيانات علاقات (Graph Database) تربط الملفات بالمشاريع والمفاهيم (مثل "الملف A" جزء من "المشروع B").
*   **Smart Content Extraction**: استخراج ذكي للنصوص من ملفات PDF و Code و Text.
*   **Hybrid Summarization**: استخدام **Qwen 2.5 (3B)** (محلياً) لتلخيص الملفات بسرعة فائقة (1.2 ثانية)، مع الانتقال تلقائياً لـ **Gemini Flash** للملفات المعقدة.
*   **Deep Search**: بحث دلالي (Semantic Search) داخل محتوى الملفات وليس فقط العناوين.
*   **Auto-Indexing**: عند نقل ملف إلى مشروع، يتم فهرسته، تلخيصه، وربطه بالرسم البياني (Graph) تلقائياً.

</div>

*   **Project Registry**: A centralized system (`projects.json`) to manage projects and prevent file scatter.
*   **Graph Store**: A relationship database linking files to projects and concepts (e.g., "File A" belongs to "Project B").
*   **Smart Content Extraction**: Intelligent text extraction from PDF, Code, and Text files.
*   **Hybrid Summarization**: Uses **Qwen 2.5 (3B)** (locally) for blazing fast summaries (1.2s), auto-falling back to **Gemini Flash** for complex files.
*   **Deep Search**: Semantic search within file content, not just filenames.
*   **Auto-Indexing**: Moving a file to a project automatically indexes, summarizes, and links it to the Knowledge Graph.

### 🧠 Intelligent Memory & Organization
- **Deep Organization**: AI-powered analysis to rename and categorize files based on content.
- **Simple Organization (Free)**: Rule-based organization by file type (Images, Docs, etc.) with zero cost.
- **Safety Layer**: `OptimizationGuard` prevents re-analyzing unchanged files, ensuring $0.00 cost for duplicate runs.
- **Vector Memory**: Semantic search for all your notes and documents.
- **Graph Database**: Tracks relationships between files, projects, and concepts.

### 💰 Cost Transparency
- **Real-time Tracking**: See exact costs for every operation.
- **Detailed Breakdown**: View separate costs for Gemini (Analysis) and GPT (Reasoning).
- **Budget Safety**: System alerts or blocks redundant expensive operations.

---

## 🚀 التثبيت والإعداد | Installation & Setup

### المتطلبات | Prerequisites
- macOS (Apple Silicon recommended)
- Python 3.11+
- Node.js & npm (for Frontend)
- API Keys: OpenAI, Gemini, Google Cloud (STT/Gmail/Calendar/Drive)

### التثبيت | Installation

```bash
# 1. Clone the repository
git clone <repo_url>
cd haitham-voice-agent

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Frontend dependencies
cd desktop
npm install
cd ..

# 5. Configure environment variables
cp .env.example .env
# Edit the .env file with your API keys
```

---

## 💡 الاستخدام | Usage

### التشغيل | Running

**1. Desktop App (Recommended for Daily Use):**
Run the packaged application:
`desktop/dist/mac-arm64/HVA Premium.app`

**2. Development Mode (For Developers):**
To run the application with hot-reloading and see logs:

```bash
python run_app.py
```

### بناء النسخة النهائية | Production Build

To build the standalone `.app` file (includes both Backend and Frontend):

```bash
cd desktop
npm run package
```

The output application will be located at:
`desktop/dist/mac-arm64/HVA Premium.app`

<div dir="rtl">

*   **"صباح الخير"** (يقدم موجزاً صباحياً مخصصاً من الذاكرة والتقويم).
*   **"احفظ ملاحظة: فكرة المشروع الجديد هي بناء نظام ذكاء اصطناعي"** (يستخدم السكرتير لحفظ الملاحظة في الذاكرة).
*   **"ما هي مهامي لهذا اليوم؟"** (يستعلم من السكرتير عن المهام المفتوحة).
*   **"هل تعتقد أن حذف جميع الملفات الموجودة على سطح المكتب فكرة جيدة؟"** (يسأل المستشار الذي سيرفض الإجراء).
*   **"لخص آخر بريد إلكتروني من المدير"** (يستخدم تكامل Gmail المتقدم مع Gemini).
*   **"ما هي مواعيدي اليوم؟"** (يستخدم تكامل تقويم Google).
*   **"ابحث في درايف عن ملف العقد"** (يستخدم تكامل Google Drive).
*   **"نظف مجلد التنزيلات"** (يستخدم المنظم الذكي لتصنيف الملفات).
*   **"وضع الاجتماع"** (يكتم الصوت ويرسل تنبيهاً).
*   **"وضع العمل"** (يضبط مستوى الصوت للمساعدة على التركيز).
*   **"نفذ أمر git status"** (يستخدم الطرفية الآمنة بعد طلب التأكيد).

</div>

*   **"Good morning"** (Gives a personalized morning brief from memory and calendar).
*   **"Save a note: the new project idea is to build an AI system"** (Uses the Secretary to save a note to memory).
*   **"What are my tasks for today?"** (Queries the Secretary for open tasks).
*   **"Do you think deleting all files on the desktop is a good idea?"** (Asks the Advisor, who will reject the action).
*   **"Summarize the last email from my manager"** (Uses the advanced Gmail integration with Gemini).
*   **"What are my events today?"** (Uses Calendar Integration).
*   **"Search Drive for the contract file"** (Uses Drive Integration).
*   **"Clean up my downloads folder"** (Uses the Smart Organizer to categorize files).
*   **"Run the command git status"** (Uses the Secure Terminal after requesting confirmation).
*   **"Remind me"** -> System: "About what?" -> **"To call Ahmed"** (Clarification Agent).
*   **"I have an idea for a new cooking app"** (Idea Agent creates a structured project).
*   **"Hey Siri, add 'Buy milk' to HVA Inbox"** (iPhone Sync -> HVA Memory).
*   **"Show files in Downloads"** (Smart File Listing with date categorization).
*   **"Am I free tomorrow?"** (Smart Calendar availability check).
*   **"Schedule a meeting with John next Monday at 5pm"** (Smart Calendar natural language scheduling).
*   **"Meeting Mode"** (Mutes volume and enables DND for meetings).
*   **"Work Mode"** (Sets volume to low for focus).

---

<div align="center">

**Made with ❤️ by Haitham**

🎤 **Voice-Powered • 🧠 System-Aware • 🔒 Privacy-First**

</div>