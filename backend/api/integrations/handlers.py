from typing import Dict, Any, Optional
import json

class IntegrationHandler:
    """Base class for integration handlers."""
    
    def __init__(self):
        self.config = {}
    
    async def send_notification(self, data: Dict[str, Any]) -> bool:
        """
        Send notification through the integration.
        
        Args:
            data: Notification data
            
        Returns:
            bool indicating success
        """
        raise NotImplementedError
    
    def validate_config(self) -> bool:
        """
        Validate integration configuration.
        
        Returns:
            bool indicating if config is valid
        """
        raise NotImplementedError

class SlackHandler(IntegrationHandler):
    """Handler for Slack integration."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        super().__init__()
        self.webhook_url = webhook_url
    
    async def send_notification(self, data: Dict[str, Any]) -> bool:
        try:
            # Mock Slack API call
            return True
        except Exception:
            return False
    
    def validate_config(self) -> bool:
        return self.webhook_url is not None

class JiraHandler(IntegrationHandler):
    """Handler for Jira integration."""
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
    
    async def send_notification(self, data: Dict[str, Any]) -> bool:
        try:
            # Mock Jira API call
            return True
        except Exception:
            return False
    
    def validate_config(self) -> bool:
        return self.api_url is not None and self.api_key is not None 