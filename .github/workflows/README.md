# GitHub Action: Auto-update README

## الغرض | Purpose

<div dir="rtl">

هذا الـ GitHub Action يحدث ملف README.md تلقائياً عند كل push للكود.

</div>

This GitHub Action automatically updates README.md on every code push.

---

## كيف يعمل | How It Works

### 1. **المشغلات | Triggers**

The action runs when:
- Code is pushed to `main` branch
- Python files in `haitham_voice_agent/` are changed
- `requirements.txt` is updated
- `.env.example` is modified
- `config.py` is changed

### 2. **العملية | Process**

```
Push to main
    ↓
Detect changed files
    ↓
Analyze changes with GPT
    ↓
Suggest README updates
    ↓
Auto-commit if needed
```

### 3. **الذكاء | Intelligence**

Uses GPT-4o-mini to:
- Analyze code changes
- Identify affected README sections
- Suggest minimal, relevant updates
- Skip unnecessary updates

---

## الإعداد | Setup

### Required GitHub Secret:

Add `OPENAI_API_KEY` to your repository secrets:

1. Go to: **Settings** → **Secrets and variables** → **Actions**
2. Click: **New repository secret**
3. Name: `OPENAI_API_KEY`
4. Value: Your OpenAI API key
5. Click: **Add secret**

---

## الاستخدام | Usage

### Automatic (Default)

The action runs automatically on every push. No manual intervention needed.

### Manual Testing

Test the update script locally:

```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Run script
python scripts/update_readme.py
```

---

## التكلفة | Cost

- **Frequency:** Once per push to main
- **Model:** GPT-4o-mini
- **Cost:** ~$0.0001 per run
- **Monthly:** ~$0.003 (30 pushes/month)

**Very affordable!** 💰

---

## التخصيص | Customization

### Skip Auto-update

Add `[skip ci]` to your commit message:

```bash
git commit -m "feat: add feature [skip ci]"
```

### Modify Triggers

Edit `.github/workflows/update-readme.yml`:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'your/custom/path/**'
```

---

## استكشاف الأخطاء | Troubleshooting

### Action fails with "API key not found"

→ Add `OPENAI_API_KEY` to GitHub secrets (see Setup above)

### README not updating

→ Check action logs in **Actions** tab
→ Verify changed files match trigger paths

### Too many updates

→ Adjust GPT prompt in `scripts/update_readme.py`
→ Add more specific file filters

---

## الملفات | Files

- `.github/workflows/update-readme.yml` - GitHub Action workflow
- `scripts/update_readme.py` - Update logic (GPT-powered)
- `.agent/workflows/update-readme.md` - Manual workflow guide

---

<div align="center">

**Keep README Fresh, Automatically! 📝✨**

</div>
