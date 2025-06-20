"""
Core Agent Framework for AI Business Intelligence System

This module provides the base architecture for all AI agents in the system,
including communication protocols, task management, and agent lifecycle.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class AgentType(Enum):
    """Agent type enumeration"""
    DATA_COLLECTOR = "data_collector"
    ANALYZER = "analyzer"
    INSIGHT_GENERATOR = "insight_generator"
    ACTION_EXECUTOR = "action_executor"


class Message(BaseModel):
    """Message model for agent communication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    recipient: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=10)


class Task(BaseModel):
    """Task model for agent task management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    agent_type: AgentType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """
    Base class for all agents in the system
    
    Provides common functionality for task processing, message handling,
    and agent lifecycle management
    """
    
    def __init__(self, agent_id: str, agent_type: AgentType, name: str, task_coordinator=None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.status = AgentStatus.IDLE
        self.task_queue: List[Task] = []
        self.message_queue: List[Message] = []
        self.completed_tasks: List[Task] = []
        self.metrics: Dict[str, Any] = {}
        self.capabilities: List[str] = []
        self.task_coordinator = task_coordinator
        
        # Add missing attributes for API compatibility
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        
        logger.info(
            "Agent initialized",
            agent_id=self.agent_id,
            agent_type=agent_type.value,
            name=name
        )
    
    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """
        Process a task and return results
        
        Args:
            task: Task to process
            
        Returns:
            Dictionary containing task results
        """
        pass
    
    @abstractmethod
    async def handle_message(self, message: Message) -> Optional[Message]:
        """
        Handle incoming messages
        
        Args:
            message: Incoming message
            
        Returns:
            Optional response message
        """
        pass
    
    async def start(self):
        """Start the agent and begin processing tasks"""
        self.status = AgentStatus.IDLE
        self.last_active = datetime.utcnow()
        logger.info("Agent started", agent_id=self.agent_id)
        
        # Start background task processing
        asyncio.create_task(self._task_processor())
        asyncio.create_task(self._message_processor())
    
    async def stop(self):
        """Stop the agent and clean up resources"""
        self.status = AgentStatus.OFFLINE
        logger.info("Agent stopped", agent_id=self.agent_id)
    
    async def add_task(self, task: Task):
        """Add a task to the agent's task queue"""
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
        logger.info(
            "Task added to queue",
            agent_id=self.agent_id,
            task_id=task.id,
            task_name=task.name
        )
    
    async def send_message(self, message: Message):
        """Send a message to another agent"""
        # In a real implementation, this would use a message broker
        # For now, we'll simulate direct message passing
        logger.info(
            "Message sent",
            sender=self.agent_id,
            recipient=message.recipient,
            message_type=message.message_type
        )
    
    async def receive_message(self, message: Message):
        """Receive a message from another agent"""
        self.message_queue.append(message)
        logger.info(
            "Message received",
            recipient=self.agent_id,
            sender=message.sender,
            message_type=message.message_type
        )
    
    async def _task_processor(self):
        """Background task processor"""
        while self.status != AgentStatus.OFFLINE:
            if self.task_queue and self.status == AgentStatus.IDLE:
                task = self.task_queue.pop(0)
                await self._execute_task(task)
            await asyncio.sleep(1)
    
    async def _message_processor(self):
        """Background message processor"""
        while self.status != AgentStatus.OFFLINE:
            if self.message_queue:
                message = self.message_queue.pop(0)
                await self.handle_message(message)
            await asyncio.sleep(0.1)
    
    async def _execute_task(self, task: Task):
        """Execute a task and update its status"""
        try:
            self.status = AgentStatus.BUSY
            self.update_last_active()
            task.status = "running"
            
            logger.info(
                "Task execution started",
                agent_id=self.agent_id,
                task_id=task.id,
                task_name=task.name
            )
            
            # Execute the task
            result = await self.process_task(task)
            
            # Update task with results
            task.result = result
            task.status = "completed"
            
            # Report task completion to coordinator
            await self._report_task_completion(task.id, result)
            
            # Update metrics
            self.metrics["tasks_completed"] = self.metrics.get("tasks_completed", 0) + 1
            
            logger.info(
                "Task execution completed",
                agent_id=self.agent_id,
                task_id=task.id,
                task_name=task.name
            )
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            
            # Report task failure to coordinator
            await self._report_task_completion(task.id, {"error": str(e)})
            
            self.metrics["tasks_failed"] = self.metrics.get("tasks_failed", 0) + 1
            
            logger.error(
                "Task execution failed",
                agent_id=self.agent_id,
                task_id=task.id,
                task_name=task.name,
                error=str(e)
            )
            
        finally:
            self.status = AgentStatus.IDLE
    
    async def _report_task_completion(self, task_id: str, result: Dict[str, Any]):
        """Report task completion to the task coordinator"""
        try:
            if self.task_coordinator:
                await self.task_coordinator.update_task_result(task_id, result)
            else:
                logger.warning(
                    "No task coordinator available to report task completion",
                    task_id=task_id,
                    agent_id=self.agent_id
                )
        except Exception as e:
            logger.error(
                "Failed to report task completion",
                task_id=task_id,
                error=str(e),
                agent_id=self.agent_id
            )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status.value,
            "queue_size": len(self.task_queue),
            "message_queue_size": len(self.message_queue),
            "metrics": self.metrics,
            "capabilities": self.capabilities
        }

    def update_last_active(self):
        """Update the last active timestamp"""
        self.last_active = datetime.utcnow()


class AgentRegistry:
    """Registry for managing all agents in the system"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[AgentType, List[str]] = {agent_type: [] for agent_type in AgentType}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent in the registry"""
        # print(f"DEBUG: register_agent called on registry id={id(self)}")
        # print(f"DEBUG: Registering agent {agent.agent_id} of type {agent.agent_type} ({type(agent.agent_type)})")
        self.agents[agent.agent_id] = agent
        self.agent_types[agent.agent_type].append(agent.agent_id)
        
        logger.info(
            "Agent registered",
            agent_id=agent.agent_id,
            agent_type=agent.agent_type.value
        )
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the registry"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            self.agent_types[agent.agent_type].remove(agent_id)
            del self.agents[agent_id]
            
            logger.info(
                "Agent unregistered",
                agent_id=agent_id
            )
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """Get all agents of a specific type"""
        # print(f"DEBUG: get_agents_by_type called on registry id={id(self)} for type={agent_type} ({type(agent_type)})")
        # print(f"DEBUG: Registered agent_types: {[ (a.agent_id, a.agent_type, type(a.agent_type)) for a in self.get_all_agents() ]}")
        return [self.agents[agent_id] for agent_id in self.agent_types[agent_type]]
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self.agents.values())
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status and statistics"""
        return {
            "total_agents": len(self.agents),
            "agents_by_type": {
                agent_type.value: len(agent_ids)
                for agent_type, agent_ids in self.agent_types.items()
            },
            "agent_status": {
                agent_id: agent.get_health_status()
                for agent_id, agent in self.agents.items()
            }
        }


# Global agent registry instance
AgentRegistryGlobal = AgentRegistry() 