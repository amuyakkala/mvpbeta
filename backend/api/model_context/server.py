from typing import Dict, Any, Optional
import json

class ModelContextServer:
    """Server for managing model context and configurations."""
    
    def __init__(self):
        self.contexts = {}
        self.configs = {}
    
    async def get_context(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get context for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Dict containing model context
        """
        return self.contexts.get(model_id)
    
    async def set_context(self, model_id: str, context: Dict[str, Any]) -> bool:
        """
        Set context for a specific model.
        
        Args:
            model_id: ID of the model
            context: Context data
            
        Returns:
            bool indicating success
        """
        try:
            self.contexts[model_id] = context
            return True
        except Exception:
            return False
    
    async def get_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Dict containing model configuration
        """
        return self.configs.get(model_id)
    
    async def set_config(self, model_id: str, config: Dict[str, Any]) -> bool:
        """
        Set configuration for a specific model.
        
        Args:
            model_id: ID of the model
            config: Configuration data
            
        Returns:
            bool indicating success
        """
        try:
            self.configs[model_id] = config
            return True
        except Exception:
            return False
    
    async def validate_context(self, context: Dict[str, Any]) -> bool:
        """
        Validate model context.
        
        Args:
            context: Context to validate
            
        Returns:
            bool indicating if context is valid
        """
        required_fields = ["model_type", "version", "parameters"]
        return all(field in context for field in required_fields)
    
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate model configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool indicating if config is valid
        """
        required_fields = ["batch_size", "learning_rate", "epochs"]
        return all(field in config for field in required_fields) 