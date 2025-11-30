# Haitham Voice Agent (HVA) 🎤🤖

<div dir="rtl">

**وكيل صوتي ذكي لنظام macOS مع توجيه هجين للذكاء الاصطناعي، تكامل Gmail، ونظام ذاكرة متقدم**

</div>

A voice-operated automation agent for macOS with hybrid LLM routing, Gmail integration, and advanced memory system.

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
- ✅ **Persistent Memory System**: نظام ذاكرة دائم مع بحث دلالي
- ✅ **Gmail Integration**: قراءة وإنشاء مسودات البريد الإلكتروني
- ✅ **Safe macOS Automation**: أتمتة آمنة لنظام macOS

---

## ✨ المميزات الرئيسية | Key Features

### 🎤 نظام التحكم الصوتي | Voice Control System

<div dir="rtl">

- **تحويل الكلام إلى نص (STT)**: استراتيجية هجينة محسّنة للدقة والتكلفة
  - **Voice Activity Detection (VAD)**: كشف تلقائي للنشاط الصوتي
  - **Mixed Language Support**: دعم محسّن للغات المختلطة
  - **Smart Timeout Handling**: معالجة ذكية لانتهاء الوقت
  - **للأوامر القصيرة:** Google Cloud Speech-to-Text (دقة 90-95%)
  - **للتسجيلات الطويلة:** Whisper `large-v3` المحلي (دقة 75-85%)
  - دعم كامل للعربية (ar-SA) والإنجليزية (en-US)
  - كشف تلقائي للغة المستخدمة
  - توفير ~60% من التكلفة مع الحفاظ على الدقة العالية
  
- **تحويل النص إلى كلام (TTS)**: استخدام نظام macOS المدمج
  - صوت "Majed" للعربية
  - أصوات "Samantha/Alex" للإنجليزية
  - استجابة باللغة المكتشفة تلقائياً

</div>

- **Speech-to-Text (STT)**: Enhanced hybrid strategy for accuracy and cost
  - **Voice Activity Detection (VAD)**: Automatic voice activity detection
  - **Mixed Language Support**: Improved support for mixed languages
  - **Smart Timeout Handling**: Intelligent timeout management
  - **For short commands:** Google Cloud Speech-to-Text (90-95% accuracy)
  - **For long sessions:** Whisper `large-v3` local (75-85% accuracy)
  - Full support for Arabic (ar-SA) and English (en-US)
  - Automatic language detection
  - Saves ~60% in costs while maintaining high accuracy
  
- **Text-to-Speech (TTS)**: Using macOS built-in system
  - "Majed" voice for Arabic
  - "Samantha/Alex" voices for English
  - Automatic response in detected language

### 🖥️ الواجهة الرسومية التفاعلية | Interactive GUI

<div dir="rtl">

- **نافذة ذكية**: واجهة رسومية حديثة مع تصميم glassmorphism
- **مؤشر نبضي**: رسوم متحركة تفاعلية أثناء الاستماع والمعالجة
- **روابط قابلة للنقر**: فتح الملفات والروابط مباشرة من النافذة
- **إدخال يدوي**: إمكانية كتابة الأوامر بدلاً من الصوت
- **تثبيت النافذة**: خيار لإبقاء النافذة مفتوحة
- **إغلاق تلقائي**: إغلاق تلقائي بعد 15 ثانية (قابل للتعطيل)

</div>

- **Smart Window**: Modern GUI with glassmorphism design
- **Pulse Indicator**: Interactive animations during listening and processing
- **Clickable Links**: Open files and links directly from window
- **Manual Input**: Type commands instead of voice
- **Pin Window**: Option to keep window open
- **Auto-close**: Automatic close after 15 seconds (can be disabled)

### 📱 تطبيق شريط القوائم | Menu Bar App

<div dir="rtl">

- **اختصار عالمي**: `⌘⇧H` (Cmd+Shift+H) للاستماع من أي مكان
- **عمل في الخلفية**: لا حاجة لنافذة Terminal مفتوحة
- **قائمة سريعة**: الوصول السريع لجميع الوظائف
- **إشعارات**: إشعارات macOS عند اكتمال المهام
- **تكامل GUI**: عرض النتائج في نافذة تفاعلية

</div>

- **Global Hotkey**: `⌘⇧H` (Cmd+Shift+H) to listen from anywhere
- **Background Operation**: No need for Terminal window
- **Quick Menu**: Fast access to all functions
- **Notifications**: macOS notifications when tasks complete
- **GUI Integration**: Display results in interactive window

### 👔 السكرتير التنفيذي | Executive Secretary
<div dir="rtl">

- **الموجز الصباحي**: تقرير يومي ذكي (الطقس، المهام، التقويم، حالة النظام)
- **أوضاع العمل**:
  - **Work**: يفتح VS Code, iTerm ويضبط الصوت 40%
  - **Meeting**: يفتح الملاحظات ويضبط الصوت 80%
  - **Chill**: يفتح Spotify ويضبط الصوت 60%

</div>

- **Morning Briefing**: Smart daily report (Weather, Tasks, Calendar, System)
- **Work Modes**:
  - **Work**: Opens VS Code, iTerm, sets volume 40%
  - **Meeting**: Opens Notes, sets volume 80%
  - **Chill**: Opens Spotify, sets volume 60%

### 🛡️ الناصح الأمين | Honest Advisor
<div dir="rtl">

- **شبكة الأمان**: منع حذف المجلدات المهمة (Documents, Desktop)
- **الصحة الرقمية**: تنبيهات عند العمل المتواصل (2h, 4h)
- **مراقب الموارد**: تنبيه عند استهلاك RAM/CPU العالي

</div>

- **Safety Net**: Prevents deletion of critical folders
- **Digital Wellbeing**: Break reminders after continuous work
- **Resource Monitor**: Alerts on high RAM/CPU usage

### 🤖 التوجيه الهجين للذكاء الاصطناعي | Hybrid LLM Routing

<div dir="rtl">

النظام يستخدم استراتيجية ذكية لتوجيه المهام إلى النموذج الأنسب:

</div>

The system uses an intelligent strategy to route tasks to the most suitable model:

#### 🔷 Gemini Models (للتحليل | For Analysis)
- 📄 معالجة ملفات PDF والمستندات
- 🌐 الترجمة والمقارنة
- 📊 التحليل والتلخيص
- 🖼️ تحليل الصور
- 🧠 الاستدلال بالسياق الكبير

#### 🔶 GPT Models (للتنفيذ | For Execution)
- 📋 إنشاء خطط التنفيذ المنظمة
- 🛠️ استدعاء الأدوات والوظائف
- 💾 عمليات الذاكرة
- 📧 مهام البريد الإلكتروني
- ⚙️ مهام النظام

### 📧 تكامل Gmail | Gmail Integration

<div dir="rtl">

- **القراءة**: جلب آخر الرسائل، البحث، قراءة المحادثات
- **الكتابة**: إنشاء مسودات، الرد، إعادة التوجيه
- **التصنيف**: تلخيص الرسائل، استخراج المهام، التصنيف التلقائي
- **الأمان**: عدم إرسال تلقائي، وضع المسودات فقط، مصادقة OAuth

</div>

- **Reading**: Fetch latest emails, search, read threads
- **Writing**: Create drafts, reply, forward
- **Classification**: Summarize emails, extract tasks, auto-categorize
- **Security**: No auto-send, draft-only mode, OAuth authentication

### 🧠 نظام الذاكرة المتقدم | Advanced Memory System

<div dir="rtl">

نظام ذاكرة متطور يحفظ المعرفة بشكل دائم:

</div>

Advanced memory system that persistently stores knowledge:

#### 🧠 الطبقات الثلاث (The 3 Layers)

1. **الذاكرة الهيكلية (Structured)**:
   - تخزين المشاريع والأفكار في مجلدات (`~/HVA_Memory`)
   - تلخيص تلقائي للأفكار
   
2. **الذاكرة المتجهة (Vector RAG)**:
   - استخدام **ChromaDB** للبحث الدلالي
   - "ماذا قلت عن X؟" يفهم المعنى

3. **رسم المعرفة (Knowledge Graph)**:
   - استخدام **NetworkX** لربط العلاقات
   - يربط الملاحظات بالمشاريع والمفاهيم تلقائياً

### 📁 أدوات إدارة الملفات | File Management Tools

<div dir="rtl">

- **العمليات الأساسية**: عرض، بحث، فتح، نسخ، نقل، إعادة تسمية
- **إدارة المجلدات**: إنشاء، حذف (مع تأكيد)
- **حل ذكي للمسارات**: دعم aliases مثل "home" و "desktop"
- **المجلد الافتراضي**: استخدام المجلد الرئيسي كافتراضي
- **الترتيب**: ترتيب الملفات حسب معايير مختلفة
- **الأمان**: تأكيد للعمليات المدمرة

</div>

- **Basic Operations**: List, search, open, copy, move, rename
- **Folder Management**: Create, delete (with confirmation)
- **Smart Path Resolution**: Support for aliases like "home" and "desktop"
- **Default Folder**: Use home directory as default
- **Sorting**: Sort files by various criteria
- **Safety**: Confirmation for destructive operations

### 📄 معالجة المستندات | Document Processing

<div dir="rtl">

باستخدام قوة Gemini:

</div>

Using Gemini's power:

- 📖 قراءة ملفات PDF
- 📝 تلخيص المستندات
- 🌐 ترجمة الملفات
- 🔄 مقارنة المستندات
- ✅ استخراج المهام من النصوص

### 🌐 أدوات المتصفح | Browser Tools

- فتح الروابط
- البحث في Google
- التنقل الآمن

### 💻 أدوات الطرفية الآمنة | Safe Terminal Tools

<div dir="rtl">

الأوامر المسموحة فقط (بدون sudo):

</div>

Allowed commands only (no sudo):

```bash
ls, pwd, echo, whoami, df
```

---

## 🏗️ البنية المعمارية | Architecture

### 📊 تدفق النظام | System Flow

```
┌─────────────────┐
│  User Voice     │
│  صوت المستخدم   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  STT Engine     │
│  محرك التعرف    │
│  (Whisper)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Intent Router   │
│ موجه النوايا    │
│ (Deterministic) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Router     │
│  موجه الذكاء    │
│ (Gemini vs GPT) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execution Plan  │
│  خطة التنفيذ    │
│  (Structured)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User Confirm    │
│ تأكيد المستخدم  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dispatcher    │
│    الموزع       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│          Tools Layer                │
│          طبقة الأدوات               │
├─────────────────────────────────────┤
│ Files │ Docs │ Gmail │ Memory │ ... │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  TTS Response   │
│  الرد الصوتي    │
│  (macOS Say)    │
└─────────────────┘
```

### 🗂️ هيكل المشروع | Project Structure

```
haitham_voice_agent/
├── 📄 main.py                    # المنسق الرئيسي | Main orchestrator
├── 🖥️ gui_process.py             # الواجهة الرسومية | GUI Process
├── 📱 hva_menubar.py             # تطبيق شريط القوائم | Menu Bar App
├── ⚙️ config.py                  # إدارة التكوين | Configuration management
├── 🎤 stt.py                     # تحويل الكلام لنص | Speech-to-Text
├── 🔊 tts.py                     # تحويل النص لكلام | Text-to-Speech
├── 🧭 intent_router.py           # توجيه النوايا | Intent routing
├── 🤖 llm_router.py              # توجيه LLM الهجين | Hybrid LLM routing
├── 🔀 model_router.py            # توجيه النماذج | Model routing
├── 📡 dispatcher.py              # موزع الأدوات | Tool dispatcher
│
├── 🛠️ tools/                     # الأدوات | Tools
│   ├── files.py                 # عمليات الملفات | File operations
│   ├── docs.py                  # معالجة المستندات | Document processing
│   ├── browser.py               # أدوات المتصفح | Browser tools
│   ├── terminal.py              # طرفية آمنة | Safe terminal
│   ├── system_tools.py          # أدوات النظام | System tools
│   ├── workspace_manager.py     # إدارة مساحة العمل | Workspace manager
│   ├── arabic_normalizer.py     # تطبيع العربية | Arabic normalizer
│   ├── secretary.py             # السكرتير التنفيذي | Executive Secretary
│   ├── advisor.py               # الناصح الأمين | Honest Advisor
│   ├── smart_organizer.py       # المنظم الذكي | Smart Organizer
│   │
│   ├── 📧 gmail/                # وحدة Gmail | Gmail module
│   │   ├── __init__.py
│   │   ├── gmail_api_handler.py
│   │   ├── imap_handler.py
│   │   ├── smtp_handler.py
│   │   ├── llm_helper.py
│   │   ├── memory_integration.py
│   │   ├── connection_manager.py
│   │   ├── prompts.py
│   │   ├── auth/              # المصادقة | Authentication
│   │   ├── models/            # نماذج البيانات | Data models
│   │   └── utils/             # أدوات مساعدة | Utilities
│   │
│   ├── 🧠 memory/               # وحدة الذاكرة | Memory module
│   │   ├── memory_system.py
│   │   ├── manager.py           # مدير الذاكرة (Layer 1)
│   │   ├── vector_store.py      # الذاكرة المتجهة (Layer 2)
│   │   ├── graph_store.py       # رسم المعرفة (Layer 3)
│   │   ├── voice_tools.py
│   │   ├── input/             # إدخال البيانات | Data input
│   │   ├── storage/           # التخزين | Storage
│   │   ├── retrieval/         # الاسترجاع | Retrieval
│   │   ├── intelligence/      # الذكاء | Intelligence
│   │   ├── export/            # التصدير | Export
│   │   ├── maintenance/       # الصيانة | Maintenance
│   │   ├── models/            # النماذج | Models
│   │   └── utils/             # أدوات مساعدة | Utilities
│   │
│   ├── 🎙️ voice/               # أدوات الصوت | Voice tools
│   │   ├── stt_router.py       # STT router (hybrid strategy)
│   │   ├── stt_langid.py       # Language detection
│   │   ├── stt_whisper_en.py   # Whisper English
│   │   ├── stt_whisper_ar.py   # Whisper Arabic (sessions)
│   │   └── stt_google.py       # Google Cloud STT (commands)
│   │
│   ├── 🔷 gemini/               # أدوات Gemini | Gemini tools
│   │
│   └── ✅ tasks/                # إدارة المهام | Task management
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
├── 📋 domain/                   # نماذج المجال | Domain models
│   └── models.py
│
├── 📦 requirements.txt          # المتطلبات | Dependencies
├── 📖 README.md                 # هذا الملف | This file
├── 🚀 RUNNING.md                # دليل التشغيل | Running guide
├── ⚙️ .env.example              # مثال البيئة | Environment example
└── 📜 *.md                      # وثائق SRS | SRS documents
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
  - بيانات اعتماد Google Cloud (لـ STT)
- **اختياري**:
  - بيانات اعتماد Google Sheets (للمزامنة)
  - بيانات اعتماد Gmail OAuth (لتكامل البريد)

</div>

- **Operating System**: macOS (Apple Silicon recommended)
- **Python**: 3.11 or newer
- **API Keys**:
  - OpenAI API Key
  - Google Gemini API Key
  - Google Cloud credentials (for STT)
- **Optional**:
  - Google Sheets credentials (for sync)
  - Gmail OAuth credentials (for email integration)

### خطوات التثبيت | Installation Steps

#### 1️⃣ استنساخ المشروع | Clone Repository

```bash
cd "/Users/haitham/development/Haitham Voice Agent (HVA)"
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

<details>
<summary>📦 قائمة المتطلبات الكاملة | Full Dependencies List</summary>

```
openai                      # OpenAI API
google-generativeai         # Google Gemini API
chromadb                    # Vector database
gspread                     # Google Sheets
soundfile                   # Audio file handling
sounddevice                 # Audio recording
SpeechRecognition           # Speech recognition
pyaudio                     # Audio I/O
cffi                        # C Foreign Function Interface
python-dotenv               # Environment variables
faster-whisper              # Whisper STT
aiosqlite                   # Async SQLite
beautifulsoup4              # HTML parsing
keyring                     # Secure credential storage
keyrings.alt                # Alternative keyring backends
google-auth-oauthlib        # Google OAuth
google-auth                 # Google authentication
google-api-python-client    # Google APIs
numpy                       # Numerical computing
scipy                       # Scientific computing
cryptography                # Encryption
transformers                # ML models
torch                       # PyTorch
pytest-asyncio==1.3.0       # Async testing
PyPDF2==3.0.1              # PDF processing
regex==2025.11.3           # Regular expressions
```

</details>

#### 4️⃣ تكوين البيئة | Configure Environment

```bash
cp .env.example .env
nano .env  # أو أي محرر نصوص | or any text editor
```

<div dir="rtl">

قم بتعبئة المتغيرات التالية:

</div>

Fill in the following variables:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Required: Google Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Google Sheets credentials path (for Memory module sync)
# GOOGLE_SHEETS_CREDENTIALS=/path/to/credentials.json

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

أسهل طريقة للاستخدام اليومي:

</div>

Easiest way for daily use:

```bash
# تشغيل تطبيق شريط القوائم
./HVA\ Simple.command

# أو
python -m haitham_voice_agent.hva_menubar
```

<div dir="rtl">

بعد التشغيل:
1. ستظهر أيقونة 🎤 في شريط القوائم
2. اضغط `⌘⇧H` في أي وقت للاستماع
3. قل "هيثم" + أمرك
4. ستظهر النتائج في نافذة تفاعلية

**المميزات:**
- عمل في الخلفية بدون نوافذ Terminal
- اختصار كيبورد عالمي من أي مكان
- واجهة رسومية تفاعلية للنتائج
- إمكانية الإدخال اليدوي (كتابة الأوامر)

</div>

After running:
1. 🎤 icon appears in menu bar
2. Press `⌘⇧H` anytime to listen
3. Say "هيثم" + your command
4. Results appear in interactive window

**Features:**
- Background operation without Terminal windows
- Global keyboard shortcut from anywhere
- Interactive GUI for results
- Manual input capability (type commands)

### التشغيل الذكي | Smart Launch

<div dir="rtl">

أسهل طريقة لتشغيل النظام هي استخدام المشغل الذكي:
1. انقر نقراً مزدوجاً على ملف **`Start HVA.command`**
2. سيعمل النظام في الخلفية (ستظهر أيقونة 🎤 في شريط القوائم)
3. اضغط **`Cmd + Shift + H`** في أي وقت للتحدث

</div>

The easiest way to run the system is using the Smart Launcher:
1. Double-click **`Start HVA.command`**
2. The system will run in the background (🎤 icon appears in menu bar)
3. Press **`Cmd + Shift + H`** anytime to speak

### الوضع التفاعلي (للمطورين) | Interactive Mode (Dev)

<div dir="rtl">

للتشغيل في التيرمينال ورؤية السجلات:

</div>

To run in terminal and see logs:

```bash
./scripts/HVA_Debug_Launcher.command
# OR
python -m haitham_voice_agent.main
```

### وضع الاختبار | Test Mode

<div dir="rtl">

اختبار بأمر نصي (بدون صوت):

</div>

Test with a text command (no voice):

```bash
python -m haitham_voice_agent.main --test "List files in Downloads"
```

### أمثلة الأوامر الصوتية | Voice Command Examples

#### 🇸🇦 أوامر عربية | Arabic Commands

<div dir="rtl">

**الذاكرة والملاحظات (Memory):**
- "مشروع جديد باسم HVA" (New Project)
- "احفظ فكرة: استخدام RAG للبحث" (Save Thought)
- "ابحث في ذاكرتي عن قواعد البيانات" (Search Memory)
- "ماذا قلت عن الذكاء الاصطناعي؟" (Semantic Search)

**السكرتير والمنظم (Secretary & Organizer):**
- "صباح الخير" (Morning Briefing)
- "وضع العمل" (Work Mode)
- "رتب التنزيلات" (Organize Downloads)
- "نظف سطح المكتب" (Clean Desktop)

**البريد الإلكتروني (Email):**
- "اقرأ آخر إيميل"
- "لخص آخر 5 إيميلات"
- "اكتب مسودة إيميل لأحمد"

**الملفات والمستندات (Files):**
- "اعرض الملفات في المجلد Downloads"
- "لخص هذا الملف PDF"
- "ترجم هذا المستند للإنجليزية"

**المهام (Tasks):**
- "أضف مهمة: مراجعة الكود"
- "اعرض مهامي"

**النظام (System):**
- "افتح تطبيق Safari"
- "ابحث في Google عن Python tutorials"

</div>

**Memory & Notes:**
- "Save note: Project meeting tomorrow at 3"
- "Record idea for Mind-Q project"
- "What are the last notes?"
- "Search notes for meetings"

**Email:**
- "Read latest email"
- "Summarize last 5 emails"
- "Draft email to Ahmad"

**Files & Documents:**
- "Show files in Downloads folder"
- "Summarize this PDF file"
- "Translate this document to English"
- "Search for project files"

**Tasks:**
- "Add task: Review code"
- "Show my tasks"
- "Complete task number 3"

**System:**
- "Open Safari app"
- "Search Google for Python tutorials"

#### 🇬🇧 English Commands

**Memory & Notes:**
- "Save note: Project meeting tomorrow at 3 PM"
- "Record this idea for the AI project"
- "What are my recent notes?"
- "Search notes about machine learning"

**Email:**
- "Read my latest emails"
- "Summarize unread emails"
- "Create a draft email to John"

**Files & Documents:**
- "List files in Documents"
- "Summarize this PDF"
- "Translate document to Arabic"
- "Find files about project X"

**Tasks:**
- "Add task: Complete documentation"
- "List my tasks"
- "Mark task 2 as done"

**System:**
- "Open Chrome"
- "Search for AI news"

---

## 🛠️ الوحدات والأدوات | Modules & Tools

### 1️⃣ نظام الصوت | Voice System

#### 📥 STT (Speech-to-Text)

<div dir="rtl">

**الملف**: `stt.py`

**المميزات**:
- دعم اللغة العربية والإنجليزية
- استخدام Whisper المحلي للدقة
- كشف تلقائي للغة
- تحمل الضوضاء

**الاستخدام**:

</div>

**File**: `stt.py`

**Features**:
- Arabic and English support
- Local Whisper for accuracy
- Automatic language detection
- Noise tolerance

**Usage**:

```python
from haitham_voice_agent.stt import listen_once

text, language = listen_once()
print(f"Detected: {text} (Language: {language})")
```

#### 📤 TTS (Text-to-Speech)

<div dir="rtl">

**الملف**: `tts.py`

**المميزات**:
- استخدام نظام macOS المدمج
- أصوات عربية وإنجليزية
- سرعة قابلة للتعديل

**الاستخدام**:

</div>

**File**: `tts.py`

**Features**:
- Using macOS built-in system
- Arabic and English voices
- Adjustable speed

**Usage**:

```python
from haitham_voice_agent.tts import speak

speak("مرحباً بك", language="ar")
speak("Hello there", language="en")
```

### 2️⃣ موجه النوايا | Intent Router

<div dir="rtl">

**الملف**: `intent_router.py`

**الغرض**: توجيه حتمي للأوامر الشائعة قبل استخدام LLM

**الأوامر المدعومة**:
- حفظ الملاحظات
- بدء/إيقاف الجلسات
- جلب البريد الإلكتروني
- إدارة المهام
- عمليات الملفات
- التحكم بالنظام

</div>

**File**: `intent_router.py`

**Purpose**: Deterministic routing for common commands before using LLM

**Supported Commands**:
- Save notes
- Start/stop sessions
- Fetch emails
- Task management
- File operations
- System control

### 🖥️ الواجهة الرسومية | GUI Process

<div dir="rtl">

**الملف**: `gui_process.py`

**الغرض**: واجهة رسومية تفاعلية لعرض النتائج والتفاعل مع النظام

**المميزات**:
- نافذة Tkinter حديثة مع تصميم عصري
- مؤشر نبضي للحالة (استماع/معالجة)
- دعم الروابط القابلة للنقر
- إدخال يدوي للأوامر
- إغلاق تلقائي ذكي مع خيار التثبيت

</div>

**File**: `gui_process.py`

**Purpose**: Interactive GUI for displaying results and interacting with the system

**Features**:
- Modern Tkinter window with contemporary design
- Pulse indicator for status (listening/processing)
- Clickable links support
- Manual command input
- Smart auto-close with pin option

**Usage**:

```python
from haitham_voice_agent.gui_process import run_gui_process
import multiprocessing

# Create queues for communication
gui_queue = multiprocessing.Queue()
cmd_queue = multiprocessing.Queue()

# Start GUI process
gui_process = multiprocessing.Process(
    target=run_gui_process, 
    args=(gui_queue, cmd_queue)
)
gui_process.start()

# Send messages to GUI
gui_queue.put(('show',))  # Show window
gui_queue.put(('add_message', 'assistant', 'Hello!', False))
gui_queue.put(('add_message', 'success', 'Task completed', True))

# Listen for commands from GUI
cmd = cmd_queue.get()  # Returns ('command', 'user text')
```

### 📱 تطبيق شريط القوائم | Menu Bar App

<div dir="rtl">

**الملف**: `hva_menubar.py`

**الغرض**: تطبيق شريط قوائم macOS مع اختصار كيبورد عالمي

**المميزات**:
- اختصار `⌘⇧H` للاستماع من أي مكان
- قائمة سريعة للوظائف
- عمل في الخلفية بدون Terminal
- تكامل مع GUI Process
- دعم الإدخال اليدوي والصوتي
- كشف كلمة الإيقاظ "هيثم"

</div>

**File**: `hva_menubar.py`

**Purpose**: macOS menu bar app with global keyboard shortcut

**Features**:
- `⌘⇧H` hotkey to listen from anywhere
- Quick menu for functions
- Background operation without Terminal
- Integration with GUI Process
- Support for manual and voice input
- Wake word detection "هيثم"

**Usage**:

```bash
# Run directly
python -m haitham_voice_agent.hva_menubar

# Or use launcher
./HVA\ Simple.command
```

**Menu Options**:
- 🎤 Listen (⌘⇧H) - Start voice listening
- 📝 Show Window - Display GUI window
- 🔄 Reset State - Reset application state
- 🗑️ Clear History - Clear conversation history
- ℹ️ About - Show about dialog
- ⏹️ Quit - Exit application

### 3️⃣ موجه LLM | LLM Router

<div dir="rtl">

**الملف**: `llm_router.py`

**الاستراتيجية**:

</div>

**File**: `llm_router.py`

**Strategy**:

| Task Type | Model | Reason |
|-----------|-------|--------|
| PDF Processing | Gemini | Large context window |
| Translation | Gemini | Better multilingual |
| Summarization | Gemini | Analysis strength |
| Image Analysis | Gemini | Vision capabilities |
| Tool Invocation | GPT | Better function calling |
| JSON Output | GPT | Structured output |
| Memory Operations | GPT | Consistency |
| Email Tasks | GPT | Action-oriented |

### 4️⃣ أدوات الملفات | File Tools

<div dir="rtl">

**الملف**: `tools/files.py`

**الوظائف المتاحة**:

</div>

**File**: `tools/files.py`

**Available Functions**:

```python
class FileTools:
    # List files in directory
    list_files(path: str) -> dict
    
    # Search for files
    search_files(path: str, pattern: str) -> dict
    
    # Open folder in Finder
    open_folder(path: str) -> dict
    
    # Create new folder
    create_folder(path: str) -> dict
    
    # Delete folder (with confirmation)
    delete_folder(path: str) -> dict
    
    # Move file
    move_file(source: str, destination: str) -> dict
    
    # Copy file
    copy_file(source: str, destination: str) -> dict
    
    # Rename file
    rename_file(old_path: str, new_name: str) -> dict
    
    # Sort files
    sort_files(path: str, criteria: str) -> dict
```

### 5️⃣ أدوات المستندات | Document Tools

<div dir="rtl">

**الملف**: `tools/docs.py`

**الوظائف المتاحة**:

</div>

**File**: `tools/docs.py`

**Available Functions**:

```python
class DocumentTools:
    # Summarize file
    summarize_file(file_path: str) -> dict
    
    # Translate file
    translate_file(file_path: str, target_lang: str) -> dict
    
    # Compare files
    compare_files(file1: str, file2: str) -> dict
    
    # Extract tasks from document
    extract_tasks(file_path: str) -> dict
    
    # Read PDF
    read_pdf(file_path: str) -> dict
```

### 6️⃣ وحدة Gmail | Gmail Module

<div dir="rtl">

**المجلد**: `tools/gmail/`

**المكونات**:

</div>

**Folder**: `tools/gmail/`

**Components**:

#### 📨 Gmail API Handler

```python
class GmailAPIHandler:
    # Fetch latest email
    fetch_latest_email(max_results: int = 1) -> dict
    
    # Fetch by query
    fetch_email_by_query(query: str, max_results: int = 10) -> dict
    
    # Fetch thread
    fetch_email_thread(thread_id: str) -> dict
    
    # Create draft
    create_draft(to: str, subject: str, body: str) -> dict
    
    # Reply to email
    reply_to_email(message_id: str, body: str) -> dict
    
    # Forward email
    forward_email(message_id: str, to: str) -> dict
```

#### 📬 IMAP Handler (Fallback)

```python
class IMAPHandler:
    # Fetch emails via IMAP
    fetch_emails(folder: str = "INBOX", limit: int = 10) -> dict
    
    # Search emails
    search_emails(criteria: str) -> dict
```

#### 🤖 LLM Helper

```python
class GmailLLMHelper:
    # Summarize email
    summarize_email(email_content: str) -> str
    
    # Extract tasks
    extract_tasks_from_email(email_content: str) -> list
    
    # Categorize email
    categorize_email(email_content: str) -> str
```

### 7️⃣ نظام الذاكرة | Memory System

<div dir="rtl">

**المجلد**: `tools/memory/`

**البنية**:

</div>

**Folder**: `tools/memory/`

**Structure**:

#### 💾 Memory System Core

```python
class MemorySystem:
    # Save note locally
    save_note_local(content: str, project: str = None, 
                   note_type: str = "note") -> dict
    
    # Get notes
    get_notes_local(project: str = None, limit: int = 10) -> dict
    
    # List recent memories
    list_recent_memories_local(limit: int = 20) -> dict
    
    # Semantic query
    semantic_query_local(query: str, limit: int = 5) -> dict
    
    # Save to Google Sheets (optional)
    save_note_sheet(content: str, project: str = None) -> dict
    
    # Query from Sheets
    query_memory_sheet(query: str) -> dict
```

#### 📊 Data Model

```python
{
    "id": "uuid",
    "timestamp": "2025-11-30T08:00:00",
    "source": "Voice|Chat|Manual",
    "project": "Mind-Q",
    "topic": "AI Development",
    "type": "idea|decision|question|task|note",
    "summary": "Brief summary",
    "details": "Full details",
    "decisions": ["Decision 1", "Decision 2"],
    "next_actions": ["Action 1", "Action 2"],
    "tags": ["ai", "project"],
    "raw_ref": "Original text"
}
```

### 8️⃣ أدوات النظام | System Tools

<div dir="rtl">

**الملف**: `tools/system_tools.py`

**الوظائف**:

</div>

**File**: `tools/system_tools.py`

**Functions**:

```python
class SystemTools:
    # Open application
    open_app(app_name: str) -> dict
    
    # Volume control
    set_volume(level: int) -> dict
    
    # System info
    get_system_info() -> dict
```

### 9️⃣ الطرفية الآمنة | Safe Terminal

<div dir="rtl">

**الملف**: `tools/terminal.py`

**الأوامر المسموحة فقط**:

</div>

**File**: `tools/terminal.py`

**Allowed Commands Only**:

```python
ALLOWED_COMMANDS = [
    "ls", "pwd", "echo", "whoami", "df", "date", "cal"
]

class TerminalTools:
    execute_safe_command(command: str) -> dict
```

---

## ⚙️ التكوين | Configuration

### ملف التكوين | Configuration File

<div dir="rtl">

**الملف**: `config.py`

**المتغيرات الرئيسية**:

</div>

**File**: `config.py`

**Main Variables**:

```python
class Config:
    # Version
    HVA_VERSION = "2.0.0"
    
    # API Keys
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    
    # Paths
    BASE_DIR: Path
    DATA_DIR: Path
    MEMORY_DIR: Path
    LOGS_DIR: Path
    
    # Models
    LOGICAL_MODELS = {
        "logical.mini": "gpt-4o-mini",
        "logical.standard": "gpt-4o",
        "logical.gemini.flash": "gemini-2.0-flash-exp",
        "logical.gemini.pro": "gemini-1.5-pro-latest"
    }
    
    # Voice Settings
    STT_LANGUAGE_AR = "ar-SA"
    STT_LANGUAGE_EN = "en-US"
    TTS_VOICE_AR = "Majed"
    TTS_VOICE_EN = "Samantha"
    
    # Memory Settings
    MEMORY_DB_PATH: Path
    VECTOR_DB_PATH: Path
    
    # Gmail Settings
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose'
    ]
```

### متغيرات البيئة | Environment Variables

<div dir="rtl">

**الملف**: `.env`

</div>

**File**: `.env`

```bash
# Required
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Optional
GOOGLE_SHEETS_CREDENTIALS=/path/to/credentials.json
LOG_LEVEL=INFO
```

---

## 🧪 الاختبارات | Testing

### تشغيل جميع الاختبارات | Run All Tests

```bash
pytest tests/ -v
```

### اختبارات محددة | Specific Tests

```bash
# Configuration tests
pytest tests/test_config.py -v

# LLM Router tests
pytest tests/test_llm_router.py -v

# Model Router tests
pytest tests/test_model_router.py -v

# Tools tests
pytest tests/test_tools.py -v

# Gmail tests
pytest tests/test_gmail_llm.py -v

# Memory tests
pytest tests/test_memory_foundation.py -v
pytest tests/test_memory_live.py -v

# Voice tests
pytest tests/test_voice_local.py -v
```

### الاختبارات المتاحة | Available Tests

<div dir="rtl">

| الملف | الوصف |
|------|-------|
| `test_config.py` | اختبار التكوين والمتغيرات |
| `test_llm_router.py` | اختبار توجيه LLM |
| `test_model_router.py` | اختبار توجيه النماذج |
| `test_tools.py` | اختبار الأدوات |
| `test_gemini_routing.py` | اختبار توجيه Gemini |
| `test_gmail_llm.py` | اختبار تكامل Gmail |
| `test_memory_foundation.py` | اختبار أساسيات الذاكرة |
| `test_memory_live.py` | اختبار الذاكرة الحية |
| `test_voice_local.py` | اختبار النظام الصوتي |
| `test_bridge_live.py` | اختبار الجسر الحي |

</div>

| File | Description |
|------|-------------|
| `test_config.py` | Configuration and variables testing |
| `test_llm_router.py` | LLM routing testing |
| `test_model_router.py` | Model routing testing |
| `test_tools.py` | Tools testing |
| `test_gemini_routing.py` | Gemini routing testing |
| `test_gmail_llm.py` | Gmail integration testing |
| `test_memory_foundation.py` | Memory foundation testing |
| `test_memory_live.py` | Live memory testing |
| `test_voice_local.py` | Voice system testing |
| `test_bridge_live.py` | Live bridge testing |

---

## 🔧 استكشاف الأخطاء | Troubleshooting

### مشاكل شائعة | Common Issues

#### 1️⃣ خطأ في مفاتيح API | API Keys Error

<div dir="rtl">

**المشكلة**: `Configuration Error: Missing API keys`

**الحل**:

</div>

**Problem**: `Configuration Error: Missing API keys`

**Solution**:

```bash
# Check .env file
cat .env

# Ensure keys are set
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...

# Test configuration
python -m haitham_voice_agent.config
```

#### 2️⃣ مشاكل الصوت | Audio Issues

<div dir="rtl">

**المشكلة**: لا يعمل التسجيل الصوتي

**الحل**:

</div>

**Problem**: Audio recording not working

**Solution**:

```bash
# Check microphone permissions
# System Preferences > Security & Privacy > Microphone

# Test audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Install/reinstall PyAudio
pip uninstall pyaudio
pip install pyaudio
```

#### 3️⃣ مشاكل Whisper | Whisper Issues

<div dir="rtl">

**المشكلة**: فشل تحويل الكلام إلى نص

**الحل**:

</div>

**Problem**: Speech-to-text failing

**Solution**:

```bash
# Reinstall faster-whisper
pip uninstall faster-whisper
pip install faster-whisper

# Check model download
python -c "from faster_whisper import WhisperModel; WhisperModel('base')"
```

#### 4️⃣ مشاكل الذاكرة | Memory Issues

<div dir="rtl">

**المشكلة**: فشل حفظ الملاحظات

**الحل**:

</div>

**Problem**: Note saving failing

**Solution**:

```bash
# Check memory directory
ls -la ~/.hva_memory/

# Reset memory database
rm ~/.hva_memory/memory.db
python -m haitham_voice_agent.main --test "Save note: test"
```

#### 5️⃣ مشاكل Gmail | Gmail Issues

<div dir="rtl">

**المشكلة**: فشل المصادقة

**الحل**:

</div>

**Problem**: Authentication failing

**Solution**:

```bash
# Remove old credentials
rm -rf ~/.hva_gmail_credentials/

# Re-authenticate
python -m haitham_voice_agent.main --test "Read latest email"
# Follow OAuth flow
```

### السجلات | Logs

<div dir="rtl">

**موقع السجلات**:

</div>

**Log Location**:

```bash
~/.hva_logs/hva.log
```

<div dir="rtl">

**عرض السجلات**:

</div>

**View Logs**:

```bash
# View recent logs
tail -f ~/.hva_logs/hva.log

# Search for errors
grep ERROR ~/.hva_logs/hva.log

# View with timestamps
cat ~/.hva_logs/hva.log | grep "2025-11-30"
```

---

## 🔒 الأمان | Security

### مبادئ الأمان | Security Principles

<div dir="rtl">

✅ **عدم الإرسال التلقائي**: لا يتم إرسال أي بريد إلكتروني تلقائياً  
✅ **تشفير البيانات**: تخزين آمن للبيانات الحساسة  
✅ **أوامر آمنة**: لا يسمح بأوامر sudo أو مدمرة  
✅ **تأكيد المستخدم**: تأكيد مطلوب للعمليات الحساسة  
✅ **OAuth**: مصادقة آمنة لـ Gmail  
✅ **تخزين محلي**: الأولوية للتخزين المحلي على السحابي  

</div>

✅ **No Auto-Send**: No emails sent automatically  
✅ **Data Encryption**: Secure storage of sensitive data  
✅ **Safe Commands**: No sudo or destructive commands allowed  
✅ **User Confirmation**: Confirmation required for sensitive operations  
✅ **OAuth**: Secure authentication for Gmail  
✅ **Local Storage**: Priority for local over cloud storage  

### العمليات المحظورة | Prohibited Operations

<div dir="rtl">

❌ إرسال البريد الإلكتروني تلقائياً  
❌ الوصول إلى كلمات المرور  
❌ تعديل إعدادات النظام  
❌ تنفيذ أوامر sudo  
❌ التحميلات التلقائية  
❌ أتمتة GUI (الماوس/لوحة المفاتيح)  

</div>

❌ Auto-sending emails  
❌ Accessing passwords  
❌ Modifying system settings  
❌ Executing sudo commands  
❌ Automatic downloads  
❌ GUI automation (mouse/keyboard)  

---

## 📚 التوثيق التقني | Technical Documentation

### وثائق SRS | SRS Documents

<div dir="rtl">

- **[hva_full_srs.md](hva_full_srs.md)**: المواصفات الكاملة للنظام
- **[HVA_Gmail_Module_SRS_v1.0.md](HVA_Gmail_Module_SRS_v1.0.md)**: مواصفات وحدة Gmail
- **[HVA_Advanced_Memory_System_Module_SRS.md](HVA_Advanced_Memory_System_Module_SRS.md)**: مواصفات نظام الذاكرة

</div>

- **[hva_full_srs.md](hva_full_srs.md)**: Complete system specifications
- **[HVA_Gmail_Module_SRS_v1.0.md](HVA_Gmail_Module_SRS_v1.0.md)**: Gmail module specifications
- **[HVA_Advanced_Memory_System_Module_SRS.md](HVA_Advanced_Memory_System_Module_SRS.md)**: Memory system specifications

### دليل التشغيل | Running Guide

<div dir="rtl">

- **[RUNNING.md](RUNNING.md)**: دليل مفصل لتشغيل النظام

</div>

- **[RUNNING.md](RUNNING.md)**: Detailed guide for running the system

---

## 🤝 المساهمة | Contributing

<div dir="rtl">

هذا مشروع خاص حالياً. للاستفسارات، يرجى التواصل مع المطور.

</div>

This is currently a private project. For inquiries, please contact the developer.

### معايير الكود | Code Standards

<div dir="rtl">

- **Python**: PEP 8
- **التوثيق**: Docstrings لجميع الوظائف
- **الاختبارات**: pytest لجميع المميزات الجديدة
- **Git**: Conventional Commits

</div>

- **Python**: PEP 8
- **Documentation**: Docstrings for all functions
- **Testing**: pytest for all new features
- **Git**: Conventional Commits

---

## 📊 حالة التطوير | Development Status

### ✅ المكتمل | Completed

- [x] البنية التحتية الأساسية (STT, TTS, LLM Router, Dispatcher)
- [x] موجه النوايا الحتمي
- [x] التوجيه الهجين للذكاء الاصطناعي
- [x] نظام الذاكرة المحلي
- [x] البحث الدلالي
- [x] تكامل Gmail (API + IMAP)
- [x] أدوات الملفات والمجلدات
- [x] معالجة المستندات
- [x] أدوات المتصفح
- [x] الطرفية الآمنة
- [x] إدارة المهام

### 🚧 قيد التطوير | In Progress

- [ ] تحسين دقة STT للعربية
- [ ] واجهة ويب للتحكم
- [ ] تكامل مع المزيد من الخدمات
- [ ] تحسين الأداء

### 📅 مخطط مستقبلي | Future Plans

- [ ] دعم المزيد من اللغات
- [ ] تطبيق iOS/iPadOS
- [ ] تكامل مع Shortcuts
- [ ] نظام Plugins
- [ ] واجهة رسومية كاملة

---

## 📝 الترخيص | License

<div dir="rtl">

مشروع خاص - جميع الحقوق محفوظة © 2025

</div>

Private project - All rights reserved © 2025

---

## 👤 المطور | Author

**Haitham**  
📅 2025

---

## 🙏 شكر وتقدير | Acknowledgments

<div dir="rtl">

- **OpenAI**: لتوفير GPT API
- **Google**: لتوفير Gemini API
- **Whisper**: لنظام التعرف على الكلام
- **مجتمع Python**: للمكتبات الرائعة

</div>

- **OpenAI**: For providing GPT API
- **Google**: For providing Gemini API
- **Whisper**: For speech recognition system
- **Python Community**: For amazing libraries

---

## 📞 الدعم | Support

<div dir="rtl">

للمشاكل التقنية أو الأسئلة:

1. راجع قسم [استكشاف الأخطاء](#-استكشاف-الأخطاء--troubleshooting)
2. تحقق من [السجلات](#السجلات--logs)
3. راجع [الوثائق التقنية](#-التوثيق-التقني--technical-documentation)

</div>

For technical issues or questions:

1. Check the [Troubleshooting](#-استكشاف-الأخطاء--troubleshooting) section
2. Review the [Logs](#السجلات--logs)
3. Consult the [Technical Documentation](#-التوثيق-التقني--technical-documentation)

---

<div align="center">

**Made with ❤️ by Haitham**

🎤 **Voice-Powered • 🤖 AI-Driven • 🔒 Privacy-First**

</div>
