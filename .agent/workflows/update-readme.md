---
description: تحديث ملف README تلقائياً | Auto-update README
---

# Workflow: تحديث ملف README | Update README

<div dir="rtl">

هذا الـ workflow يضمن أن ملف README.md يبقى محدثاً دائماً بناءً على التغييرات في الكود.

</div>

This workflow ensures that README.md stays up-to-date based on code changes.

## متى تستخدم هذا الـ Workflow | When to Use This Workflow

<div dir="rtl">

استخدم هذا الـ workflow عندما:
- تضيف وحدة جديدة أو أداة جديدة
- تغير البنية المعمارية
- تضيف ميزة جديدة
- تحدث التبعيات (requirements.txt)
- تغير التكوين (config.py)
- تضيف أمثلة استخدام جديدة
- تحدث وثائق SRS

</div>

Use this workflow when:
- Adding a new module or tool
- Changing the architecture
- Adding a new feature
- Updating dependencies (requirements.txt)
- Changing configuration (config.py)
- Adding new usage examples
- Updating SRS documentation

## الخطوات | Steps

### 1. فحص التغييرات | Check Changes

<div dir="rtl">

افحص ما تم تغييره في المشروع:

</div>

Check what has changed in the project:

```bash
# Check recent commits
git log --oneline -10

# Check modified files
git status

# Check diff
git diff HEAD~1
```

### 2. تحديد الأقسام المتأثرة | Identify Affected Sections

<div dir="rtl">

حدد أي أقسام في README تحتاج للتحديث:

</div>

Identify which README sections need updating:

| التغيير | القسم المتأثر |
|---------|--------------|
| وحدة جديدة | 🛠️ الوحدات والأدوات |
| ميزة جديدة | ✨ المميزات الرئيسية |
| تبعية جديدة | 🚀 التثبيت والإعداد |
| تكوين جديد | ⚙️ التكوين |
| اختبار جديد | 🧪 الاختبارات |
| أمر صوتي جديد | 💡 الاستخدام |
| تغيير معماري | 🏗️ البنية المعمارية |

### 3. تحديث README | Update README

<div dir="rtl">

افتح ملف README وحدث الأقسام المناسبة:

</div>

Open README and update appropriate sections:

```bash
# Open README in editor
code README.md

# Or use nano
nano README.md
```

### 4. التحقق من الدقة | Verify Accuracy

<div dir="rtl">

تأكد من:

</div>

Ensure:

- ✅ جميع أسماء الملفات صحيحة
- ✅ جميع أمثلة الكود تعمل
- ✅ جميع الروابط صحيحة
- ✅ التنسيق سليم (Markdown)
- ✅ الأقسام العربية والإنجليزية متطابقة

- ✅ All file names are correct
- ✅ All code examples work
- ✅ All links are valid
- ✅ Formatting is correct (Markdown)
- ✅ Arabic and English sections match

### 5. اختبار التعليمات | Test Instructions

<div dir="rtl">

اختبر تعليمات التثبيت والاستخدام:

</div>

Test installation and usage instructions:

```bash
# Test installation steps
python -m haitham_voice_agent.config

# Test example commands
python -m haitham_voice_agent.main --test "List files"

# Run tests
pytest tests/ -v
```

### 6. حفظ التغييرات | Commit Changes

```bash
# Add README
git add README.md

# Commit with descriptive message
git commit -m "docs: update README with [describe changes]"

# Push
git push
```

## قالب التحديث | Update Template

<div dir="rtl">

عند إضافة وحدة جديدة، استخدم هذا القالب:

</div>

When adding a new module, use this template:

### إضافة وحدة جديدة | Adding New Module

```markdown
### X️⃣ اسم الوحدة | Module Name

<div dir="rtl">

**الملف**: `path/to/module.py`

**الغرض**: وصف الغرض

**المميزات**:
- ميزة 1
- ميزة 2

</div>

**File**: `path/to/module.py`

**Purpose**: Purpose description

**Features**:
- Feature 1
- Feature 2

**Usage**:

\`\`\`python
from module import Class

# Example usage
instance = Class()
result = instance.method()
\`\`\`
```

## قائمة التحقق | Checklist

<div dir="rtl">

قبل الانتهاء، تأكد من:

</div>

Before finishing, ensure:

- [ ] تم تحديث جميع الأقسام المتأثرة
- [ ] الأمثلة تعمل بشكل صحيح
- [ ] الروابط صحيحة
- [ ] التنسيق سليم
- [ ] النسخة العربية والإنجليزية متطابقة
- [ ] تم اختبار التعليمات
- [ ] تم حفظ التغييرات في Git

- [ ] All affected sections updated
- [ ] Examples work correctly
- [ ] Links are valid
- [ ] Formatting is correct
- [ ] Arabic and English versions match
- [ ] Instructions tested
- [ ] Changes committed to Git

## الصيانة الدورية | Regular Maintenance

<div dir="rtl">

قم بمراجعة README بشكل دوري:

</div>

Review README periodically:

- 📅 **شهرياً**: تحقق من دقة المعلومات
- 📅 **عند كل إصدار**: تحديث رقم الإصدار والميزات
- 📅 **عند تغيير كبير**: مراجعة شاملة

- 📅 **Monthly**: Check information accuracy
- 📅 **Each release**: Update version and features
- 📅 **Major changes**: Comprehensive review

## أدوات مساعدة | Helper Tools

```bash
# Check for broken links (if you have markdown-link-check)
npx markdown-link-check README.md

# Format markdown (if you have prettier)
npx prettier --write README.md

# Check spelling (if you have cspell)
npx cspell README.md
```

---

<div align="center">

**Keep README Fresh! 📝✨**

</div>
