"""
Communication Module for AI Agent System

Handles message passing, coordination, and communication protocols
between different agents in the system.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import structlog
from pydantic import BaseModel

from .agent_framework import AgentType, Message, BaseAgent,  AgentRegistryGlobal

logger = structlog.get_logger(__name__)


class CommunicationProtocol(BaseModel):
    """Protocol definition for agent communication"""
    protocol_id: str
    version: str
    message_types: List[str]
    encoding: str = "json"
    compression: bool = False


class MessageBroker:
    """
    Message broker for handling communication between agents
    
    Provides pub/sub, direct messaging, and broadcast capabilities
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[BaseAgent]] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.message_history: List[Message] = []
        self.max_history_size = 1000
        
        logger.info("Message broker initialized")
    
    async def publish(self, topic: str, message: Message):
        """Publish a message to a topic"""
        if topic in self.subscribers:
            for subscriber in self.subscribers[topic]:
                await subscriber.receive_message(message)
        
        # Store in history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history_size:
            self.message_history.pop(0)
        
        logger.info(
            "Message published",
            topic=topic,
            message_id=message.id,
            sender=message.sender
        )
    
    async def subscribe(self, topic: str, agent: BaseAgent):
        """Subscribe an agent to a topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        
        if agent not in self.subscribers[topic]:
            self.subscribers[topic].append(agent)
            
        logger.info(
            "Agent subscribed to topic",
            agent_id=agent.agent_id,
            topic=topic
        )
    
    async def unsubscribe(self, topic: str, agent: BaseAgent):
        """Unsubscribe an agent from a topic"""
        if topic in self.subscribers and agent in self.subscribers[topic]:
            self.subscribers[topic].remove(agent)
            
        logger.info(
            "Agent unsubscribed from topic",
            agent_id=agent.agent_id,
            topic=topic
        )
    
    async def broadcast(self, message: Message, exclude_sender: bool = True):
        """Broadcast a message to all agents"""
        for agent in AgentRegistryGlobal.get_all_agents():
            if exclude_sender and agent.agent_id == message.sender:
                continue
            await agent.receive_message(message)
        
        logger.info(
            "Message broadcasted",
            message_id=message.id,
            sender=message.sender,
            recipients_count=len(AgentRegistryGlobal.get_all_agents())
        )
    
    async def direct_message(self, recipient_id: str, message: Message) -> bool:
        """Send a direct message to a specific agent"""
        recipient = AgentRegistryGlobal.get_agent(recipient_id)
        if recipient:
            await recipient.receive_message(message)
            logger.info(
                "Direct message sent",
                sender=message.sender,
                recipient=recipient_id,
                message_id=message.id
            )
            return True
        else:
            logger.warning(
                "Direct message failed - recipient not found",
                sender=message.sender,
                recipient=recipient_id,
                message_id=message.id
            )
            return False
    
    def get_message_history(self, limit: int = 100) -> List[Message]:
        """Get recent message history"""
        return self.message_history[-limit:]
    
    def get_subscriber_count(self, topic: str) -> int:
        """Get number of subscribers for a topic"""
        return len(self.subscribers.get(topic, []))


class TaskCoordinator:
    """
    Task coordinator for managing task distribution and execution
    
    Handles task routing, load balancing, and result aggregation
    """
    
    def __init__(self, message_broker: MessageBroker):
        self.message_broker = message_broker
        self.task_routing: Dict[str, str] = {}  # task_id -> agent_id
        self.task_results: Dict[str, Any] = {}
        self.agent_loads: Dict[str, int] = {}
        
        logger.info("Task coordinator initialized")
    
    async def submit_task(self, task_type: str, parameters: Dict[str, Any], 
                         priority: int = 1) -> str:
        """Submit a task for execution"""
        from .agent_framework import Task, AgentType
        
        # Determine which agent type should handle this task
        agent_type = self._get_agent_type_for_task(task_type)
        
        # Find available agents of the required type
        available_agents = AgentRegistryGlobal.get_agents_by_type(agent_type)
        
        if not available_agents:
            raise ValueError(f"No available agents for task type: {task_type}")
        
        # Select the least loaded agent
        selected_agent = self._select_agent(available_agents)
        
        # Create task
        task = Task(
            name=task_type,
            description=f"Task of type {task_type}",
            agent_type=agent_type,
            parameters=parameters,
            priority=priority
        )
        
        # Route task to selected agent
        await selected_agent.add_task(task)
        self.task_routing[task.id] = selected_agent.agent_id
        self.agent_loads[selected_agent.agent_id] = self.agent_loads.get(selected_agent.agent_id, 0) + 1
        
        logger.info(
            "Task submitted",
            task_id=task.id,
            task_type=task_type,
            assigned_agent=selected_agent.agent_id
        )
        
        return task.id
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed task"""
        return self.task_results.get(task_id)
    
    async def wait_for_task_completion(self, task_id: str, timeout: int = 60) -> Optional[Dict[str, Any]]:
        """Wait for a task to complete and return its result"""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < timeout:
            if task_id in self.task_results:
                return self.task_results[task_id]
            await asyncio.sleep(1)
        
        logger.warning(
            "Task completion timeout",
            task_id=task_id,
            timeout=timeout
        )
        return None
    
    def _get_agent_type_for_task(self, task_type: str) -> 'AgentType':
        """Determine which agent type should handle a given task type"""
        task_agent_mapping = {
            "collect_data": AgentType.DATA_COLLECTOR,
            "collect_market_data": AgentType.DATA_COLLECTOR,
            
            "analyze_data": AgentType.ANALYZER,
            "generate_insights": AgentType.INSIGHT_GENERATOR,
            "execute_action": AgentType.ACTION_EXECUTOR,
            "web_scraping": AgentType.DATA_COLLECTOR,
            "api_integration": AgentType.DATA_COLLECTOR,
            "trend_analysis": AgentType.ANALYZER,
            "pattern_recognition": AgentType.ANALYZER,
            "business_intelligence": AgentType.INSIGHT_GENERATOR,
            "report_generation": AgentType.ACTION_EXECUTOR,
            "notification": AgentType.ACTION_EXECUTOR,

            # New demo task mappings
            "analyze_stocks": AgentType.ANALYZER,
            "analyze_forex": AgentType.ANALYZER,
            "analyze_crypto": AgentType.ANALYZER,
            "generate_comprehensive_insights": AgentType.INSIGHT_GENERATOR,
            "anomaly_detection": AgentType.ANALYZER,
            "statistical_analysis": AgentType.ANALYZER,
            "create_recommendations": AgentType.INSIGHT_GENERATOR
        }
        
        return task_agent_mapping.get(task_type, AgentType.ANALYZER)
    
    def _select_agent(self, available_agents: List[BaseAgent]) -> BaseAgent:
        """Select the best agent based on load and status"""
        # Filter agents that are not offline
        active_agents = [agent for agent in available_agents if agent.status.value != "offline"]
        
        if not active_agents:
            raise ValueError("No active agents available")
        
        # Select agent with lowest load
        selected_agent = min(active_agents, key=lambda a: self.agent_loads.get(a.agent_id, 0))
        
        return selected_agent
    
    async def update_task_result(self, task_id: str, result: Dict[str, Any]):
        """Update task result when completed"""
        self.task_results[task_id] = result
        
        # Update agent load
        if task_id in self.task_routing:
            agent_id = self.task_routing[task_id]
            self.agent_loads[agent_id] = max(0, self.agent_loads.get(agent_id, 1) - 1)
        
        logger.info(
            "Task result updated",
            task_id=task_id,
            result_keys=list(result.keys())
        )


class CommunicationManager:
    """
    High-level communication manager for the agent system
    
    Provides unified interface for all communication operations
    """
    
    def __init__(self):
        self.message_broker = MessageBroker()
        self.task_coordinator = TaskCoordinator(self.message_broker)
        self.protocols: Dict[str, CommunicationProtocol] = {}
        
        logger.info("Communication manager initialized")
    
    async def initialize_protocols(self):
        """Initialize communication protocols"""
        # Define standard protocols
        protocols = [
            CommunicationProtocol(
                protocol_id="task_execution",
                version="1.0",
                message_types=["task_request", "task_result", "task_status"]
            ),
            CommunicationProtocol(
                protocol_id="data_sharing",
                version="1.0",
                message_types=["data_request", "data_response", "data_update"]
            ),
            CommunicationProtocol(
                protocol_id="coordination",
                version="1.0",
                message_types=["sync_request", "sync_response", "broadcast"]
            )
        ]
        
        for protocol in protocols:
            self.protocols[protocol.protocol_id] = protocol
        
        logger.info(
            "Communication protocols initialized",
            protocol_count=len(protocols)
        )
    
    async def send_task_request(self, task_type: str, parameters: Dict[str, Any], 
                               priority: int = 1) -> str:
        """Send a task request and return task ID"""
        return await self.task_coordinator.submit_task(task_type, parameters, priority)
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task result by ID"""
        return await self.task_coordinator.get_task_result(task_id)
    
    async def broadcast_message(self, message_type: str, content: Dict[str, Any], 
                               sender: str):
        """Broadcast a message to all agents"""
        message = Message(
            sender=sender,
            recipient="broadcast",
            message_type=message_type,
            content=content
        )
        await self.message_broker.broadcast(message)
    
    async def subscribe_to_topic(self, topic: str, agent: BaseAgent):
        """Subscribe an agent to a topic"""
        await self.message_broker.subscribe(topic, agent)
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        return {
            "message_history_size": len(self.message_broker.message_history),
            "active_subscriptions": {
                topic: len(subscribers)
                for topic, subscribers in self.message_broker.subscribers.items()
            },
            "task_routing_count": len(self.task_coordinator.task_routing),
            "completed_tasks": len(self.task_coordinator.task_results),
            "agent_loads": self.task_coordinator.agent_loads
        }


# Global communication manager instance
communication_manager = CommunicationManager()