#!/bin/zsh

# ═══════════════════════════════════════════════════════════
#  🎤 HVA Simple - Menu Bar Launcher
#  تشغيل الوكيل الصوتي في شريط القوائم
# ═══════════════════════════════════════════════════════════

PROJECT_DIR="/Users/haitham/development/Haitham Voice Agent (HVA)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
  echo "⚠️  البيئة الافتراضية غير موجودة!"
  echo "يرجى تشغيل: python3 -m venv .venv"
  exit 1
fi

# Check .env file
if [ ! -f "$PROJECT_DIR/.env" ]; then
  echo "⚠️  ملف .env غير موجود!"
  echo "يرجى إنشاء ملف .env مع المفاتيح المطلوبة"
  exit 1
fi

echo "🎤 Starting HVA Menu Bar App..."
echo ""
echo "✨ التعليمات:"
echo "  1. ستظهر أيقونة 🎤 في شريط القوائم"
echo "  2. اضغط ⌘⇧H (Cmd+Shift+H) في أي وقت"
echo "  3. قل 'هيثم' + أمرك"
echo "  4. شاهد النتيجة في النافذة"
echo ""
echo "🔴 للإيقاف: اضغط Ctrl+C"
echo ""

# Run the menu bar app
"$VENV_PYTHON" -m haitham_voice_agent.hva_menubar
