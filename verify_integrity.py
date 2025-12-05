import sys
import importlib
import pkgutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("IntegrityCheck")

def check_imports():
    """Attempt to import all key modules to catch SyntaxErrors and ImportErrors"""
    root_path = Path(__file__).parent
    sys.path.insert(0, str(root_path))
    
    modules_to_check = [
        "haitham_voice_agent.tools.files",
        "haitham_voice_agent.tools.smart_organizer",
        "haitham_voice_agent.tools.deep_organizer",
        "haitham_voice_agent.tools.memory.memory_system",
        "haitham_voice_agent.llm_router",
        "haitham_voice_agent.intent_router",
        "api.main"
    ]
    
    failed = []
    
    for module_name in modules_to_check:
        try:
            importlib.import_module(module_name)
            logger.info(f"✅ Import OK: {module_name}")
        except Exception as e:
            logger.error(f"❌ Import FAILED: {module_name} - {e}")
            failed.append(module_name)
            
    return failed

def check_tool_instantiation():
    """Try to instantiate key tools to ensure singletons work"""
    try:
        from haitham_voice_agent.tools.smart_organizer import get_organizer
        get_organizer()
        logger.info("✅ Tool OK: SmartOrganizer")
    except Exception as e:
        logger.error(f"❌ Tool FAILED: SmartOrganizer - {e}")
        return ["SmartOrganizer"]
        
    try:
        from haitham_voice_agent.tools.deep_organizer import get_deep_organizer
        get_deep_organizer()
        logger.info("✅ Tool OK: DeepOrganizer")
    except Exception as e:
        logger.error(f"❌ Tool FAILED: DeepOrganizer - {e}")
        return ["DeepOrganizer"]

    return []

if __name__ == "__main__":
    logger.info("Starting System Integrity Check...")
    
    import_errors = check_imports()
    tool_errors = check_tool_instantiation()
    
    if import_errors or tool_errors:
        logger.error("🚨 INTEGRITY CHECK FAILED! Fix errors before starting.")
        sys.exit(1)
    else:
        logger.info("✨ All Systems Go! Integrity check passed.")
        sys.exit(0)
