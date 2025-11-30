# Haitham Voice Agent (HVA) 🎤🤖

<div dir="rtl">

**وكيل صوتي ذكي لنظام macOS مع توجيه هجين للذكاء الاصطناعي، وعي كامل بالنظام، وتكامل Gmail**

</div>

A voice-operated automation agent for macOS with hybrid LLM routing, full system awareness, Gmail integration, and an advanced memory system.

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
- ✅ **Persistent Memory System**: نظام ذاكرة دائم مع بحث دلالي
- ✅ **Full Gmail Integration**: قراءة، تلخيص، وإنشاء مسودات البريد الإلكتروني
- ✅ **Safety First**: نظام أمان شامل يمنع الإجراءات المدمرة

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
│ Files │ Apps │ Gmail │ Memory │ System   │
└──────────────────────────────────────────┘
```

### 🗂️ هيكل المشروع | Project Structure

```
haitham_voice_agent/
├── 📱 hva_menubar.py             # تطبيق شريط القوائم الرئيسي
├── 🖥️ gui_process.py             # عملية الواجهة الرسومية
├── ⚙️ config.py                  # التكوين المركزي
├── main.py                      # نقطة الدخول (CLI)
│
├── 🧠 tools/system_awareness/    # وحدة الوعي بالنظام
│   ├── system_profiler.py       # Layer 1: Hardware & Apps
│   ├── quick_indexer.py         # Layer 2: Quick Access
│   └── ...
│
├── 🎤 tools/voice/               # وحدة الصوت الموحدة
│   ├── stt.py                   # Unified STT Handler
│   ├── stt_google.py            # Google Cloud Backend
│   ├── stt_whisper_ar.py        # Whisper Arabic Backend
│   └── tts.py                   # Text-to-Speech
│
├── 🛠️ tools/                     # الأدوات
│   ├── files.py                 # عمليات الملفات
│   ├── system_tools.py          # أدوات النظام
│   ├── gmail/                   # وحدة Gmail
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

تم تعزيز المشروع بنظام توثيق وأمان شامل في مجلد `docs/`:

*   **`PROJECT_MAP.md`**: خريطة كاملة للمشروع، الملفات الحرجة، والتبعيات.
*   **`CHANGE_RULES.md`**: بروتوكولات صارمة لتعديل الكود لضمان الاستقرار.
*   **`TEST_COMMANDS.md`**: دليل شامل للاختبار اليدوي والآلي.
*   **`CHECKLIST.md`**: قائمة تحقق قبل وبعد أي تعديل.

</div>

The project is fortified with a comprehensive safety and documentation system in `docs/`:

*   **`PROJECT_MAP.md`**: Full project map, critical files, and dependencies.
*   **`CHANGE_RULES.md`**: Strict protocols for code modification.
*   **`TEST_COMMANDS.md`**: Comprehensive guide for manual and automated testing.
*   **`CHECKLIST.md`**: Pre- and post-change checklists.

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
*   **"اقرأ آخر إيميل"** (Gmail Integration)

</div>

*   **"Open Chrome"** (Uses System Awareness for precise launch)
*   **"Find report file"** (Searches Quick Index then Spotlight)
*   **"How much storage left?"** (Instant storage status)
*   **"Good morning"** (Morning briefing with Memory context)
*   **"Read last email"** (Gmail Integration)

---

<div align="center">

**Made with ❤️ by Haitham**

🎤 **Voice-Powered • 🧠 System-Aware • 🔒 Privacy-First**

</div>