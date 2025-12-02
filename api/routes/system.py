from fastapi import APIRouter, HTTPException
from haitham_voice_agent.dispatcher import get_dispatcher

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/status")
async def get_system_status():
    """Get system status"""
    dispatcher = get_dispatcher()
    system_tool = dispatcher.tools.get("system")
    
    if not system_tool:
        raise HTTPException(status_code=503, detail="System tool not available")
        
    try:
        if hasattr(system_tool, "get_status"):
            status = await system_tool.get_status()
            return status
        else:
            return {"status": "online", "message": "System tool active"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_system_logs(lines: int = 100):
    """Get backend logs"""
    try:
        log_file = "/tmp/hva_backend.log"
        with open(log_file, "r") as f:
            # Read all lines and return last N
            all_lines = f.readlines()
            return all_lines[-lines:]
    except FileNotFoundError:
        return ["Log file not found."]
    except Exception as e:
        return [f"Error reading logs: {str(e)}"]

@router.post("/report")
async def save_report(report: dict):
    """Save debug report to disk"""
    try:
        import os
        import json
        from datetime import datetime

        # Create reports directory if it doesn't exist
        reports_dir = "debug_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.json"
        filepath = os.path.join(reports_dir, filename)

        # Save report
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return {"status": "success", "filename": filename, "path": os.path.abspath(filepath)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
