#!/bin/bash

# ═══════════════════════════════════════════════════════════
#  🎤 Haitham Voice Agent - Smart Launcher
#  تشغيل الوكيل الصوتي الذكي (بدون تيرمينال)
# ═══════════════════════════════════════════════════════════

PROJECT_DIR="/Users/haitham/development/Haitham Voice Agent (HVA)"
SCRIPT_PATH="$PROJECT_DIR/scripts/launch_silent.sh"

# Check if HVA is already running
if pgrep -f "haitham_voice_agent.hva_menubar" > /dev/null 2>&1; then
  # It is running, so we stop it
  osascript -e 'display notification "Stopping HVA..." with title "Haitham Voice Agent"'
  pkill -f "haitham_voice_agent.hva_menubar"
  osascript -e 'display notification "HVA Stopped" with title "Haitham Voice Agent"'
else
  # It is not running, so we start it
  if [ -f "$SCRIPT_PATH" ]; then
    "$SCRIPT_PATH"
  else
    osascript -e 'display alert "Error: Launch script not found at '"$SCRIPT_PATH"'"'
  fi
fi

# Close this terminal window
osascript -e 'tell application "Terminal" to close (every window whose name contains "Start HVA")' & exit
