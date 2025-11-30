# Haitham Voice Agent (HVA) 🎤🤖

<div dir="rtl">

**وكيل صوتي ذكي لنظام macOS مع توجيه هجين للذكاء الاصطناعي، تكامل Gmail، ونظام ذاكرة متقدم**

</div>

A voice-operated automation agent for macOS with hybrid LLM routing, Gmail integration, and an advanced memory system.

---

## 📋 جدول المحتويات | Table of Contents

- [نظرة عامة | Overview](#-نظرة-عامة--overview)
- [المميزات الرئيسية | Key Features](#-المميزات-الرئيسية--key-features)
- [البنية المعمارية | Architecture](#-البنية-المعمارية--architecture)
- [التثبيت والإعداد | Installation & Setup](#-التثبيت-والإعداد--installation--setup)
- [الاستخدام | Usage](#-الاستخدام--usage)
- [الوحدات والأدوات | Modules & Tools](#-الوحدات-والأدوات--modules--tools)
- [التكوين | Configuration](#-التكوين--configuration)
- [الاختبارات | Testing](#-الاختبارات--testing)
- [استكشاف الأخطاء | Troubleshooting](#-استكشاف-الأخطاء--troubleshooting)
- [التوثيق التقني | Technical Documentation](#-التوثيق-التقني--technical-documentation)
- [الأمان | Security](#-الأمان--security)
- [المساهمة | Contributing](#-المساهمة--contributing)

---

## 🌟 نظرة عامة | Overview

<div dir="rtl">

**Haitham Voice Agent (HVA)** هو وكيل صوتي ذكي مصمم خصيصاً لنظام macOS، يجمع بين قوة الذكاء الاصطناعي المتقدم والتحكم الصوتي الطبيعي. يدعم النظام اللغتين العربية والإنجليزية، ويستخدم استراتيجية توجيه هجينة بين نماذج Gemini و GPT لتحقيق أفضل أداء لكل مهمة.

</div>

**Haitham Voice Agent (HVA)** is an intelligent voice-operated automation agent designed specifically for macOS. It combines the power of advanced AI with natural voice control, supporting both Arabic and English languages. The system uses a hybrid routing strategy between Gemini and GPT models to achieve optimal performance for each task.

### 🎯 الأهداف الأساسية | Core Objectives

- ✅ **Voice-to-Action Automation**: تحويل الأوامر الصوتية إلى إجراءات تلقائية
- ✅ **Hybrid LLM Intelligence**: توجيه ذكي بين نماذج الذكاء الاصطناعي
- ✅ **Structured Execution Plans**: خطط تنفيذ منظمة مع تأكيد المستخدم
- ✅ **Persistent Memory System**: نظام ذاكرة دائم مع بحث دلالي ورسم بياني للمعرفة
- ✅ **Full Gmail Integration**: قراءة، تلخيص، وإنشاء مسودات البريد الإلكتروني
- ✅ **Safe macOS Automation**: أتمتة آمنة لنظام macOS

---

## ✨ المميزات الرئيسية | Key Features

### 📱 تطبيق شريط القوائم | Menu Bar App

<div dir="rtl">

- **اختصار عالمي**: `⌘⇧H` (Cmd+Shift+H) للاستماع من أي مكان في النظام.
- **عمل في الخلفية**: يعمل بسلاسة في الخلفية دون الحاجة لنافذة Terminal.
- **قائمة سريعة**: وصول سريع لجميع الوظائف الأساسية (بدء/إيقاف، عرض النافذة، إعادة الضبط).
- **إشعارات النظام**: إشعارات macOS عند اكتمال المهام الطويلة.
- **تكامل مع الواجهة الرسومية**: يعرض النتائج تلقائياً في نافذة تفاعلية.

</div>

- **Global Hotkey**: `⌘⇧H` (Cmd+Shift+H) to listen from anywhere in the OS.
- **Background Operation**: Runs seamlessly in the background with no required Terminal window.
- **Quick Menu**: Fast access to all core functions (Toggle On/Off, Show Window, Reset).
- **System Notifications**: macOS notifications when long-running tasks complete.
- **GUI Integration**: Automatically displays results in an interactive window.

### 🖥️ الواجهة الرسومية التفاعلية | Interactive GUI

<div dir="rtl">

- **نافذة ذكية**: واجهة رسومية حديثة مبنية بـ PyQt مع تصميم glassmorphism.
- **نظام التبويبات**:
  - **📊 لوحة التحكم**: عرض فوري لحالة النظام، الطقس، وسجل المحادثة.
  - **📁 الملفات**: وصول سريع للملفات والمشاريع الحديثة (اضغط للفتح).
  - **⚙️ الإعدادات**: التحكم في الصوت، الوضع الليلي، والإغلاق التلقائي للنافذة.
- **مؤشر نبضي**: رسوم متحركة تفاعلية أثناء الاستماع والمعالجة لتقديم ملاحظات مرئية.
- **روابط قابلة للنقر**: فتح مسارات الملفات والروابط مباشرة من نافذة المحادثة.
- **إدخال يدوي**: إمكانية كتابة الأوامر مباشرة في النافذة كبديل للصوت.
- **تثبيت النافذة**: خيار لإبقاء النافذة مفتوحة بشكل دائم.

</div>

- **Smart Window**: Modern GUI built with PyQt featuring a glassmorphism design.
- **Tabbed Interface**:
  - **📊 Dashboard**: At-a-glance view of system status, weather, and chat history.
  - **📁 Files**: Quick access to recent files and projects (Click to open).
  - **⚙️ Settings**: Toggle TTS, Dark Mode, and Window Auto-close.
- **Pulse Indicator**: Interactive animations during listening and processing for visual feedback.
- **Clickable Links**: Open file paths and URLs directly from the chat window.
- **Manual Input**: Ability to type commands directly into the window as an alternative to voice.
- **Pin Window**: Option to keep the window persistently open.

### 🎤 نظام التحكم الصوتي | Voice Control System

<div dir="rtl">

- **كلمة الإيقاظ**: يبدأ الاستماع بعد اكتشاف "هيثم" أو "Haitham".
- **تحويل الكلام إلى نص (STT)**: استراتيجية هجينة محسّنة للدقة والتكلفة:
  - **للأوامر القصيرة التفاعلية:** Google Cloud Speech-to-Text (دقة عالية في العربية).
  - **للتسجيلات الطويلة (اجتماعات، ملاحظات):** Whisper `large-v3` يعمل محلياً (دقة ممتازة للجلسات).
  - دعم كامل للعربية (ar-SA) والإنجليزية (en-US) مع كشف تلقائي للغة.
- **تحويل النص إلى كلام (TTS)**: استخدام نظام macOS المدمج للاستجابة السريعة:
  - صوت "Majed" للعربية.
  - أصوات "Samantha/Alex" للإنجليزية.
  - استجابة صوتية تلقائية بنفس لغة الأمر المكتشفة.

</div>

- **Wake Word Detection**: Starts listening upon detecting "هيثم" or "Haitham".
- **Speech-to-Text (STT)**: Optimized hybrid strategy for accuracy and cost:
  - **For short, interactive commands:** Google Cloud Speech-to-Text (high accuracy for Arabic).
  - **For long sessions (meetings, notes):** Local Whisper `large-v3` (excellent accuracy for sessions).
  - Full support for Arabic (ar-SA) and English (en-US) with automatic language detection.
- **Text-to-Speech (TTS)**: Utilizes the native macOS system for fast responses:
  - "Majed" voice for Arabic.
  - "Samantha/Alex" voices for English.
  - Automatically responds in the detected language of the command.

### 🤖 التوجيه الهجين للذكاء الاصطناعي | Hybrid LLM Routing

<div dir="rtl">

يستخدم النظام استراتيجية توجيه ذكية ومتعددة الطبقات لاختيار النموذج الأنسب لكل مهمة، مع إعطاء الأولوية للجودة ثم التكلفة.

</div>

The system uses an intelligent, multi-layered routing strategy to select the optimal model for each task, prioritizing quality first, then cost.

- **الطبقة الأولى: موجه النوايا (`intent_router.py`)**: يتعامل مع الأوامر الشائعة والمحددة (مثل "احفظ ملاحظة") بشكل حتمي لتجاوز LLM تمامًا، مما يضمن سرعة وموثوقية 100%.
- **الطبقة الثانية: موجه LLM (`llm_router.py`)**: يختار بين عائلات النماذج (Gemini مقابل GPT) بناءً على نقاط القوة الأساسية:
  - **🔷 Gemini**: للتحليل، التلخيص، الترجمة، ومعالجة المستندات (PDF، صور).
  - **🔶 GPT**: لإنشاء خطط التنفيذ، استدعاء الأدوات (JSON)، وعمليات الذاكرة.
- **الطبقة الثالثة: موجه النموذج (`model_router.py`)**: يختار النموذج المحدد داخل العائلة (مثل GPT-4o-mini مقابل GPT-4o) بناءً على بيانات وصفية للمهمة (مثل المخاطرة، التعقيد) لتحسين التكلفة.

### 🧠 نظام الذاكرة الحي | Living Memory System

<div dir="rtl">

نظام ذاكرة متطور يحفظ المعرفة بشكل دائم عبر ثلاث طبقات متكاملة.

</div>

An advanced memory system that persistently stores knowledge across three integrated layers.

1.  **الطبقة الأولى: مساحة العمل المنظمة (Structured Workspace)**:
    -   باستخدام `workspace_manager.py`، يتم تخزين المشاريع والملاحظات والأفكار في بنية مجلدات منظمة على القرص (`~/HVA_Memory`). يوفر أساسًا ملموسًا ومنظمًا.

2.  **الطبقة الثانية: الذاكرة المتجهة (Vector RAG)**:
    -   باستخدام `ChromaDB` (`memory/vector_store.py`)، يتم تضمين جميع الملاحظات وتخزينها للبحث الدلالي. يسمح بطرح أسئلة مثل "ماذا قلت عن مشروع X؟" وفهم المعنى بدلاً من الكلمات الرئيسية.

3.  **الطبقة الثالثة: الرسم البياني للمعرفة (Knowledge Graph)**:
    -   باستخدام `NetworkX` (`memory/graph_store.py`)، يربط النظام الكيانات (المشاريع، الأشخاص، المفاهيم) معًا. يبني تلقائيًا شبكة من العلاقات، مما يسمح باستعلامات معقدة مثل "أرني جميع الملاحظات المتعلقة بأحمد في مشروع HVA".

### 👔 السكرتير التنفيذي | Executive Secretary

<div dir="rtl">

- **الموجز الصباحي**: عند سماع "صباح الخير"، يقدم تقريرًا يوميًا ذكيًا يشمل الطقس، المهام المعلقة، أحداث التقويم، وحالة النظام.
- **أوضاع العمل**:
  - **Work**: يفتح VS Code, iTerm ويضبط الصوت على 40%.
  - **Meeting**: يفتح تطبيق الملاحظات ويضبط الصوت على 80%.
  - **Chill**: يفتح Spotify ويضبط الصوت على 60%.

</div>

- **Morning Briefing**: Upon hearing "Good morning," provides a smart daily report including weather, pending tasks, calendar events, and system status.
- **Work Modes**:
  - **Work**: Opens VS Code, iTerm, and sets volume to 40%.
  - **Meeting**: Opens the Notes app and sets volume to 80%.
  - **Chill**: Opens Spotify and sets volume to 60%.

### 🛡️ الناصح الأمين | Honest Advisor

<div dir="rtl">

- **شبكة الأمان**: يمنع الإجراءات المدمرة مثل حذف المجلدات المهمة (المستندات، سطح المكتب) عن طريق اعتراض الخطة والتحذير.
- **الصحة الرقمية**: يرسل تنبيهات لطيفة لأخذ استراحة بعد فترات طويلة من العمل المتواصل (على سبيل المثال، ساعتان، 4 ساعات).
- **مراقب الموارد**: يطلق تنبيهًا عند اكتشاف استهلاك مرتفع ومستمر لوحدة المعالجة المركزية (CPU) أو الذاكرة (RAM).

</div>

- **Safety Net**: Prevents destructive actions like deleting critical folders (Documents, Desktop) by intercepting the plan and providing a warning.
- **Digital Wellbeing**: Sends gentle reminders to take a break after long periods of continuous work (e.g., 2h, 4h).
- **Resource Monitor**: Issues an alert upon detecting sustained high CPU or RAM usage.

### 📧 تكامل Gmail الكامل | Full Gmail Integration

<div dir="rtl">

- **اتصال ذكي**: يبدل تلقائيًا بين Gmail API (المفضل) و IMAP/SMTP (الاحتياطي) لضمان الموثوقية.
- **القراءة**: جلب آخر الرسائل، البحث المتقدم، وقراءة المحادثات الكاملة.
- **الكتابة**: إنشاء مسودات، الرد على الرسائل، وإعادة توجيهها.
- **ذكاء LLM**: تلخيص الرسائل، استخراج المهام، وتصنيف البريد تلقائيًا باستخدام Gemini و GPT.
- **أمان OAuth 2.0**: يستخدم تدفق مصادقة آمن مع تخزين بيانات الاعتماد المشفرة في macOS Keychain.
- **وضع المسودات فقط**: لا يرسل أي بريد إلكتروني مباشرة أبدًا؛ يتم إنشاؤه كمسودة ليقوم المستخدم بمراجعته وإرساله.

</div>

- **Smart Connection**: Auto-switches between the Gmail API (preferred) and IMAP/SMTP (fallback) for reliability.
- **Reading**: Fetch latest emails, advanced search, and read full threads.
- **Writing**: Create drafts, reply to messages, and forward them.
- **LLM Intelligence**: Summarize, extract tasks, and categorize emails automatically using Gemini and GPT.
- **OAuth 2.0 Security**: Uses a secure authentication flow with encrypted credentials stored in the macOS Keychain.
- **Drafts-Only Mode**: Never sends an email directly; always creates a draft for user review and sending.

---

## 🏗️ البنية المعمارية | Architecture

### 📊 تدفق النظام | System Flow

```
┌─────────────────┐
│  User Voice     │
│  (Via Hotkey)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Wake Word Detect│
│  "هيثم/Haitham" │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ STT Router      │
│ (Google/Whisper)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Intent Router   │
│ (Deterministic) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Router     │
│ (Gemini vs GPT) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execution Plan  │
│  (User Confirm) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dispatcher    │
│    الموزع       │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│               Tools Layer                │
├──────────────────────────────────────────┤
│ Files │ Docs │ Gmail │ Memory │ System │...│
└────────┬─────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  TTS Response   │
│  (macOS Say)    │
└─────────────────┘

```

### 🗂️ هيكل المشروع | Project Structure

```
haitham_voice_agent/
├── 📱 hva_menubar.py             # تطبيق شريط القوائم الرئيسي | Main Menu Bar App
├── 🖥️ gui_process.py             # عملية الواجهة الرسومية (PyQt) | GUI Process
├── 🖼️ gui_widgets.py             # مكونات الواجهة الرسومية | GUI Widgets
├── ⚙️ config.py                  # إدارة التكوين المركزي | Central Configuration
├── 🎤 stt.py                     # منسق تحويل الكلام لنص | STT Orchestrator
├── 🔊 tts.py                     # منسق تحويل النص لكلام | TTS Orchestrator
├── 👂 wake_word.py               # كشف كلمة الإيقاظ | Wake Word Detection
├── 🧭 intent_router.py           # موجه النوايا الحتمي | Deterministic Intent Router
├── 🤖 llm_router.py              # موجه LLM (Gemini vs GPT) | LLM Router
├── 🔀 model_router.py            # موجه النموذج (e.g., mini vs standard) | Model Router
├── 📡 dispatcher.py              # موزع الأدوات | Tool Dispatcher
│
├── 🧠 memory/                     # نظام الذاكرة الجديد | New Memory System
│   ├── manager.py               # مدير الذاكرة (نقطة الدخول) | Memory Manager (Entrypoint)
│   ├── vector_store.py          # طبقة RAG (ChromaDB) | Vector Store Layer
│   └── graph_store.py           # طبقة الرسم البياني للمعرفة | Knowledge Graph Layer
│
├── 🛠️ tools/                     # مجموعة الأدوات | Toolset
│   ├── 👔 secretary.py          # السكرتير التنفيذي | Executive Secretary
│   ├── 🛡️ advisor.py             # الناصح الأمين | Honest Advisor
│   ├── 🧹 smart_organizer.py      # المنظم الذكي | Smart Organizer
│   ├── 📂 files.py                # عمليات الملفات | File Operations
│   ├── 📄 docs.py                 # معالجة المستندات | Document Processing
│   ├── 🌐 browser.py              # أدوات المتصفح | Browser Tools
│   ├── 💻 terminal.py            # طرفية آمنة | Safe Terminal
│   ├── ⚙️ system_tools.py        # أدوات النظام | System Tools
│   ├── 🗂️ workspace_manager.py   # إدارة مساحة العمل (الطبقة 1 للذاكرة) | Workspace Manager
│   │
│   ├── 📧 gmail/                # وحدة Gmail الكاملة | Full Gmail Module
│   │   ├── connection_manager.py
│   │   ├── gmail_api_handler.py
│   │   ├── imap_handler.py
│   │   ├── smtp_handler.py
│   │   ├── llm_helper.py
│   │   ├── auth/
│   │   ├── models/
│   │   └── utils/
│   │
│   ├── 🎙️ voice/               # أدوات الصوت الداخلية | Internal Voice Tools
│   │   ├── recorder.py          # مسجل الجلسات الطويلة | Session Recorder
│   │   └── stt.py               # محرك STT المحلي (Whisper) | Local STT Engine
│   │
│   ├── 🗣️ stt_router.py          # موجه STT (Google vs Whisper) | STT Router
│   │
│   ├── 🔷 gemini/               # أدوات Gemini | Gemini Tools
│   │   ├── gemini_router.py
│   │   └── model_discovery.py
│   │
│   └── ✅ tasks/                # إدارة المهام | Task Management
│       └── task_manager.py
│
├── 🧪 tests/                    # الاختبارات | Tests
│   ├── test_config.py
│   ├── test_llm_router.py
│   ├── test_model_router.py
│   ├── test_tools.py
│   ├── test_gemini_routing.py
│   ├── test_gmail_llm.py
│   ├── test_memory_foundation.py
│   ├── test_memory_live.py
│   ├── test_voice_local.py
│   └── test_bridge_live.py
│
├── 📋 domain/                   # نماذج المجال (المشاريع، المهام) | Domain Models
│   └── models.py
│
├── 📦 requirements.txt          # المتطلبات | Dependencies
└── 📖 README.md                 # هذا الملف | This file
```

---

## 🚀 التثبيت والإعداد | Installation & Setup

### المتطلبات الأساسية | Prerequisites

<div dir="rtl">

- **نظام التشغيل**: macOS (يفضل Apple Silicon)
- **Python**: 3.11 أو أحدث
- **مفاتيح API**:
  - OpenAI API Key
  - Google Gemini API Key
  - بيانات اعتماد Google Cloud (لمكتبة Speech-to-Text)
- **مصادقة Gmail**: ملف `credentials.json` من Google Cloud Console لـ OAuth 2.0.

</div>

- **Operating System**: macOS (Apple Silicon recommended)
- **Python**: 3.11 or newer
- **API Keys**:
  - OpenAI API Key
  - Google Gemini API Key
  - Google Cloud credentials (for STT library)
- **Gmail Authentication**: A `credentials.json` file from Google Cloud Console for OAuth 2.0.

### خطوات التثبيت | Installation Steps

#### 1️⃣ استنساخ المشروع | Clone Repository

```bash
git clone <repository_url>
cd haitham-voice-agent
```

#### 2️⃣ إنشاء البيئة الافتراضية | Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3️⃣ تثبيت المتطلبات | Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4️⃣ تكوين البيئة | Configure Environment

```bash
cp .env.example .env
nano .env  # أو أي محرر نصوص | or any text editor
```

<div dir="rtl">

قم بتعبئة المتغيرات المطلوبة:

</div>

Fill in the required variables:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Required: Google Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here

# Required: Path to your Google Cloud credentials for STT and Gmail
# This JSON file is used by both the STT library and the Gmail OAuth flow.
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-cloud-credentials.json

# Optional: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

#### 5️⃣ اختبار التكوين | Test Configuration

```bash
python -m haitham_voice_agent.config
```

<div dir="rtl">

يجب أن ترى رسالة تأكيد بنجاح التكوين.

</div>

You should see a confirmation message of successful configuration.

---

## 💡 الاستخدام | Usage

### وضع شريط القوائم (الموصى به) | Menu Bar Mode (Recommended)

<div dir="rtl">

أسهل وأفضل طريقة للاستخدام اليومي هي عبر تطبيق شريط القوائم.

</div>

The easiest and best way for daily use is via the menu bar application.

```bash
# شغل المشغل الذكي
./Start_HVA.command
```

<div dir="rtl">

بعد التشغيل:
1. ستظهر أيقونة 🎤 في شريط القوائم العلوي.
2. اضغط `⌘⇧H` في أي وقت ومن أي تطبيق لبدء الاستماع.
3. قل "هيثم" متبوعًا بأمرك (على سبيل المثال، "هيثم، صباح الخير").
4. ستظهر النتائج في النافذة الرسومية التفاعلية.

**المميزات:**
- تشغيل وإيقاف بنقرة واحدة من شريط القوائم (Toggle ON/OFF).
- يعمل في الخلفية دون الحاجة لإبقاء نافذة Terminal مفتوحة.
- اختصار لوحة مفاتيح عالمي.

</div>

After running:
1. A 🎤 icon will appear in your top menu bar.
2. Press `⌘⇧H` anytime from any application to start listening.
3. Say "Haitham" followed by your command (e.g., "Haitham, good morning").
4. Results will appear in the interactive GUI window.

**Features:**
- One-click Toggle ON/OFF from the menu bar.
- Background operation without needing a Terminal window open.
- Global keyboard shortcut.

### وضع التصحيح (للمطورين) | Debug Mode (For Developers)

<div dir="rtl">

لتشغيل التطبيق في Terminal ورؤية السجلات مباشرة:

</div>

To run the application in the terminal and see live logs:

```bash
python -m haitham_voice_agent.hva_menubar
```

### وضع الاختبار النصي | Text Test Mode

<div dir="rtl">

لاختبار منطق الأوامر بدون استخدام الصوت:

</div>

To test the command logic without using voice:

```bash
python -m haitham_voice_agent.main --test "List files in my Downloads folder"
```

---

## 🛠️ الوحدات والأدوات | Modules & Tools

This section provides a high-level overview of the key modules.

### 1️⃣ الوحدات الأساسية | Core Modules

-   **`hva_menubar.py`**: The main entry point for the application. Manages the macOS menu bar icon, global hotkey, and orchestrates communication between the voice system and the GUI.
-   **`gui_process.py`**: Runs the PyQt-based graphical user interface in a separate process to ensure the main application remains responsive. Handles all visual elements and user interactions.
-   **`dispatcher.py`**: Receives a structured execution plan from the LLM and routes each step to the appropriate tool (e.g., `files.list_files`).
-   **`config.py`**: Centralized configuration hub. Loads environment variables, defines paths, and sets system-wide constants.

### 2️⃣ طبقة التوجيه | Routing Layer

-   **`intent_router.py`**: The first layer of routing. Handles common, deterministic commands (e.g., "save note") with simple rules to bypass the LLM for speed and reliability.
-   **`llm_router.py`**: The second layer. Decides whether to use the Gemini or GPT model family based on the task type (e.g., Gemini for analysis, GPT for tool use).
-   **`model_router.py`**: The third layer. Selects the specific model variant (e.g., `gpt-4o-mini` vs `gpt-4o`) based on task metadata like risk and complexity to optimize for cost.

### 3️⃣ نظام الذاكرة | Memory System

-   **`memory/manager.py`**: The primary interface for the memory system. Orchestrates saving and retrieving information across all three layers.
-   **`tools/workspace_manager.py`**: Manages the structured file-based memory (Layer 1), creating project folders and notes.
-   **`memory/vector_store.py`**: Manages the vector database (Layer 2) for semantic search using ChromaDB.
-   **`memory/graph_store.py`**: Manages the knowledge graph (Layer 3), connecting entities and relationships using NetworkX.

### 4️⃣ وحدة Gmail | Gmail Module (`tools/gmail/`)

-   **`connection_manager.py`**: Intelligently switches between the Gmail API and a fallback IMAP/SMTP connection.
-   **`gmail_api_handler.py`**: Implements all primary functions (fetch, search, draft) using the official Google API.
-   **`auth/oauth_flow.py`**: Handles the secure, browser-based OAuth 2.0 authentication process.
-   **`auth/credentials_store.py`**: Securely stores encrypted credentials in the macOS Keychain.
-   **`llm_helper.py`**: Provides LLM-powered enhancements like summarization and task extraction for emails.

### 5️⃣ الأدوات المتخصصة | Specialist Tools

-   **`tools/secretary.py`**: Implements the "Executive Secretary" persona, handling routines like the morning briefing and work modes.
-   **`tools/advisor.py`**: Implements the "Honest Advisor" persona, providing safety checks and wellness reminders.
-   **`tools/smart_organizer.py`**: Contains logic for cleaning up the Desktop and organizing the Downloads folder.
-   **`tools/files.py` & `tools/docs.py`**: Provide a safe and robust interface for file and document manipulation.

---

## 🧪 الاختبارات | Testing

### تشغيل جميع الاختبارات | Run All Tests

```bash
pytest -v
```

### الاختبارات المتاحة | Available Tests

<div dir="rtl">

| الملف | الوصف |
|------|-------|
| `test_config.py` | يختبر تحميل التكوين وصحة المسارات والمتغيرات. |
| `test_llm_router.py` | يتحقق من أن موجه LLM يختار بين Gemini و GPT بشكل صحيح. |
| `test_model_router.py` | يتحقق من أن موجه النموذج يختار البديل الصحيح (مثل mini مقابل pro) لتحسين التكلفة. |
| `test_tools.py` | اختبارات الوحدة للأدوات الأساسية مثل `files` و `docs`. |
| `test_gemini_routing.py` | يختبر منطق التوجيه الداخلي لـ Gemini (Flash مقابل Pro). |
| `test_gmail_llm.py` | يختبر وظائف LLM الخاصة بالبريد الإلكتروني (التلخيص، استخراج المهام). |
| `test_memory_foundation.py` | يختبر المكونات الأساسية لنظام الذاكرة (الحفظ، الاستعلام). |
| `test_memory_live.py` | اختبارات تكاملية حية لنظام الذاكرة. |
| `test_voice_local.py` | يختبر نظام الصوت المحلي، بما في ذلك التهيئة والتسجيل. |
| `test_bridge_live.py` | اختبار حي شامل من Gmail إلى الذاكرة (حفظ بريد إلكتروني والبحث عنه دلاليًا). |

</div>

| File | Description |
|------|-------------|
| `test_config.py` | Tests that the configuration loads and paths/variables are correct. |
| `test_llm_router.py` | Verifies the LLM router chooses correctly between Gemini and GPT. |
| `test_model_router.py` | Verifies the model router chooses the correct cost-optimized variant (e.g., mini vs pro). |
| `test_tools.py` | Unit tests for basic tools like `files` and `docs`. |
| `test_gemini_routing.py` | Tests the internal Gemini routing logic (Flash vs Pro). |
| `test_gmail_llm.py` | Tests email-specific LLM functions (summarization, task extraction). |
| `test_memory_foundation.py` | Tests the foundational components of the memory system (saving, querying). |
| `test_memory_live.py` | Live integration tests for the memory system. |
| `test_voice_local.py` | Tests the local voice system, including initialization and recording. |
| `test_bridge_live.py` | An end-to-end live test from Gmail to Memory (saving an email and searching for it). |

---

## 🔧 استكشاف الأخطاء | Troubleshooting

### مشاكل شائعة | Common Issues

#### 1️⃣ خطأ في بيانات اعتماد Google | Google Credentials Error

<div dir="rtl">

**المشكلة**: `google.auth.exceptions.DefaultCredentialsError`

**الحل**: تأكد من أن متغير البيئة `GOOGLE_APPLICATION_CREDENTIALS` في ملف `.env` الخاص بك يشير إلى المسار الصحيح لملف `json` الخاص ببيانات الاعتماد.

</div>

**Problem**: `google.auth.exceptions.DefaultCredentialsError`

**Solution**: Ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable in your `.env` file points to the correct path of your credentials `json` file.

#### 2️⃣ مشاكل الصوت (لا يوجد تسجيل) | Audio Issues (No Recording)

<div dir="rtl">

**المشكلة**: لا يعمل التسجيل الصوتي عند الضغط على الاختصار.

**الحل**:
1.  تحقق من أذونات الميكروفون: **System Settings > Privacy & Security > Microphone**. تأكد من أن تطبيق Terminal (أو تطبيق HVA) لديه الإذن.
2.  أعد تثبيت مكتبات الصوت: `pip uninstall pyaudio sounddevice && pip install pyaudio sounddevice`.

</div>

**Problem**: Audio recording doesn't work when pressing the hotkey.

**Solution**:
1.  Check microphone permissions: **System Settings > Privacy & Security > Microphone**. Ensure your Terminal app (or HVA.app) has permission.
2.  Reinstall audio libraries: `pip uninstall pyaudio sounddevice && pip install pyaudio sounddevice`.

#### 3️⃣ فشل مصادقة Gmail | Gmail Authentication Failure

<div dir="rtl">

**المشكلة**: فشل تدفق OAuth أو ظهور خطأ `token has been expired or revoked`.

**الحل**: بيانات الاعتماد القديمة قد تكون غير صالحة. قم بإزالتها لإعادة المصادقة:
`rm ~/.hva_credentials/gmail_token.json`
في المرة التالية التي تستخدم فيها ميزة Gmail، سيتم تشغيل تدفق المصادقة الجديد.

</div>

**Problem**: OAuth flow fails or you get a `token has been expired or revoked` error.

**Solution**: The old token may be invalid. Remove it to re-authenticate:
`rm ~/.hva_credentials/gmail_token.json`
The next time you use a Gmail feature, the new authentication flow will be triggered.

### السجلات | Logs

<div dir="rtl">

**موقع السجلات**: `~/.hva_logs/hva.log`

**عرض السجلات الحية**: `tail -f ~/.hva_logs/hva.log`

</div>

**Log Location**: `~/.hva_logs/hva.log`

**View Live Logs**: `tail -f ~/.hva_logs/hva.log`

---

## 🔒 الأمان | Security

### مبادئ الأمان | Security Principles

<div dir="rtl">

✅ **وضع المسودات فقط**: لا يتم إرسال أي بريد إلكتروني تلقائياً؛ يتم إنشاؤه كمسودة للمراجعة.
✅ **تشفير بيانات الاعتماد**: يتم تشفير بيانات Gmail وتخزينها بأمان في macOS Keychain.
✅ **أوامر طرفية آمنة**: قائمة بيضاء من الأوامر الآمنة فقط (مثل `ls`, `pwd`) مسموح بها.
✅ **تأكيد المستخدم**: يطلب تأكيد المستخدم قبل تنفيذ أي خطة عمل تتضمن عمليات حساسة (مثل حذف الملفات).
✅ **OAuth 2.0**: يستخدم بروتوكول المصادقة القياسي والآمن للوصول إلى Gmail.

</div>

✅ **Drafts-Only Mode**: No emails are ever sent automatically; they are created as drafts for review.
✅ **Credential Encryption**: Gmail credentials are encrypted and stored securely in the macOS Keychain.
✅ **Safe Terminal Commands**: Only a whitelist of safe, read-only commands (like `ls`, `pwd`) are permitted.
✅ **User Confirmation**: User approval is required before executing any action plan involving sensitive operations (like file deletion).
✅ **OAuth 2.0**: Uses the standard, secure authentication protocol for Gmail access.

---

## 📚 التوثيق التقني | Technical Documentation

For detailed specifications of core modules, please refer to the SRS (Software Requirements Specification) documents in the project root.

---

## 🤝 المساهمة | Contributing

<div dir="rtl">

هذا مشروع خاص حالياً. للاستفسارات، يرجى التواصل مع المطور.

</div>

This is currently a private project. For inquiries, please contact the developer.

---

<div align="center">

**Made with ❤️ by Haitham**

🎤 **Voice-Powered • 🤖 AI-Driven • 🔒 Privacy-First**

</div>