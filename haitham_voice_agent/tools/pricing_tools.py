import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from haitham_voice_agent.token_tracker import get_tracker

logger = logging.getLogger(__name__)

class PricingTools:
    """
    Tools for managing API pricing configuration.
    Allows dynamic updates to cost tracking without code changes.
    """
    
    def __init__(self):
        self.tracker = get_tracker()
        self.pricing_file = self.tracker.pricing_file
        
    async def get_current_pricing(self) -> Dict[str, Any]:
        """
        Get the current pricing configuration.
        """
        return self.tracker.PRICING
        
    async def update_pricing(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update pricing for specific models.
        
        Args:
            updates: Dictionary of model updates. 
                     Example: {"gpt-4o": {"input": 0.0025, "output": 0.01}}
        """
        try:
            current_pricing = await self.get_current_pricing()
            
            # Apply updates
            for model, rates in updates.items():
                if model in current_pricing:
                    current_pricing[model].update(rates)
                else:
                    current_pricing[model] = rates
                
                # Update timestamp
                from datetime import datetime
                current_pricing[model]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            
            # Save to file
            with open(self.pricing_file, "w") as f:
                json.dump(current_pricing, f, indent=2)
                
            # Reload in tracker
            self.tracker.reload_pricing()
            
            return {
                "success": True, 
                "message": f"Updated pricing for {len(updates)} models.",
                "updated_models": list(updates.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to update pricing: {e}")
            return {"error": True, "message": str(e)}

    async def check_pricing_updates(self) -> Dict[str, Any]:
        """
        Check if pricing is outdated (older than 30 days).
        Note: This does not fetch new prices from the web, but warns if manual update is needed.
        """
        outdated = []
        from datetime import datetime, timedelta
        
        current_pricing = await self.get_current_pricing()
        threshold = datetime.now() - timedelta(days=30)
        
        for model, data in current_pricing.items():
            last_updated = data.get("last_updated")
            if not last_updated:
                outdated.append(model)
                continue
                
            try:
                date_obj = datetime.strptime(last_updated, "%Y-%m-%d")
                if date_obj < threshold:
                    outdated.append(model)
            except:
                pass
                
        if outdated:
            return {
                "status": "outdated",
                "message": f"Pricing for {len(outdated)} models hasn't been updated in 30 days.",
                "models": outdated,
                "recommendation": "Please ask me to 'Search for latest API pricing' to update these."
            }
            
        return {"status": "current", "message": "All pricing configurations are up to date."}
