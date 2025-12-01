# Haitham Voice Agent (HVA) 🎤🤖

<div dir="rtl">

**وكيل صوتي ذكي لنظام macOS مع توجيه هجين للذكاء الاصطناعي، وعي كامل بالنظام، وتكامل Gmail**

</div>

A voice-operated automation agent for macOS with hybrid LLM routing, full system awareness, Gmail integration, and an advanced memory system.

> [!NOTE]
> **Status: Production Ready** 🚀
> The system has undergone a major architectural refactoring (Dec 2025) to ensure stability, unified routing, and zero state drift.

---

## 📋 جدول المحتويات | Table of Contents

- [نظرة عامة | Overview](#-نظرة-عامة--overview)
- [المميزات الرئيسية | Key Features](#-المميزات-الرئيسية--key-features)
- [البنية المعمارية | Architecture](#-البنية-المعمارية--architecture)
- [التثبيت والإعداد | Installation & Setup](#-التثبيت-والإعداد--installation--setup)
- [الاستخدام | Usage](#-الاستخدام--usage)
- [الوحدات والأدوات | Modules & Tools](#-الوحدات-والأدوات--modules--tools)
- [نظام الأمان | Safety System](#-نظام-الأمان--safety-system)
- [استكشاف الأخطاء | Troubleshooting](#-استكشاف-الأخطاء--troubleshooting)

---

## 🌟 نظرة عامة | Overview

<div dir="rtl">

**Haitham Voice Agent (HVA)** هو وكيل صوتي ذكي مصمم خصيصاً لنظام macOS، يجمع بين قوة الذكاء الاصطناعي المتقدم والتحكم الصوتي الطبيعي. يدعم النظام اللغتين العربية والإنجليزية، ويستخدم استراتيجية توجيه هجينة بين نماذج Gemini و GPT، بالإضافة إلى نظام "وعي بالنظام" (System Awareness) لفهم جهازك وملفاتك بدقة.

</div>

**Haitham Voice Agent (HVA)** is an intelligent voice-operated automation agent designed specifically for macOS. It combines the power of advanced AI with natural voice control, supporting both Arabic and English languages. The system uses a hybrid routing strategy between Gemini and GPT models, along with a "System Awareness" module to deeply understand your device and files.

### 🎯 الأهداف الأساسية | Core Objectives

- ✅ **Voice-to-Action Automation**: تحويل الأوامر الصوتية إلى إجراءات تلقائية
- ✅ **System Awareness**: فهم عميق للجهاز، التطبيقات، والملفات (3-Layer Architecture)
- ✅ **Hybrid LLM Intelligence**: توجيه ذكي بين نماذج الذكاء الاصطناعي
- ✅ **Unified Memory System**: ذاكرة موحدة تعتمد على SQLite و Vector Store (لا يوجد انقسام في الذاكرة)
- ✅ **Unified Memory System**: ذاكرة موحدة تعتمد على SQLite و Vector Store (لا يوجد انقسام في الذاكرة)
- ✅ **Full Google Integration**: ربط كامل مع Gmail, Calendar, Drive (Unified OAuth)
- ✅ **Proactive Notifications**: نظام تنبيهات ذكي للمواعيد والإيميلات الهامة
- ✅ **Safety First**: نظام أمان شامل يمنع الإجراءات المدمرة
- ✅ **Robust Architecture**: نظام غير محجوب (Non-blocking I/O) مع معالجة ذكية للأخطاء

---

## ✨ المميزات الرئيسية | Key Features

### 🧠 الوعي بالنظام | System Awareness (New)

<div dir="rtl">

نظام ذكي مكون من 3 طبقات يمنح الوكيل معرفة فورية بجهازك:
1.  **Layer 1 (System Profile)**: يعرف مواصفات جهازك (M4 Chip, RAM) والتطبيقات المثبتة بدقة.
2.  **Layer 2 (Quick Access)**: فهرس فوري للملفات في سطح المكتب، التنزيلات، والمستندات.
3.  **Layer 3 (Deep Search)**: بحث عميق باستخدام Spotlight (`mdfind`) للعثور على أي ملف في ثوانٍ.

</div>

A smart 3-layer system giving the agent instant knowledge of your device:
1.  **Layer 1 (System Profile)**: Knows your hardware specs and installed apps.
2.  **Layer 2 (Quick Access)**: Instant index of Desktop, Downloads, and Documents.
3.  **Layer 3 (Deep Search)**: Deep search using Spotlight (`mdfind`) to find any file in seconds.

### 👂 استراتيجية الصوت الموحدة | Unified Voice Strategy (Golden Rule)

<div dir="rtl">

نستخدم استراتيجية "القاعدة الذهبية" لضمان أفضل دقة:
*   **الأوامر العربية القصيرة**: نستخدم **Google Cloud STT** (دقة عالية وسرعة).
*   **الجلسات الطويلة**: نستخدم **Whisper Large-v3** (مجاني، محلي، ويفهم السياق الطويل).
*   **الإنجليزية**: نستخدم **Whisper** (محلي وسريع).

</div>

We use the "Golden Rule" strategy for best accuracy:
*   **Short Arabic Commands**: Uses **Google Cloud STT** (High accuracy & speed).
*   **Long Sessions**: Uses **Whisper Large-v3** (Free, local, handles long context).
*   **English**: Uses **Whisper** (Local & fast).

### 💾 الذاكرة الموحدة | Unified Memory (New)

<div dir="rtl">

تم توحيد نظام الذاكرة بالكامل ليعمل كـ "عقل واحد":
*   **SQLite Store**: تخزين منظم للملاحظات، المشاريع، والمهام.
*   **Vector Store**: بحث دلالي (Semantic Search) للعثور على المعلومات بالمعنى.
*   **Transactional Logic**: ضمان نزاهة البيانات (Data Integrity) عبر التراجع التلقائي عند الخطأ.
*   **تكامل كامل**: السكرتير (Secretary) والمستشار (Advisor) يقرأون ويكتبون في نفس قاعدة البيانات.

</div>

The memory system is fully unified to act as a "Single Brain":
*   **SQLite Store**: Structured storage for notes, projects, and tasks.
*   **Vector Store**: Semantic search to find information by meaning.
*   **Transactional Logic**: Ensures data integrity via automatic rollback on failure.
*   **Full Integration**: Secretary and Advisor read/write to the same database.

### ⚡️ أداء عالي واستقرار | High Performance & Stability

<div dir="rtl">

- **Non-blocking I/O**: النظام لا يتجمد أثناء التسجيل ويستجيب للمقاطعة (Ctrl+C).
- **Smart Fallback**: الأوامر غير المفهومة أو القصيرة تُحفظ تلقائياً كملاحظات بدلاً من رفضها.
- **Thread-Safe**: تسجيل ومعالجة متزامنة دون تضارب.

</div>

- **Non-blocking I/O**: System remains responsive during recording and handles interrupts gracefully.
- **Smart Fallback**: Unrecognized or short commands are automatically saved as notes.
- **Thread-Safe**: Concurrent recording and processing without conflicts.

### 🧠 الترقية الذكية | Intelligence Upgrade (New)

<div dir="rtl">

- **📅 Calendar Integration**: إدارة المواعيد، إنشاء اجتماعات، والاستعلام عن الجدول اليومي.
- **☁️ Drive Integration**: البحث عن الملفات في السحابة وعرضها.
- **🔔 Proactive Notifications**: "الجهاز العصبي" للنظام. ينبهك قبل الاجتماعات بـ 15 دقيقة وعند وصول إيميلات هامة.

</div>

- **📅 Calendar Integration**: Manage events, schedule meetings, and query daily schedule.
- **☁️ Drive Integration**: Search and view cloud files.
- **🔔 Proactive Notifications**: The system's "Nervous System". Alerts you 15 mins before meetings and for important emails.

### 🚦 الطرفية الآمنة | Secure Terminal (New)

<div dir="rtl">

- **Traffic Light System**: نظام أمان يمنع الأوامر الخطرة تلقائياً.
- **Developer Friendly**: دعم تنفيذ أوامر git, python, pip بأمان.
- **Injection Protection**: حماية ضد هجمات التسلسل (Command Chaining).

</div>

- **Traffic Light System**: Automatically blocks dangerous commands.
- **Developer Friendly**: Safely execute git, python, pip commands.
- **Injection Protection**: Prevents command chaining attacks.

### 📱 تطبيق شريط القوائم | Menu Bar App

<div dir="rtl">

- **اختصار عالمي**: `⌘⇧H` (Cmd+Shift+H).
- **أداء محسن**: تحديثات واجهة سريعة ومعالجة خلفية غير معطلة للنظام.
- **إشعارات النظام**: تنبيهات عند اكتمال المهام.

</div>

- **Global Hotkey**: `⌘⇧H` (Cmd+Shift+H).
- **Optimized Performance**: Fast UI updates and non-blocking background processing.
- **System Notifications**: Alerts when tasks complete.

---

## 🏗️ البنية المعمارية | Architecture

### 📊 تدفق النظام | System Flow

```
┌─────────────────┐
│  User Voice     │
└────────┬────────┘
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Unified STT     │ ───► │ System Awareness │
│ (Google/Whisper)│      │ (Profile/Index)  │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         ▼                        │
┌─────────────────┐               │
│ Ollama          │ ◄─────────────┘
│ Orchestrator    │
└────────┬────────┘
         ▼
┌─────────────────┐
│ LLM Router      │
│ (GPT/Gemini)    │
└────────┬────────┘
         ▼
┌─────────────────┐
│   Dispatcher    │
└────────┬────────┘
         ▼
┌──────────────────────────────────────────┐
│               Tools Layer                │
├──────────────────────────────────────────┤
│ Files │ Apps │ Gmail │ Memory │ Terminal │
│                      │ (SQLite)          │
└──────────────────────────────────────────┘
```

### 🗂️ هيكل المشروع | Project Structure

```
haitham_voice_agent/
├── 📱 hva_menubar.py             # تطبيق شريط القوائم الرئيسي
├── 🖥️ gui_process.py             # عملية الواجهة الرسومية
├── ⚙️ config.py                  # التكوين المركزي
├── main.py                      # نقطة الدخول (CLI - Non-blocking)
│
├── 🧠 tools/system_awareness/    # وحدة الوعي بالنظام
│   ├── system_profiler.py       # Layer 1: Hardware & Apps
│   ├── quick_indexer.py         # Layer 2: Quick Access
│   └── ...
│
├── 🎤 tools/voice/               # وحدة الصوت الموحدة
│   ├── stt.py                   # Unified STT Handler
│   ├── models.py                # Shared Whisper Models
│   ├── stt_google.py            # Google Cloud Backend
│   ├── stt_whisper_ar.py        # Whisper Arabic Backend
│   └── tts.py                   # Text-to-Speech
│
├── 🛠️ tools/                     # الأدوات
│   ├── files.py                 # Smart Sandbox File Operations
│   ├── system_tools.py          # أدوات النظام
│   ├── terminal.py              # Traffic Light Terminal Tools
│   ├── gmail/                   # وحدة Gmail
│   ├── secretary.py             # (Memory Integrated - SQLite)
│   └── advisor.py               # (Memory Integrated - SQLite)
│
├── 💾 memory/                    # نظام الذاكرة الموحد
│   ├── manager.py               # Unified Wrapper (Transactional)
│   └── ...
│
├── ☁️ ollama_orchestrator.py     # منسق الذكاء الاصطناعي المحلي
└── 🛡️ docs/                      # وثائق الأمان والنظام
    ├── PROJECT_MAP.md
    ├── CHANGE_RULES.md
    └── TEST_COMMANDS.md
```

---

## 🔒 نظام الأمان | Safety System

<div dir="rtl">

تم تعزيز المشروع بنظام أمان متقدم (Security Architecture 2.0):

*   **🚦 Traffic Light Terminal**:
    *   **🟢 أخضر**: أوامر آمنة (`ls`, `pwd`) تنفذ فوراً.
    *   **🟡 أصفر**: أوامر مقيدة (`python`, `pip`) تطلب تأكيداً.
    *   **🔴 أحمر**: أوامر خطرة (`rm -rf`, `mkfs`) محظورة تماماً.
*   **🏖️ Smart User Sandbox**:
    *   يمنع الوصول لأي ملف خارج مجلد المستخدم (`~/`).
    *   يحظر المجلدات الحساسة (`.ssh`, `Library`) حتى داخل مجلد المستخدم.
*   **🛡️ Documentation**:
    *   **`PROJECT_MAP.md`**: خريطة كاملة للمشروع.
    *   **`CHANGE_RULES.md`**: بروتوكولات صارمة لتعديل الكود.

</div>

The project is fortified with an advanced security system (Security Architecture 2.0):

*   **🚦 Traffic Light Terminal**:
    *   **🟢 Green**: Safe commands (`ls`, `pwd`) execute immediately.
    *   **🟡 Yellow**: Restricted commands (`python`, `pip`) require confirmation.
    *   **🔴 Red**: Dangerous commands (`rm -rf`, `mkfs`) are strictly blocked.
*   **🏖️ Smart User Sandbox**:
    *   Blocks access to any file outside the user's home directory (`~/`).
    *   Blacklists sensitive folders (`.ssh`, `Library`) even within home.
*   **🛡️ Documentation**:
    *   **`PROJECT_MAP.md`**: Full project map.
    *   **`CHANGE_RULES.md`**: Strict protocols for code modification.

---

## 🚀 التثبيت والإعداد | Installation & Setup

### المتطلبات | Prerequisites
- macOS (Apple Silicon recommended)
- Python 3.11+
- API Keys: OpenAI, Gemini, Google Cloud (STT/Gmail)

### التثبيت | Installation

```bash
# 1. Clone
git clone <repo_url>
cd haitham-voice-agent

# 2. Venv
python3 -m venv .venv
source .venv/bin/activate

# 3. Install
pip install -r requirements.txt

# 4. Config
cp .env.example .env
# Edit .env with your API keys
```

---

## 💡 الاستخدام | Usage

### التشغيل | Running

```bash
# تشغيل التطبيق (شريط القوائم)
python -m haitham_voice_agent.hva_menubar
```

### أوامر صوتية للتجربة | Voice Commands to Try

<div dir="rtl">

*   **"افتح كروم"** (يستخدم System Awareness لفتح التطبيق بدقة)
*   **"وين ملف التقرير؟"** (يبحث في الفهرس السريع ثم Spotlight)
*   **"كم المساحة المتبقية؟"** (يعطيك حالة التخزين فوراً)
*   **"صباح الخير"** (الموجز الصباحي مع سياق الذاكرة)
*   **"صباح الخير"** (الموجز الصباحي مع سياق الذاكرة)
*   **"اقرأ آخر إيميل"** (Gmail Integration)
*   **"ما هي مواعيدي اليوم؟"** (Calendar Integration)
*   **"ابحث في درايف عن ملف العقد"** (Drive Integration)
*   **"نفذ أمر git status"** (Terminal Integration)

</div>

*   **"Open Chrome"** (Uses System Awareness for precise launch)
*   **"Find report file"** (Searches Quick Index then Spotlight)
*   **"How much storage left?"** (Instant storage status)
*   **"Good morning"** (Morning briefing with Memory context)
*   **"Good morning"** (Morning briefing with Memory context)
*   **"Read last email"** (Gmail Integration)
*   **"What are my events today?"** (Calendar Integration)
*   **"Search Drive for contract"** (Drive Integration)
*   **"Run git status"** (Terminal Integration)

---

<div align="center">

**Made with ❤️ by Haitham**

🎤 **Voice-Powered • 🧠 System-Aware • 🔒 Privacy-First**

</div>