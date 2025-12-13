# Haitham Voice Agent (HVA) 🎤🤖

<div dir="rtl">

**وكيل صوتي ذكي لنظام macOS مع توجيه هجين للذكاء الاصطناعي، ذاكرة حية، وعي كامل بالنظام، وتكامل عميق مع خدمات Google.**

</div>

A voice-operated automation agent for macOS with hybrid LLM routing, a living memory system, full system awareness, and deep Google Suite integration.

> [!NOTE]
> **Status: Production Ready (v2.6)** 🚀
> The system features a **Client-Server Architecture** using **FastAPI** (Backend) and **Electron + React** (Frontend), with advanced **Fine-Tuning Lab** for model optimization and **Automated Dataset Collection** for continuous improvement.

---

## 📋 جدول المحتويات | Table of Contents

- [نظرة عامة | Overview](#-نظرة-عامة--overview)
- [المميزات الرئيسية | Key Features](#-المميزات-الرئيسية--key-features)
- [البنية المعمارية | Architecture](#-البنية-المعمارية--architecture)
- [مختبر التحسين (Fine-Tuning Lab)](#-مختبر-التحسين-fine-tuning-lab)
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

**الجديد في v2.6:**
- 🧪 **مختبر التحسين (Fine-Tuning Lab)**: واجهة تفاعلية لمقارنة النماذج وتدريب Qwen على بيانات التوجيه الخاصة بك.
- 📊 **نظام تجميع البيانات التلقائي**: يسجل كل قرار توجيه تلقائياً لبناء مجموعة بيانات تدريب عالية الجودة.
- 🎯 **Qwen 2.5 (3B) المحسّن**: نموذج محلي سريع (1.2 ثانية) مع دقة عالية في التصنيف.
- ✍️ **Haithm Style Fine-Tuning**: تدريب نموذج على أسلوب كتابة Haithm الطبيعي مع أدوات مقارنة مدمجة.

</div>

**Haitham Voice Agent (HVA)** is an intelligent voice-operated automation agent for macOS. It combines advanced AI with natural voice control, supporting both Arabic and English. The system uses a multi-layered, deterministic routing strategy and a "Living Memory" system that merges graph, vector, and relational databases to understand context and relationships.

**New in v2.6:**
- 🧪 **Fine-Tuning Lab**: Interactive interface for model comparison and training Qwen on your routing data.
- 📊 **Automated Dataset Collection**: Automatically logs every routing decision to build high-quality training datasets.
- 🎯 **Optimized Qwen 2.5 (3B)**: Fast local model (1.2s) with high classification accuracy.
- ✍️ **Haithm Style Fine-Tuning**: Train models on Haithm's natural writing style with integrated comparison tools.

### 🎯 الأهداف الأساسية | Core Objectives

- ✅ **Voice-to-Action Automation**: تحويل الأوامر الصوتية إلى إجراءات تلقائية.
- ✅ **Deterministic Routing**: اختيار النموذج الصحيح للمهمة بناءً على البيانات الوصفية.
- ✅ **Living Memory System**: ذاكرة موحدة (Graph + Vector + SQL) تفهم العلاقات والمفاهيم.
- ✅ **System Awareness**: فهم عميق للجهاز، التطبيقات، والملفات.
- ✅ **Executive Personas**: أدوات متخصصة (سكرتير، مستشار) لإدارة المهام.
- ✅ **Full Google Integration**: ربط كامل مع Gmail, Calendar, Drive.
- ✅ **Proactive Notifications**: نظام تنبيهات ذكي للمواعيد والإيميلات.
- ✅ **Safety First**: نظام أمان متعدد الطبقات يمنع الإجراءات المدمرة.
- ✅ **Self-Improving AI**: نظام تعلم ذاتي يتحسن مع الاستخدام.

---

## ✨ المميزات الرئيسية | Key Features

### 🧠 التوجيه الذكي والحتمي | Intelligent & Deterministic Routing

<div dir="rtl">

بنية توجيه من 4 طبقات تضمن الدقة والكفاءة والتكلفة المثلى:

1. **Intent Router**: يتعرف فوراً على الأوامر العربية الأساسية (مثل "احفظ ملاحظة") لتجاوز LLM بالكامل.
2. **Ollama Orchestrator (Qwen 2.5 3B)**: 
   - يعمل كطبقة وسطى محلية سريعة للتصنيف الأولي
   - يدعم **الذاكرة قصيرة المدى** لفهم الأوامر المتتالية
   - **تسجيل تلقائي** لكل قرار توجيه لبناء مجموعة بيانات التدريب
   - قابل للتحسين عبر **Fine-Tuning Lab**
3. **LLM Router**: يوجه المهام استراتيجياً: **Gemini** للمستندات والتحليل، و **GPT** للتخطيط والأدوات.
4. **Model Router**: يختار النموذج الأمثل (Flash vs Pro) بناءً على بيانات المهمة.

</div>

A 4-layer routing architecture ensures accuracy, efficiency, and cost-optimization:

1. **Intent Router**: Instantly catches core Arabic commands to bypass LLM entirely.
2. **Ollama Orchestrator (Qwen 2.5 3B)**:
   - Fast local classification layer
   - **Short-Term Memory** for context-aware follow-ups
   - **Automatic logging** of every routing decision for dataset building
   - Fine-tunable via **Fine-Tuning Lab**
3. **LLM Router**: Strategically routes: **Gemini** for docs/analysis, **GPT** for planning/tools.
4. **Model Router**: Deterministically chooses optimal model variant based on task metadata.

### 🧪 مختبر التحسين | Fine-Tuning Lab

<div dir="rtl">

**مختبر تفاعلي متكامل لتحسين نموذج التوجيه المحلي:**

#### المميزات الرئيسية:
- **📊 نظرة عامة على التجربة**: معلومات تفصيلية عن مجموعة البيانات والنموذج الأساسي والنموذج المحسّن.
- **🔄 خط الأنابيب المرئي**: عرض تفاعلي لمراحل التحسين (إعداد البيانات → التدريب → التقييم → النشر).
- **✅ حالة الموارد**: فحص فوري لوجود مجموعة البيانات والنموذج المحسّن.
- **📁 معاينة البيانات**: عرض عينات من مجموعة بيانات التدريب.
- **⚖️ مقارنة النماذج**: اختبار جنباً إلى جنب بين النموذج الأساسي والمحسّن.
- **📈 ملخص التدريب**: إحصائيات التدريب والأداء (قريباً).
- **🤖 مدرس التحسين الذكي**: مساعد AI يشرح مفاهيم PEFT و QLoRA ويجيب على أسئلتك.

#### نظام تجميع البيانات التلقائي:
- **تسجيل شفاف**: كل قرار توجيه يُسجل تلقائياً بصيغة `ROUTING INPUT` و `ROUTING OUTPUT`.
- **إعداد سهل**: يمكن تفعيل/تعطيل التسجيل عبر `Config.LOG_ROUTING_CLASSIFICATIONS`.
- **بناء مجموعة البيانات**: سكربت `scripts/build_hva_routing_dataset.py` يحول السجلات إلى ملف JSONL جاهز للتدريب.
- **جودة عالية**: يدعم تنسيقات السجلات القديمة والجديدة مع إزالة التكرار التلقائية.

#### سير العمل الموصى به:
1. استخدم HVA بشكل طبيعي لعدة أيام/أسابيع
2. قم بتشغيل `python scripts/build_hva_routing_dataset.py --force`
3. راجع البيانات في مختبر التحسين
4. قارن أداء النموذج الأساسي مع المحسّن
5. استخدم المدرس الذكي لفهم النتائج

</div>

**Integrated interactive lab for optimizing the local routing model:**

#### Key Features:
- **📊 Experiment Overview**: Detailed info about dataset, base model, and fine-tuned model.
- **🔄 Visual Pipeline**: Interactive display of fine-tuning stages (Data Prep → Training → Eval → Deploy).
- **✅ Resource Status**: Instant check for dataset and fine-tuned model availability.
- **📁 Dataset Preview**: View samples from the training dataset.
- **⚖️ Model Comparison**: Side-by-side testing of base vs fine-tuned model.
- **📈 Training Summary**: Training stats and performance metrics (coming soon).
- **🤖 Intelligent Tutor**: AI assistant explaining PEFT, QLoRA concepts and answering questions.

#### Automated Dataset Collection:
- **Transparent Logging**: Every routing decision automatically logged as `ROUTING INPUT` and `ROUTING OUTPUT`.
- **Easy Setup**: Enable/disable via `Config.LOG_ROUTING_CLASSIFICATIONS`.
- **Dataset Building**: Script `scripts/build_hva_routing_dataset.py` converts logs to training-ready JSONL.
- **High Quality**: Supports legacy and new log formats with automatic deduplication.

#### Recommended Workflow:
1. Use HVA normally for several days/weeks
2. Run `python scripts/build_hva_routing_dataset.py --force`
3. Review data in Fine-Tuning Lab
4. Compare base vs fine-tuned model performance
5. Use Intelligent Tutor to understand results

### 🧑‍💼 السكرتير التنفيذي والمستشار | Executive Secretary & Advisor

<div dir="rtl">

شخصيات الذكاء الاصطناعي المدمجة:
- **السكرتير (Secretary)**: "المنفذ". يدير المهام، المشاريع، والملاحظات.
- **المستشار (Advisor)**: "المفكر". يقدم رؤى ويتحقق من سلامة الإجراءات.

</div>

Integrated AI personas:
- **Secretary**: The "doer." Manages tasks, projects, and notes.
- **Advisor**: The "thinker." Provides insights and validates actions for safety.

### 💾 الذاكرة الحية | Living Memory (Graph + Vector + SQL)

<div dir="rtl">

نظام ذاكرة موحد يعمل كـ "عقل واحد":
- **Graph Store**: يفهم العلاقات بين الكيانات.
- **Vector Store**: بحث دلالي عن المفاهيم والأفكار.
- **SQLite Store**: تخزين منظم للحقائق والبيانات.
- **Transactional Logic**: ضمان نزاهة البيانات.

</div>

Unified memory system acting as a single "brain":
- **Graph Store**: Understands relationships between entities.
- **Vector Store**: Semantic search for concepts and ideas.
- **SQLite Store**: Structured storage for facts and metadata.
- **Transactional Logic**: Ensures data integrity via automatic rollback.

### 📧 تكامل Gmail المتقدم | Advanced Gmail Integration

<div dir="rtl">

- **اتصال ذكي**: تبديل تلقائي بين Gmail API و IMAP.
- **تخزين آمن**: استخدام macOS Keychain.
- **مساعد LLM**: Gemini للتلخيص، GPT للردود الذكية.

</div>

- **Intelligent Connection**: Auto-switches between Gmail API and IMAP.
- **Secure Storage**: Uses macOS Keychain.
- **LLM Helpers**: Gemini for summarization, GPT for smart replies.

### 🖥️ الوعي بالنظام والتحكم | System Awareness & Control

<div dir="rtl">

- **نظام 3 طبقات**: ملف تعريف النظام، فهرس سريع، بحث عميق.
- **المنظم الذكي**:
  - **وضع بسيط (مجاني)**: ترتيب حسب التاريخ/الحجم/النوع.
  - **وضع عميق (AI)**: تصنيف ذكي بناءً على المحتوى.
  - **التنظيف التلقائي**: نقل الملفات القديمة من Downloads.
  - **Time Machine**: نظام نقاط استعادة لكل عملية تنظيم.
- **التعلم التكيفي**:
  - **البصمة الرقمية (SHA-256)**: تتبع دقيق للملفات.
  - **التعلم من التحركات اليدوية**: يتعلم من تفضيلاتك.
  - **التصنيف بناءً على الثقة**: تطبيق تلقائي للأنماط المتعلمة.
- **System Sentry**: مراقبة صحة النظام والتنظيف الذكي.

</div>

- **3-Layer System**: System Profile, Quick Index, Deep Search.
- **Smart Organizer**:
  - **Simple Mode (FREE)**: Sort by date/size/type.
  - **Deep Mode (AI)**: Intelligent categorization based on content.
  - **Auto-Cleanup**: Moves old files from Downloads.
  - **Time Machine**: Checkpoint system for every organization operation.
- **Adaptive Learning**:
  - **Digital Fingerprint (SHA-256)**: Precise file tracking.
  - **Learning from Manual Moves**: Learns your preferences.
  - **Confidence-Based Categorization**: Auto-applies learned patterns.
- **System Sentry**: System health monitoring and smart cleanup.

### 🤖 ترقيات الذكاء | Intelligence Upgrades

<div dir="rtl">

- **Smart Feedback Agent**: نظام "نكز" ذكي للمشاريع المتوقفة.
- **Clarification Agent**: حلقة توضيح ذكية (حتى 3 محاولات).
- **Idea Agent**: تحويل الأفكار الخام إلى مشاريع منظمة.
- **iPhone Sync**: مزامنة مع Siri Reminders.
- **Smart Calendar**: فهم طبيعي للتواريخ والأوقات.
- **Premium GUI**: واجهة فخمة مع Dark Mode.
- **Timezone-Aware**: فهم فروقات التوقيت.
- **System Modes**: وضع الاجتماع، العمل، الراحة.

</div>

- **Smart Feedback Agent**: Intelligent nudge system for stale projects.
- **Clarification Agent**: Smart retry loop (max 3 attempts).
- **Idea Agent**: Turns raw ideas into structured projects.
- **iPhone Sync**: Syncs with Siri Reminders.
- **Smart Calendar**: Natural language date parsing.
- **Premium GUI**: Stunning Dark Mode interface.
- **Timezone-Aware**: Understands time zone differences.
- **System Modes**: Meeting, Work, Chill modes.

### 📱 تطبيق شريط القوائم وواجهة المستخدم | Menu Bar App & GUI

<div dir="rtl">

- **اختصار عالمي**: `⌘⇧H` للاستماع من أي مكان.
- **Premium Dashboard**: لوحة تحكم ديناميكية.
- **Live Logs Widget**: عرض حي لتفكير النظام.
- **Memory View**: تصور ثلاثي الأبعاد للذاكرة الحية.
- **Fine-Tuning Lab**: واجهة تفاعلية لتحسين النماذج.
- **Gmail & Calendar**: واجهات مخصصة.
- **Active Agent Indicator**: مؤشر حي للعقل النشط.

</div>

- **Global Hotkey**: `⌘⇧H` to listen from anywhere.
- **Premium Dashboard**: Dynamic grid layout.
- **Live Logs Widget**: Real-time system thinking display.
- **Memory View**: 3D-inspired visualization.
- **Fine-Tuning Lab**: Interactive model optimization interface.
- **Gmail & Calendar**: Dedicated views.
- **Active Agent Indicator**: Live brain activity indicator.

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
┌───────────────────┐
│ Ollama Orchestrator│
│   (Qwen 2.5 3B)   │ ◄── Dataset Logging
│ + Short-Term Mem  │
└───────┬───────────┘
        ▼
┌───────────────┐
│  LLM Router   │
│ (GPT/Gemini)  │
└───────┬───────┘
        ▼
┌───────────────┐
│  Dispatcher   │
│ (Tool Exec)   │
└───────┬───────┘
        ▼
┌───────────────────────────────────────────────┐
│                    Tools Layer                │
├───────────────────────────────────────────────┤
│ Secretary │ Advisor │ Files │ Gmail │ Terminal │
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
├── api/                         # FastAPI Backend
│   ├── main.py                  # API Entry Point
│   └── routes/                  # API Routes
│       ├── finetune.py          # 🆕 Fine-Tuning Lab API
│       ├── voice.py
│       ├── memory.py
│       └── ...
├── desktop/                     # Electron + React Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   └── FinetuneLab.jsx  # 🆕 Fine-Tuning Lab UI
│   │   ├── components/
│   │   └── services/
│   │       └── api.js           # API Client
│   ├── main.js                  # Electron Main
│   └── package.json
├── haitham_voice_agent/         # Core Logic
│   ├── config.py                # 🆕 LOG_ROUTING_CLASSIFICATIONS
│   ├── ollama_orchestrator.py   # 🆕 Dataset Logging
│   ├── dispatcher.py
│   ├── memory/                  # Living Memory
│   └── tools/                   # Tools
├── scripts/
│   └── build_hva_routing_dataset.py  # 🆕 Dataset Builder
├── docs/
│   ├── finetune_notes.md        # 🆕 PEFT/QLoRA Guide
│   ├── hva_routing_dataset_analysis.md  # 🆕 Dataset Analysis
│   └── model_guide_qwen.md      # Qwen Guide
├── data/
│   └── dataset_hva_qwen_routing.jsonl  # Training Dataset
├── run_app.py                   # Unified Launcher
└── requirements.txt
```

---

## 🧪 مختبر التحسين Fine-Tuning Lab

<div dir="rtl">

### الوصول إلى المختبر

افتح التطبيق وانقر على "مختبر النموذج" في الشريط الجانبي، أو انتقل إلى:
`http://localhost:8765/finetune-lab`

### المكونات الرئيسية

#### 1. نظرة عامة على التجربة
- **الهدف**: تحسين Qwen 2.5 (3B) لتصنيف الأوامر الصوتية
- **الطريقة**: PEFT (Parameter-Efficient Fine-Tuning) باستخدام QLoRA
- **البيانات**: أزواج (طلب مستخدم → JSON توجيه) من سجلات الاستخدام الفعلي

#### 2. خط الأنابيب
1. **📁 إعداد البيانات**: تجميع وتنظيف بيانات التوجيه
2. **🎯 التدريب**: ضبط دقيق للنموذج باستخدام QLoRA
3. **📊 التقييم**: قياس الدقة والأداء
4. **🚀 النشر**: دمج النموذج المحسّن في النظام

#### 3. حالة الموارد
- **مجموعة البيانات**: `data/dataset_hva_qwen_routing.jsonl`
- **النموذج الأساسي**: `qwen2.5:3b`
- **النموذج المحسّن**: `hva-qwen-routing-v1`

#### 4. معاينة البيانات
عرض عينات من مجموعة البيانات لفهم جودة البيانات وتنوعها.

#### 5. مقارنة النماذج
اختبر نفس الطلب على النموذجين وقارن:
- **الدقة**: هل الإجابة صحيحة؟
- **السرعة**: زمن الاستجابة
- **الاتساق**: ثبات النتائج

**مقارنة أسلوب Haithm (Haithm Style Comparison):**
- مقارنة مباشرة بين النموذج الأساسي (Qwen 3B) ونموذج Haithm V1 المحسّن
- اختبار جودة النص المولد وأسلوب الكتابة
- قياس زمن الاستجابة على MPS/CPU

#### 6. المدرس الذكي
اسأل أي سؤال عن:
- مفاهيم PEFT و QLoRA
- كيفية تحسين جودة البيانات
- استراتيجيات التدريب
- تفسير النتائج

### سير العمل الكامل

```bash
# 1. استخدم HVA بشكل طبيعي (التسجيل التلقائي مفعّل)
# الأوامر تُسجل تلقائياً في ~/.hva/logs/hva.log

# 2. بناء مجموعة البيانات
python scripts/build_hva_routing_dataset.py --force

# 3. افتح مختبر التحسين
# راجع البيانات وقارن النماذج

# 4. (اختياري) تدريب النموذج
# استخدم Ollama أو Unsloth لتدريب النموذج

# 5. اختبر النموذج المحسّن في المختبر
```

### تكوين التسجيل

في `haitham_voice_agent/config.py`:
```python
LOG_ROUTING_CLASSIFICATIONS: bool = True  # تفعيل التسجيل
```

عند التفعيل، كل قرار توجيه يُسجل كـ:
```
ROUTING INPUT: افتح سفاري
ROUTING OUTPUT: {"type": "execute_command", "intent": "open_app", ...}
```

</div>

### Accessing the Lab

Open the app and click "Fine-Tuning Lab" in the sidebar, or navigate to:
`http://localhost:8765/finetune-lab`

### Main Components

#### 1. Experiment Overview
- **Goal**: Fine-tune Qwen 2.5 (3B) for voice command classification
- **Method**: PEFT (Parameter-Efficient Fine-Tuning) using QLoRA
- **Data**: (User request → Routing JSON) pairs from real usage logs

#### 2. Pipeline
1. **📁 Data Preparation**: Collect and clean routing data
2. **🎯 Training**: Fine-tune model using QLoRA
3. **📊 Evaluation**: Measure accuracy and performance
4. **🚀 Deployment**: Integrate fine-tuned model into system

#### 3. Resource Status
- **Dataset**: `data/dataset_hva_qwen_routing.jsonl`
- **Base Model**: `qwen2.5:3b`
- **Fine-tuned Model**: `hva-qwen-routing-v1`

#### 4. Dataset Preview
View samples from the dataset to understand data quality and diversity.

#### 5. Model Comparison
Test the same request on both models and compare:
- **Accuracy**: Is the answer correct?
- **Speed**: Response time
- **Consistency**: Result stability

**Haithm Style Comparison:**
- Direct comparison between base model (Qwen 3B) and fine-tuned Haithm V1
- Test generated text quality and writing style
- Measure response time on MPS/CPU

#### 6. Intelligent Tutor
Ask any question about:
- PEFT and QLoRA concepts
- How to improve data quality
- Training strategies
- Result interpretation

### Complete Workflow

```bash
# 1. Use HVA normally (automatic logging enabled)
# Commands are automatically logged to ~/.hva/logs/hva.log

# 2. Build the dataset
python scripts/build_hva_routing_dataset.py --force

# 3. Open Fine-Tuning Lab
# Review data and compare models

# 4. (Optional) Train the model
# Use Ollama or Unsloth to train the model

# 5. Test fine-tuned model in the lab
```

### Logging Configuration

In `haitham_voice_agent/config.py`:
```python
LOG_ROUTING_CLASSIFICATIONS: bool = True  # Enable logging
```

When enabled, every routing decision is logged as:
```
ROUTING INPUT: open safari
ROUTING OUTPUT: {"type": "execute_command", "intent": "open_app", ...}
```

---

## 📚 الوحدات والأدوات | Modules & Tools

| Module / Tool             | Description                                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Core Orchestration**    | `dispatcher.py`: Main application loop and task routing.                                                |
| **Backend API**           | `api/`: FastAPI server (Port 8765, Bound to 0.0.0.0).                                                   |
| **Frontend GUI**          | `desktop/`: Electron + React application.                                                               |
| **Fine-Tuning Lab**       | `api/routes/finetune.py` + `desktop/src/pages/FinetuneLab.jsx`: Model optimization interface.          |
| **Dataset Builder**       | `scripts/build_hva_routing_dataset.py`: Converts logs to training data.                                |
| **Unified Voice Engine**  | `tools/voice/`: STT (Google/Whisper) and TTS operations.                                                |
| **System Awareness**      | `tools/system_awareness/`: File/app/system indexing.                                                    |
| **Living Memory**         | `memory/`: Graph + Vector + SQL unified memory system.                                                  |
| **Ollama Orchestrator**   | `ollama_orchestrator.py`: Local Qwen routing with dataset logging.                                     |

---

## 🛠️ أدوات المطور | Developer Toolkit

<div dir="rtl">

يحتوي HVA على مجموعة أدوات مدمجة للمطورين:

- **Network Monitor**: مراقبة حية لجميع طلبات API.
- **Smart Diagnostics**: تحليل ذكي للأخطاء مع تحديد الموقع.
- **State Inspector**: مراقبة حالة WebSocket والذاكرة.
- **Debug Export**: تصدير تقرير شامل بضغطة زر.

[📄 اقرأ الدليل الكامل (DEVELOPER_TOOLKIT.md)](DEVELOPER_TOOLKIT.md)

</div>

HVA includes a built-in Developer Toolkit:

- **Network Monitor**: Live API request monitoring.
- **Smart Diagnostics**: Intelligent error analysis with source location.
- **State Inspector**: Real-time WebSocket and memory monitoring.
- **Debug Export**: One-click comprehensive report export.

[📄 Read the full guide (DEVELOPER_TOOLKIT.md)](DEVELOPER_TOOLKIT.md)

---

## 🔒 نظام الأمان | Safety System

<div dir="rtl">

نظام أمان متعدد الطبقات:

- **🚦 Traffic Light Terminal**:
  - **🟢 أخضر**: أوامر آمنة (`ls`, `pwd`)
  - **🟡 أصفر**: أوامر مقيدة (`git`, `pip`) تطلب تأكيداً
  - **🔴 أحمر**: أوامر خطرة (`rm -rf`, `sudo`) محظورة
- **🏖️ Smart User Sandbox**: منع الوصول خارج `~/`
- **🔐 Secure Credential Store**: استخدام macOS Keychain
- **🛡️ Action Confirmation**: تأكيد للإجراءات المدمرة

</div>

Multi-layered security system:

- **🚦 Traffic Light Terminal**:
  - **🟢 Green**: Safe commands (`ls`, `pwd`)
  - **🟡 Yellow**: Restricted commands (`git`, `pip`) require confirmation
  - **🔴 Red**: Dangerous commands (`rm -rf`, `sudo`) blocked
- **🏖️ Smart User Sandbox**: Blocks access outside `~/`
- **🔐 Secure Credential Store**: Uses macOS Keychain
- **🛡️ Action Confirmation**: Confirmation for destructive actions

---

## 🚀 التثبيت والإعداد | Installation & Setup

### المتطلبات | Prerequisites
- macOS (Apple Silicon recommended)
- Python 3.11+
- Node.js & npm
- Ollama (for local Qwen model)
- API Keys: OpenAI, Gemini, Google Cloud

### التثبيت | Installation

```bash
# 1. Clone the repository
git clone <repo_url>
cd haitham-voice-agent

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Ollama and pull Qwen model
brew install ollama
ollama pull qwen2.5:3b

# 5. Install Frontend dependencies
cd desktop
npm install
cd ..

# 6. Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### الإعداد الأولي | Initial Setup

```bash
# 1. Setup Google credentials
# Place client_secret.json in project root

# 2. Initialize directories
python -c "from haitham_voice_agent.config import Config; Config.ensure_directories()"

# 3. Test Ollama connection
ollama run qwen2.5:3b "Hello"
```

---

## 💡 الاستخدام | Usage

### التشغيل | Running

**1. الطريقة الموصى بها (Recommended):**

```bash
# Start backend
./start_hva.sh

# In another terminal, start frontend
cd desktop
npm run dev
```

**2. وضع التطوير (Development Mode):**

```bash
python run_app.py
```

**3. التطبيق المعبأ (Packaged App):**

```bash
# Build
cd desktop
npm run package

# Run
open "desktop/dist/mac-arm64/HVA Premium.app"
```

### أمثلة الاستخدام | Usage Examples

<div dir="rtl">

**أوامر صوتية:**
- **"صباح الخير"** → موجز صباحي مخصص
- **"احفظ ملاحظة: فكرة المشروع الجديد"** → حفظ في الذاكرة
- **"افتح سفاري"** → فتح التطبيق
- **"بدي ملف عن كرافت"** → بحث في الملفات
- **"رتب مجلد Downloads"** → تنظيم ذكي
- **"لخص آخر إيميل"** → تلخيص بريد
- **"ما مواعيدي اليوم؟"** → عرض التقويم
- **"وضع الاجتماع"** → تفعيل وضع الاجتماع

**مختبر التحسين:**
- افتح `/finetune-lab` في المتصفح
- راجع حالة البيانات والنموذج
- قارن أداء النماذج
- اسأل المدرس الذكي عن PEFT

</div>

**Voice Commands:**
- **"Good morning"** → Personalized morning brief
- **"Save note: new project idea"** → Save to memory
- **"Open Safari"** → Launch app
- **"Find file about CRAFTS"** → File search
- **"Organize Downloads"** → Smart organization
- **"Summarize last email"** → Email summary
- **"What are my events today?"** → Calendar view
- **"Meeting mode"** → Enable meeting mode

**Fine-Tuning Lab:**
- Open `/finetune-lab` in browser
- Review dataset and model status
- Compare model performance
- Ask Intelligent Tutor about PEFT

---

## 💰 تتبع التكلفة والميزانية | Cost Tracking & Budgeting

<div dir="rtl">

- **تتبع فوري**: تكلفة دقيقة لكل عملية
- **تفصيل كامل**: تكاليف منفصلة لـ Gemini و GPT
- **أمان الميزانية**: تنبيهات ومنع للعمليات المكررة
- **لوحة التحكم**: رسوم بيانية يومية وسجلات مفصلة

</div>

- **Real-time Tracking**: Exact cost for every operation
- **Detailed Breakdown**: Separate costs for Gemini and GPT
- **Budget Safety**: Alerts and blocking for redundant operations
- **Dashboard**: Daily charts and detailed logs

---

## 🔧 استكشاف الأخطاء | Troubleshooting

### المشاكل الشائعة | Common Issues

**1. Failed to Fetch / Network Error:**
- **السبب**: الواجهة لا تستطيع الاتصال بالخادم
- **الحل**: تأكد من تشغيل الخادم على المنفذ 8765

**2. Ollama Connection Error:**
- **السبب**: Ollama غير مشغل أو النموذج غير محمل
- **الحل**: 
  ```bash
  ollama serve
  ollama pull qwen2.5:3b
  ```

**3. Dataset Builder Returns 0 Pairs:**
- **السبب**: التسجيل غير مفعّل أو لم تستخدم HVA بعد
- **الحل**: تأكد من `LOG_ROUTING_CLASSIFICATIONS = True` واستخدم HVA

**4. Fine-Tuning Lab Shows "Dataset Not Found":**
- **السبب**: لم يتم بناء مجموعة البيانات بعد
- **الحل**: 
  ```bash
  python scripts/build_hva_routing_dataset.py --force
  ```

**5. Permission Denied (Microphone):**
- **السبب**: قيود أمان macOS
- **الحل**: امنح الأذونات في System Settings → Privacy & Security

---

## ✍️ تحسين أسلوب Haithm | Haithm Style Fine-Tuning

<div dir="rtl">

### نظرة عامة

**Haithm Style Fine-Tuning** هو نظام متكامل لتدريب نماذج اللغة على أسلوب كتابة Haithm الطبيعي. يتضمن:
- مجموعة بيانات من نصوص Haithm الأصلية (~6170 عينة)
- نموذج V1 محسّن باستخدام QLoRA على Qwen 2.5 3B
- أدوات مقارنة CLI و UI مدمجة

### المكونات الرئيسية

#### 1. مجموعة البيانات
- **الموقع**: `data/dataset_haithm_style_natural.jsonl`
- **الحجم**: ~6170 عينة من نصوص Haithm الطبيعية
- **التنسيق**: Alpaca format (instruction, input, output)
- **المصدر**: محادثات GPT، ملاحظات، ومراسلات

#### 2. النماذج المحسّنة (Fine-Tuned Models)

**V1 (Text-Only) - ✅ SUCCESS**
- **الاسم**: `hs-20251211-v1-text-only`
- **الحالة**: ناجح (Proof of Concept)
- **الملاحظات**: جيد في النصوص القصيرة، لكنه يفتقد للذكاء العميق.

**V2.5 (Cognitive Map) - ❌ FAILED VALIDATION**
- **الاسم**: `hva_haithm_style_lora_v2`
- **المنصة**: Google Colab L4 (Bulletproof Mode)
- **الحالة**: **فشل في التحقق (Identity Crisis + JSON Hallucination)**
- **التشخيص**: الموديل يعاني من "أزمة هوية" (يظن نفسه مساعداً) ويهلوس في مخرجات JSON.
- **الدرس المستفاد**: البيانات الطبيعية (6000+) طغت على بيانات البيرسونا (20). الحل هو **Synthetic Data** في V3.
- **[📄 اقرأ تقرير ما بعد الكارثة (Post-Mortem)](docs/V2.5_Post_Mortem.md)**

#### 3. طريقة الاستخدام (Inference)
```bash
python finetune/haithm_style/infer_haithm_style_qwen3b.py \
  --prompt "اكتب فقرة قصيرة عن استخدام AI في المشاريع"
```

**ب. واجهة Finetune Lab:**
- افتح `/finetune-lab` في المتصفح
- انتقل إلى قسم "مقارنة النماذج"
- أدخل نصاً واضغط "تشغيل المقارنة"
- شاهد النتائج جنباً إلى جنب مع أزمنة الاستجابة

### سير العمل الكامل

```bash
# 1. مراجعة البيانات
python scripts/analyze_haithm_style_dataset.py

# 2. تدريب نموذج جديد (اختياري)
python finetune/haithm_style/train_haithm_style_qwen3b.py \
  --config finetune/haithm_style/config_style.yaml \
  --run-id hs-$(date +%Y%m%d-%H%M)

# 3. مقارنة النماذج (CLI)
python finetune/haithm_style/infer_haithm_style_qwen3b.py \
  --prompt "نص الاختبار"

# 4. مقارنة النماذج (UI)
# افتح http://localhost:8765/finetune-lab
```

### التكوين

**ملف التكوين**: `finetune/haithm_style/config_style.yaml`

```yaml
base_model_name: "Qwen/Qwen2.5-3B-Instruct"
dataset_natural: "data/dataset_haithm_style_natural.jsonl"
use_prompts_dataset: false

hyperparameters:
  num_train_epochs: 1
  per_device_train_batch_size: 2
  learning_rate: 2e-4
  max_seq_length: 1024
  lora_r: 16
  lora_alpha: 32
  max_steps: 30  # للاختبار السريع
```

### سجل التجارب

جميع التجارب مسجلة في:
- **Registry**: `finetune/haithm_style/runs.json`
- **Documentation**: `docs/haithm_style_finetune_runs.md`

### الوثائق الإضافية

- [📄 Haithm Style Dataset Guide](docs/haithm_style_dataset.md)
- [📄 Fine-tuning Runs Log](docs/haithm_style_finetune_runs.md)
- [📄 Haithm Corpus Status](docs/haithm_corpus_audio_status.md)

</div>

### Overview

**Haithm Style Fine-Tuning** is an integrated system for training language models on Haithm's natural writing style. It includes:
- Dataset of Haithm's original texts (~6170 samples)
- V1 model fine-tuned using QLoRA on Qwen 2.5 3B
- Integrated CLI and UI comparison tools

### Main Components

#### 1. Dataset
- **Location**: `data/dataset_haithm_style_natural.jsonl`
- **Size**: ~6170 samples of Haithm's natural texts
- **Format**: Alpaca format (instruction, input, output)
- **Source**: GPT conversations, notes, and correspondence

#### 2. Fine-tuned Model (V1)
- **Name**: `hs-20251211-v1-text-only`
- **Base Model**: Qwen/Qwen2.5-3B-Instruct
- **Method**: QLoRA (LoRA rank 16, alpha 32)
- **Location**: `models/hva_haithm_style_lora_hs-20251211-v1-text-only`
- **Characteristics**:
  - Light training (30 steps) as initial test
  - Final loss: ~2.16
  - Training time: ~5.5 minutes on MPS
  - macOS compatible (FP16, no quantization)

#### 3. Comparison Tools

**A. CLI Tool:**
```bash
python finetune/haithm_style/infer_haithm_style_qwen3b.py \
  --prompt "Write a short paragraph about using AI in projects"
```

**B. Finetune Lab UI:**
- Open `/finetune-lab` in browser
- Navigate to "Model Comparison" section
- Enter text and click "Run Comparison"
- View side-by-side results with response times

### Complete Workflow

```bash
# 1. Review data
python scripts/analyze_haithm_style_dataset.py

# 2. Train new model (optional)
python finetune/haithm_style/train_haithm_style_qwen3b.py \
  --config finetune/haithm_style/config_style.yaml \
  --run-id hs-$(date +%Y%m%d-%H%M)

# 3. Compare models (CLI)
python finetune/haithm_style/infer_haithm_style_qwen3b.py \
  --prompt "test text"

# 4. Compare models (UI)
# Open http://localhost:8765/finetune-lab
```

### Configuration

**Config File**: `finetune/haithm_style/config_style.yaml`

```yaml
base_model_name: "Qwen/Qwen2.5-3B-Instruct"
dataset_natural: "data/dataset_haithm_style_natural.jsonl"
use_prompts_dataset: false

hyperparameters:
  num_train_epochs: 1
  per_device_train_batch_size: 2
  learning_rate: 2e-4
  max_seq_length: 1024
  lora_r: 16
  lora_alpha: 32
  max_steps: 30  # for quick testing
```

### Experiment Log

All experiments are logged in:
- **Registry**: `finetune/haithm_style/runs.json`
- **Documentation**: `docs/haithm_style_finetune_runs.md`

### Additional Documentation

- [📄 Haithm Style Dataset Guide](docs/haithm_style_dataset.md)
- [📄 Fine-tuning Runs Log](docs/haithm_style_finetune_runs.md)
- [📄 Haithm Corpus Status](docs/haithm_corpus_audio_status.md)

### 3. Google Colab V2.5 Fine-Tuning (L4 GPU)

**The Winning Strategy (The "Bulletproof" Method):**
After extensive testing with T4 GPUs (failed due to quantization issues), we successfully trained the V2.5 model using the **L4 GPU** with a specific high-stability configuration.

**Key Configuration Features:**
*   **Hardware:** Google Colab L4 (24GB VRAM).
*   **Precision:** Full `torch.bfloat16` (No Quantization/BitsAndBytes involved).
*   **Stability:** Batch Size 1 (Minimizes peak memory) + Gradient Accumulation 32 (Maintains quality).
*   **Safety:** Built-in Memory Wiper (GC/Empty Cache) to prevent OOM errors.
*   **Data Strategy:** V2 Datasets + **V3 Cognitive Map** (Weighted 50x for strong adherence).

**Successful Script:**
[HVA_Finetune_V2_5_L4_Method2_Success.py](colab_notebooks/HVA_Finetune_V2_5_L4_Method2_Success.py)

---

## 📖 الوثائق الإضافية | Additional Documentation

- [📄 Developer Toolkit Guide](DEVELOPER_TOOLKIT.md)
- [📄 Fine-Tuning Notes](docs/finetune_notes.md)
- [📄 Dataset Analysis](docs/hva_routing_dataset_analysis.md)
- [📄 Qwen Model Guide](docs/model_guide_qwen.md)
- [📄 Gmail Module SRS](HVA_Gmail_Module_SRS_v1.0.md)
- [📄 Memory System SRS](HVA_Advanced_Memory_System_Module_SRS.md)

---

<div align="center">

**Made with ❤️ by Haitham**

🎤 **Voice-Powered** • 🧠 **System-Aware** • 🔒 **Privacy-First** • 🧪 **Self-Improving**

</div>