from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return the result.
        
        Args:
            data: Input data to process
            
        Returns:
            Dict containing the processing results
        """
        pass
    
    @abstractmethod
    async def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate the input data.
        
        Args:
            data: Input data to validate
            
        Returns:
            bool indicating if the data is valid
        """
        pass
    
    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the agent.
        
        Returns:
            Dict containing agent metadata
        """
        pass 