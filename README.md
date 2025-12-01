Of course. As an expert technical writer for the Haitham Voice Agent project, I will update the README.md to accurately reflect the current state of the codebase.

Here is the full, updated `README.md` content:

# Haitham Voice Agent (HVA) 🎤🤖

<div dir="rtl">

**وكيل صوتي ذكي لنظام macOS مع توجيه هجين للذكاء الاصطناعي، ذاكرة حية، وعي كامل بالنظام، وتكامل عميق مع خدمات Google.**

</div>

A voice-operated automation agent for macOS with hybrid LLM routing, a living memory system, full system awareness, and deep Google Suite integration.

> [!NOTE]
> **Status: Production Ready** 🚀
> The system has undergone a major architectural refactoring to ensure stability, deterministic routing, and a unified, state-aware memory system.

---

## 📋 جدول المحتويات | Table of Contents

- [نظرة عامة | Overview](#-نظرة-عامة--overview)
- [المميزات الرئيسية | Key Features](#-المميزات-الرئيسية--key-features)
- [البنية المعمارية | Architecture](#-البنية-المعمارية--architecture)
- [الوحدات والأدوات | Modules & Tools](#-الوحدات-والأدوات--modules--tools)
- [نظام الأمان | Safety System](#-نظام-الأمان--safety-system)
- [التثبيت والإعداد | Installation & Setup](#-التثبيت-والإعداد--installation--setup)
- [الاستخدام | Usage](#-الاستخدام--usage)
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
- **Smart Organizer**: Tools to automatically clean the Desktop and organize the Downloads folder.
- **Workspace Manager**: Automatically creates and manages project folder structures.

### 🤖 ترقيات الذكاء (v1.1 - v1.7) | Intelligence Upgrades
<div dir="rtl">

- **Smart Feedback Agent**: نظام "نكز" ذكي في الموجز الصباحي يذكرك بالمشاريع المتوقفة باحترام وتدرج.
- **Clarification Agent**: لا يفشل عند الغموض! يستخدم حلقة ذكية (Robust Loop) للتوضيح حتى 3 محاولات. إذا قلت "ذكرني"، سيسألك "بماذا؟" ويسمع إجابتك.
- **Idea Agent**: حول أفكارك الخام إلى مشاريع منظمة. قل "عندي فكرة..." وسيقوم بإنشاء خطة مشروع كاملة (باستخدام **GPT-5 Mini** للسرعة والتكلفة).
- **iPhone Sync**: اربط هاتفك بالوكيل! قل لـ Siri: "Add task to HVA Inbox" وسيظهر في ذاكرة HVA فوراً.
- **Smart Calendar**: فهم كامل للوقت ("غداً"، "الاثنين القادم") وفحص ذكي للتوفر ("هل أنا مشغول؟").
- **Premium GUI**: واجهة فخمة (Dark Mode) مع مؤشر ذكاء حي يظهر من يفكر الآن (Ollama vs GPT).
- **Timezone-Aware Scheduling**: يفهم "اجتماع الساعة 5 بتوقيت القاهرة" ويحسب فرق التوقيت تلقائياً ليحجز الموعد الصحيح.

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

### 📱 تطبيق شريط القوائم وواجهة المستخدم | Menu Bar App & GUI

<div dir="rtl">

- **اختصار عالمي**: `⌘⇧H` (Cmd+Shift+H) لبدء الاستماع من أي مكان.
- **Premium Dashboard**: لوحة تحكم تعرض حالة النظام، الطقس، والمهام.
- **Active Agent Indicator**: مؤشر حي يظهر لك "عقل" النظام وهو يعمل (تحليل، تفكير سحابي، تنفيذ أدوات).
- **إجراءات سريعة**: أزرار للوصول السريع للموجز الصباحي والتقويم.

</div>

- **Global Hotkey**: `⌘⇧H` (Cmd+Shift+H) to start listening from anywhere.
- **Premium Dashboard**: Displays system status, weather, and tasks.
- **Active Agent Indicator**: Live indicator showing the system's "brain" at work (Analyzing, Cloud Thinking, Tool Execution).
- **Quick Actions**: Buttons for instant access to Morning Briefing and Calendar.
- **Copy/Paste Support**: Right-click on chat bubbles to copy text, or use full context menu in the input field.

---

## 🏗️ البنية المعمارية | Architecture

### 📊 تدفق النظام | System Flow

```
┌───────────────┐
│  User Voice   │
└───────┬───────┘
        ▼
┌───────────────┐      ┌──────────────────┐
│ Unified STT   │ ───► │ System Awareness │
│(Google/Whisper)│      │ (Profile/Index)  │
└───────┬───────┘      └────────┬─────────┘
        │                       │
        ▼                       │
┌───────────────┐               │
│ Intent Router │◄──────────────┘
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
├── main.py                      # نقطة الدخول الرئيسية (CLI)
├── hva_menubar.py               # 📱 تطبيق شريط القوائم (مشغل الواجهة)
├── gui_process.py               # 🖥️ عملية نافذة الواجهة الرئيسية
│
├── ⚙️ config.py                  # الإعدادات المركزية
├── dispatcher.py                # موزع المهام والأدوات
│
├── intent_router.py             # 1. موجه الأوامر الحتمي (عربي)
├── ollama_orchestrator.py       # 2. منسق النماذج (محلي/سحابي)
├── llm_router.py                # 3. موجه LLM الهجين (GPT/Gemini)
└── model_router.py              # 4. موجه النموذج الحتمي (جودة/تكلفة)
│
├── 💾 memory/                     # --- نظام الذاكرة الحية ---
│   ├── manager.py               # المدير الموحد للذاكرة
│   ├── graph_store.py           # مخزن الرسم البياني (علاقات)
│   └── vector_store.py          # مخزن المتجهات (بحث دلالي)
│
├── 🛠️ tools/                     # --- الأدوات والقدرات الأساسية ---
│   ├── secretary.py             # السكرتير التنفيذي (مهام، ملاحظات)
│   ├── advisor.py               # المستشار النزيه (رؤى، تحقق)
│   ├── files.py                 # عمليات ملفات آمنة (Sandbox)
│   ├── terminal.py              # طرفية آمنة (Traffic Light)
│   ├── smart_organizer.py       # منظم الملفات الذكي
│   │
│   ├── 🎤 voice/                # وحدة الصوت الموحدة
│   │   └── stt.py               #   معالج STT الموحد (القاعدة الذهبية)
│   │
│   ├── 📧 gmail/                 # وحدة Gmail المتقدمة
│   │   ├── connection_manager.py#   مدير اتصال ذكي (API/IMAP)
│   │   └── auth/                #   مصادقة آمنة (OAuth/Keychain)
│   │
│   └── 🌐 system_awareness/     # وحدة الوعي بالنظام
│
└── 🧪 tests/                     # الاختبارات الوحدوية والتكاملية
```

---

## 📚 الوحدات والأدوات | Modules & Tools

A high-level overview of the key components in the HVA ecosystem:

| Module / Tool             | Description                                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Core Orchestration**    | `main.py`, `dispatcher.py`: Handles the main application loop and routes tasks to the correct tools.      |
| **Intelligence & Routing**| `intent_router.py`, `llm_router.py`, `model_router.py`: The 4-layer system for smart, deterministic routing. |
| **Living Memory**         | `memory/`: The unified brain (Graph, Vector, SQL) for storing and retrieving contextual information.      |
| **Executive Secretary**   | `tools/secretary.py`: Manages notes, tasks, and projects, integrating deeply with the memory system.    |
| **Honest Advisor**        | `tools/advisor.py`: Provides insights, validates actions, and ensures system wellbeing.                 |
| **Secure System Tools**   | `tools/files.py`, `tools/terminal.py`: Safe file and command-line operations with sandbox security.       |
| **Google Suite**          | `tools/gmail/`, `calendar.py`, `drive.py`: Deep integration with Google services.                         |
| **Unified Voice Engine**  | `tools/voice/`: Manages all Speech-to-Text (STT) and Text-to-Speech (TTS) operations.                    |
| **System Awareness**      | `tools/system_awareness/`: Discovers and indexes files, apps, and system specifications.                |
| **GUI System**            | `hva_menubar.py`, `gui_process.py`: Provides the user-facing menu bar app and dashboard.                  |

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

---

## 🚀 التثبيت والإعداد | Installation & Setup

### المتطلبات | Prerequisites
- macOS (Apple Silicon recommended)
- Python 3.11+
- API Keys: OpenAI, Gemini, Google Cloud (STT/Gmail/Calendar/Drive)

### التثبيت | Installation

```bash
# 1. Clone the repository
git clone <repo_url>
cd haitham-voice-agent

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit the .env file with your API keys
```

---

## 💡 الاستخدام | Usage

### التشغيل | Running

**Desktop Launcher (Recommended):**
Double-click the **HVA Premium.app** on your Desktop.

**Alternative (Terminal):**
```bash
# Run the HVA Menu Bar App
python -m haitham_voice_agent.hva_menubar
```
Click the icon in your menu bar or use the global hotkey `Cmd+Shift+H` to start listening.

### أوامر صوتية للتجربة | Voice Commands to Try

<div dir="rtl">

*   **"صباح الخير"** (يقدم موجزاً صباحياً مخصصاً من الذاكرة والتقويم).
*   **"احفظ ملاحظة: فكرة المشروع الجديد هي بناء نظام ذكاء اصطناعي"** (يستخدم السكرتير لحفظ الملاحظة في الذاكرة).
*   **"ما هي مهامي لهذا اليوم؟"** (يستعلم من السكرتير عن المهام المفتوحة).
*   **"هل تعتقد أن حذف جميع الملفات الموجودة على سطح المكتب فكرة جيدة؟"** (يسأل المستشار الذي سيرفض الإجراء).
*   **"لخص آخر بريد إلكتروني من المدير"** (يستخدم تكامل Gmail المتقدم مع Gemini).
*   **"ما هي مواعيدي اليوم؟"** (يستخدم تكامل تقويم Google).
*   **"ابحث في درايف عن ملف العقد"** (يستخدم تكامل Google Drive).
*   **"نظف مجلد التنزيلات"** (يستخدم المنظم الذكي لتصنيف الملفات).
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

---

<div align="center">

**Made with ❤️ by Haitham**

🎤 **Voice-Powered • 🧠 System-Aware • 🔒 Privacy-First**

</div>