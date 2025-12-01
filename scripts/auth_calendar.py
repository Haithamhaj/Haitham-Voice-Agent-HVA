from haitham_voice_agent.tools.calendar import CalendarTools

print("🚀 Starting Calendar Authorization...")
cal = CalendarTools()
res = cal.authorize()
print(f"Result: {res}")
