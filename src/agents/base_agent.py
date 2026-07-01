"""Base agent class for all agentic AI agents"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agentic AI agents"""

    def __init__(self, agent_name: str, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize base agent
        Args:
            agent_name: Name of the agent
            model: Claude model to use
        """
        self.agent_name = agent_name
        self.model = model
        self.execution_history = []

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic
        Must be implemented by subclasses
        """
        pass

    def _log_execution(self, input_data: Dict[str, Any], output: Dict[str, Any],
                      duration_ms: float) -> None:
        """Log agent execution"""
        execution_record = {
            "agent": self.agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "input_keys": list(input_data.keys()),
            "output_keys": list(output.keys()),
            "duration_ms": duration_ms
        }
        self.execution_history.append(execution_record)
        logger.info(f"Agent {self.agent_name} executed: {execution_record}")

    def get_execution_history(self) -> list:
        """Get execution history of this agent"""
        return self.execution_history

    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with given parameters"""
        return template.format(**kwargs)

    def _validate_input(self, required_fields: list, input_data: Dict[str, Any]) -> bool:
        """
        Validate input has required fields
        Args:
            required_fields: List of field names required
            input_data: Input data to validate
        Returns:
            True if all required fields present, False otherwise
        """
        missing = [f for f in required_fields if f not in input_data or input_data[f] is None]
        if missing:
            logger.warning(f"Missing fields in {self.agent_name}: {missing}")
            return False
        return True
