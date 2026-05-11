from typing import Dict, Any, List
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all specialized agents."""
    
    def __init__(self, name: str, llm_client):
        self.name = name
        self.llm = llm_client
        self.memory = []  # Agent's memory
        self.logger = logging.getLogger(f"agent.{name}")
    
    
    async def perceive(self, environment: Dict) -> Dict:
        """
        Observe the environment and extract relevant information.
        
        Args:
            environment: Current state (products, user prefs, past results, etc.)
        
        Returns:
            Dict of observations relevant to this agent's specialty
            
        Note: Subclasses should implement this to extract domain-specific info
        """
        raise NotImplementedError("Subclasses must implement perceive()")

    async def decide(self, observations: Dict) -> Dict:
        """Make decisions based on observations."""
        pass

    async def safe_decide(self, observations: Dict) -> Dict:
        """Wrapper with error handling for decide()."""
        try:
            return await self.decide(observations)
        except Exception as e:
            self.logger.error(f"{self.name} decision failed: {e}")
            return {"error": str(e), "fallback": True}

    
    async def act(self, decision: Dict) -> Any:
        """Execute the decision."""
        pass
    def add_to_memory(self, observation: Dict) -> None:
        """Store observation in agent's memory."""
        self.memory.append({
            'timestamp': datetime.now(),
            'observation': observation
        })
        # Limit memory size to prevent unbounded growth
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]

    def get_recent_memory(self, n: int = 10) -> List[Dict]:
        """Retrieve n most recent memories."""
        return self.memory[-n:]

    def clear_memory(self) -> None:
        """Clear agent's memory."""
        self.memory = []
