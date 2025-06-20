"""
Tests for AI Agent System

Tests for:
- Agent framework functionality
- Individual agent capabilities
- Agent communication
- Task processing
- Error handling
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd
import numpy as np

# Import modules to test
from core.agent_framework import BaseAgent, AgentType, Task, Message, AgentStatus, AgentRegistry
from core.communication import CommunicationManager, MessageBroker, TaskCoordinator
from agents.data_collector_agent import DataCollectorAgent, create_data_collector_agent
from agents.analyzer_agent import AnalyzerAgent, create_analyzer_agent
from agents.insight_generator_agent import InsightGeneratorAgent, create_insight_generator_agent
from agents.action_executor_agent import ActionExecutorAgent, create_action_executor_agent


class TestBaseAgent:
    """Test cases for BaseAgent class"""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance"""
        return BaseAgent(
            agent_id="test_agent_001",
            agent_type=AgentType.DATA_COLLECTOR,
            name="Test Agent"
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.agent_id == "test_agent_001"
        assert agent.agent_type == AgentType.DATA_COLLECTOR
        assert agent.name == "Test Agent"
        assert agent.status == AgentStatus.OFFLINE
        assert len(agent.capabilities) == 0
        assert len(agent.task_queue) == 0
        assert len(agent.completed_tasks) == 0
    
    def test_agent_health_status(self, agent):
        """Test agent health status"""
        health = agent.get_health_status()
        assert "status" in health
        assert "last_active" in health
        assert "task_count" in health
        assert "error_count" in health
    
    @pytest.mark.asyncio
    async def test_agent_start_stop(self, agent):
        """Test agent start and stop functionality"""
        # Test start
        await agent.start()
        assert agent.status == AgentStatus.ONLINE
        
        # Test stop
        await agent.stop()
        assert agent.status == AgentStatus.OFFLINE
    
    @pytest.mark.asyncio
    async def test_task_processing(self, agent):
        """Test task processing functionality"""
        # Create a test task
        task = Task(
            name="test_task",
            description="Test task description",
            agent_type=AgentType.DATA_COLLECTOR,
            parameters={"test_param": "test_value"},
            priority=1
        )
        
        # Add task to agent
        await agent.add_task(task)
        assert len(agent.task_queue) == 1
        
        # Process task (mock the process_task method)
        with patch.object(agent, 'process_task', return_value={"result": "success"}):
            result = await agent.process_next_task()
            assert result is not None
            assert len(agent.completed_tasks) == 1
    
    @pytest.mark.asyncio
    async def test_message_handling(self, agent):
        """Test message handling functionality"""
        # Create a test message
        message = Message(
            sender="sender_agent",
            recipient="test_agent_001",
            message_type="test_message",
            content={"test": "data"}
        )
        
        # Test message receiving
        await agent.receive_message(message)
        assert len(agent.message_queue) == 1
        
        # Test message processing (mock the handle_message method)
        with patch.object(agent, 'handle_message', return_value=None):
            response = await agent.process_next_message()
            assert response is None


class TestAgentRegistry:
    """Test cases for AgentRegistry class"""
    
    @pytest.fixture
    def registry(self):
        """Create a test registry instance"""
        return AgentRegistry()
    
    @pytest.fixture
    def test_agent(self):
        """Create a test agent"""
        return BaseAgent(
            agent_id="test_agent_001",
            agent_type=AgentType.DATA_COLLECTOR,
            name="Test Agent"
        )
    
    def test_registry_initialization(self, registry):
        """Test registry initialization"""
        assert len(registry.agents) == 0
        assert registry.agent_count == 0
    
    def test_agent_registration(self, registry, test_agent):
        """Test agent registration"""
        registry.register_agent(test_agent)
        assert len(registry.agents) == 1
        assert registry.agent_count == 1
        assert registry.get_agent("test_agent_001") == test_agent
    
    def test_agent_unregistration(self, registry, test_agent):
        """Test agent unregistration"""
        registry.register_agent(test_agent)
        registry.unregister_agent("test_agent_001")
        assert len(registry.agents) == 0
        assert registry.agent_count == 0
        assert registry.get_agent("test_agent_001") is None
    
    def test_get_agents_by_type(self, registry):
        """Test getting agents by type"""
        # Create agents of different types
        data_collector = BaseAgent("dc_001", AgentType.DATA_COLLECTOR, "Data Collector")
        analyzer = BaseAgent("an_001", AgentType.ANALYZER, "Analyzer")
        
        registry.register_agent(data_collector)
        registry.register_agent(analyzer)
        
        data_collectors = registry.get_agents_by_type(AgentType.DATA_COLLECTOR)
        analyzers = registry.get_agents_by_type(AgentType.ANALYZER)
        
        assert len(data_collectors) == 1
        assert len(analyzers) == 1
        assert data_collectors[0].agent_id == "dc_001"
        assert analyzers[0].agent_id == "an_001"
    
    def test_get_all_agents(self, registry, test_agent):
        """Test getting all agents"""
        registry.register_agent(test_agent)
        all_agents = registry.get_all_agents()
        assert len(all_agents) == 1
        assert all_agents[0] == test_agent


class TestCommunicationManager:
    """Test cases for CommunicationManager class"""
    
    @pytest.fixture
    def comm_manager(self):
        """Create a test communication manager"""
        return CommunicationManager()
    
    @pytest.mark.asyncio
    async def test_initialization(self, comm_manager):
        """Test communication manager initialization"""
        await comm_manager.initialize_protocols()
        assert len(comm_manager.protocols) > 0
    
    @pytest.mark.asyncio
    async def test_task_submission(self, comm_manager):
        """Test task submission"""
        # Mock the task coordinator
        with patch.object(comm_manager.task_coordinator, 'submit_task', return_value="task_123"):
            task_id = await comm_manager.send_task_request(
                "test_task",
                {"param": "value"},
                priority=1
            )
            assert task_id == "task_123"
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, comm_manager):
        """Test message broadcasting"""
        # Mock the message broker
        with patch.object(comm_manager.message_broker, 'broadcast'):
            await comm_manager.broadcast_message(
                "test_message",
                {"content": "test"},
                "sender_agent"
            )
            comm_manager.message_broker.broadcast.assert_called_once()


class TestDataCollectorAgent:
    """Test cases for DataCollectorAgent class"""
    
    @pytest.fixture
    def data_collector(self):
        """Create a test data collector agent"""
        return create_data_collector_agent("test_dc_001")
    
    def test_agent_creation(self, data_collector):
        """Test data collector agent creation"""
        assert data_collector.agent_id == "test_dc_001"
        assert data_collector.agent_type == AgentType.DATA_COLLECTOR
        assert "web_scraping" in data_collector.capabilities
        assert "api_integration" in data_collector.capabilities
    
    @pytest.mark.asyncio
    async def test_web_scraping_task(self, data_collector):
        """Test web scraping task processing"""
        task = Task(
            name="web_scraping",
            description="Test web scraping",
            agent_type=AgentType.DATA_COLLECTOR,
            parameters={
                "urls": ["https://example.com"],
                "selectors": {"title": "h1"},
                "extract_text": True
            }
        )
        
        # Mock requests.get to avoid actual HTTP calls
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><h1>Test Title</h1></html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await data_collector.process_task(task)
            
            assert result["task_type"] == "web_scraping"
            assert "scraped_data" in result
            assert len(result["scraped_data"]) > 0
    
    @pytest.mark.asyncio
    async def test_api_integration_task(self, data_collector):
        """Test API integration task processing"""
        task = Task(
            name="api_integration",
            description="Test API integration",
            agent_type=AgentType.DATA_COLLECTOR,
            parameters={
                "api_url": "https://api.example.com/data",
                "method": "GET",
                "headers": {"Authorization": "Bearer token"}
            }
        )
        
        # Mock requests.request to avoid actual HTTP calls
        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test_data"}
            mock_response.status_code = 200
            mock_request.return_value = mock_response
            
            result = await data_collector.process_task(task)
            
            assert result["task_type"] == "api_integration"
            assert "api_data" in result
            assert result["api_data"]["data"] == "test_data"
    
    @pytest.mark.asyncio
    async def test_data_collection_task(self, data_collector):
        """Test general data collection task processing"""
        task = Task(
            name="collect_data",
            description="Test data collection",
            agent_type=AgentType.DATA_COLLECTOR,
            parameters={
                "data_sources": ["web", "api"],
                "collection_type": "standard",
                "parameters": {}
            }
        )
        
        # Mock the specific collection methods
        with patch.object(data_collector, '_collect_from_web', return_value={"web_data": "test"}):
            with patch.object(data_collector, '_collect_from_api', return_value={"api_data": "test"}):
                result = await data_collector.process_task(task)
                
                assert result["task_type"] == "collect_data"
                assert "collected_data" in result
                assert len(result["collected_data"]) > 0


class TestAnalyzerAgent:
    """Test cases for AnalyzerAgent class"""
    
    @pytest.fixture
    def analyzer(self):
        """Create a test analyzer agent"""
        return create_analyzer_agent("test_an_001")
    
    def test_agent_creation(self, analyzer):
        """Test analyzer agent creation"""
        assert analyzer.agent_id == "test_an_001"
        assert analyzer.agent_type == AgentType.ANALYZER
        assert "statistical_analysis" in analyzer.capabilities
        assert "trend_analysis" in analyzer.capabilities
    
    @pytest.mark.asyncio
    async def test_trend_analysis_task(self, analyzer):
        """Test trend analysis task processing"""
        # Create sample time series data
        sample_data = {
            "data": [
                {"timestamp": "2023-01-01", "value": 100},
                {"timestamp": "2023-01-02", "value": 105},
                {"timestamp": "2023-01-03", "value": 110},
                {"timestamp": "2023-01-04", "value": 115},
                {"timestamp": "2023-01-05", "value": 120}
            ]
        }
        
        task = Task(
            name="analyze_trends",
            description="Test trend analysis",
            agent_type=AgentType.ANALYZER,
            parameters=sample_data
        )
        
        result = await analyzer.process_task(task)
        
        assert result["task_type"] == "analyze_trends"
        assert "trend_analysis" in result
        assert "linear_trend" in result["trend_analysis"]
        assert result["trend_analysis"]["linear_trend"]["trend_direction"] == "increasing"
    
    @pytest.mark.asyncio
    async def test_pattern_recognition_task(self, analyzer):
        """Test pattern recognition task processing"""
        # Create sample data with patterns
        sample_data = {
            "data": [
                {"id": 1, "value": 10, "category": "A"},
                {"id": 2, "value": 15, "category": "A"},
                {"id": 3, "value": 20, "category": "B"},
                {"id": 4, "value": 25, "category": "B"},
                {"id": 5, "value": 30, "category": "A"}
            ]
        }
        
        task = Task(
            name="pattern_recognition",
            description="Test pattern recognition",
            agent_type=AgentType.ANALYZER,
            parameters=sample_data
        )
        
        result = await analyzer.process_task(task)
        
        assert result["task_type"] == "pattern_recognition"
        assert "patterns" in result
        assert "numerical_patterns" in result["patterns"]
    
    @pytest.mark.asyncio
    async def test_anomaly_detection_task(self, analyzer):
        """Test anomaly detection task processing"""
        # Create sample data with anomalies
        sample_data = {
            "data": [1, 2, 3, 100, 4, 5, 6, 200, 7, 8, 9]  # 100 and 200 are anomalies
        }
        
        task = Task(
            name="anomaly_detection",
            description="Test anomaly detection",
            agent_type=AgentType.ANALYZER,
            parameters=sample_data
        )
        
        result = await analyzer.process_task(task)
        
        assert result["task_type"] == "anomaly_detection"
        assert "anomalies" in result
        assert result["total_anomalies"] > 0
    
    @pytest.mark.asyncio
    async def test_statistical_analysis_task(self, analyzer):
        """Test statistical analysis task processing"""
        # Create sample data
        sample_data = {
            "data": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        }
        
        task = Task(
            name="statistical_analysis",
            description="Test statistical analysis",
            agent_type=AgentType.ANALYZER,
            parameters=sample_data
        )
        
        result = await analyzer.process_task(task)
        
        assert result["task_type"] == "statistical_analysis"
        assert "statistics" in result
        assert "descriptive_stats" in result["statistics"]


class TestInsightGeneratorAgent:
    """Test cases for InsightGeneratorAgent class"""
    
    @pytest.fixture
    def insight_generator(self):
        """Create a test insight generator agent"""
        return create_insight_generator_agent("test_ig_001")
    
    def test_agent_creation(self, insight_generator):
        """Test insight generator agent creation"""
        assert insight_generator.agent_id == "test_ig_001"
        assert insight_generator.agent_type == AgentType.INSIGHT_GENERATOR
        assert "insight_generation" in insight_generator.capabilities
        assert "recommendation_creation" in insight_generator.capabilities
    
    @pytest.mark.asyncio
    async def test_insight_generation_task(self, insight_generator):
        """Test insight generation task processing"""
        # Create sample analysis results
        analysis_results = {
            "trend_analysis": {
                "linear_trend": {
                    "slope": 0.5,
                    "r_squared": 0.8,
                    "trend_direction": "increasing"
                }
            },
            "anomaly_detection": {
                "total_anomalies": 2
            }
        }
        
        task = Task(
            name="generate_insights",
            description="Test insight generation",
            agent_type=AgentType.INSIGHT_GENERATOR,
            parameters={
                "analysis_results": analysis_results,
                "business_context": {"industry": "technology"},
                "categories": ["trends", "anomalies"]
            }
        )
        
        result = await insight_generator.process_task(task)
        
        assert result["task_type"] == "generate_insights"
        assert "insights" in result
        assert result["insight_count"] > 0
    
    @pytest.mark.asyncio
    async def test_recommendation_creation_task(self, insight_generator):
        """Test recommendation creation task processing"""
        # Create sample insights
        insights = [
            {
                "insight_id": "insight_001",
                "title": "Strong upward trend detected",
                "description": "Data shows increasing trend",
                "category": "trends",
                "confidence": 0.8,
                "impact_score": 0.7
            }
        ]
        
        task = Task(
            name="create_recommendations",
            description="Test recommendation creation",
            agent_type=AgentType.INSIGHT_GENERATOR,
            parameters={
                "insights": insights,
                "business_context": {"industry": "technology"}
            }
        )
        
        result = await insight_generator.process_task(task)
        
        assert result["task_type"] == "create_recommendations"
        assert "recommendations" in result
        assert result["recommendation_count"] > 0
    
    @pytest.mark.asyncio
    async def test_report_generation_task(self, insight_generator):
        """Test report generation task processing"""
        # Create sample report data
        report_data = {
            "executive_summary": "Test summary",
            "key_insights": ["Insight 1", "Insight 2"],
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }
        
        task = Task(
            name="generate_report",
            description="Test report generation",
            agent_type=AgentType.INSIGHT_GENERATOR,
            parameters={
                "report_type": "business_intelligence",
                "report_data": report_data,
                "format": "json"
            }
        )
        
        result = await insight_generator.process_task(task)
        
        assert result["task_type"] == "generate_report"
        assert "report" in result
        assert result["report"]["report_type"] == "business_intelligence"


class TestActionExecutorAgent:
    """Test cases for ActionExecutorAgent class"""
    
    @pytest.fixture
    def action_executor(self):
        """Create a test action executor agent"""
        return create_action_executor_agent("test_ae_001")
    
    def test_agent_creation(self, action_executor):
        """Test action executor agent creation"""
        assert action_executor.agent_id == "test_ae_001"
        assert action_executor.agent_type == AgentType.ACTION_EXECUTOR
        assert "action_execution" in action_executor.capabilities
        assert "report_generation" in action_executor.capabilities
    
    @pytest.mark.asyncio
    async def test_action_execution_task(self, action_executor):
        """Test action execution task processing"""
        task = Task(
            name="execute_action",
            description="Test action execution",
            agent_type=AgentType.ACTION_EXECUTOR,
            parameters={
                "action_type": "data_export",
                "action_data": {
                    "format": "json",
                    "data": [{"test": "data"}],
                    "file_path": "test_export.json"
                }
            }
        )
        
        result = await action_executor.process_task(task)
        
        assert result["task_type"] == "execute_action"
        assert "action_id" in result
        assert result["action_type"] == "data_export"
    
    @pytest.mark.asyncio
    async def test_notification_task(self, action_executor):
        """Test notification task processing"""
        task = Task(
            name="send_notification",
            description="Test notification sending",
            agent_type=AgentType.ACTION_EXECUTOR,
            parameters={
                "notification_type": "email",
                "recipients": ["test@example.com"],
                "message": "Test notification",
                "subject": "Test Subject"
            }
        )
        
        # Mock email sending to avoid actual emails
        with patch.object(action_executor, '_send_email_notification', return_value={"status": "success"}):
            result = await action_executor.process_task(task)
            
            assert result["task_type"] == "send_notification"
            assert "notification_id" in result
            assert result["notification_type"] == "email"
    
    @pytest.mark.asyncio
    async def test_report_generation_task(self, action_executor):
        """Test report generation task processing"""
        task = Task(
            name="generate_report",
            description="Test report generation",
            agent_type=AgentType.ACTION_EXECUTOR,
            parameters={
                "report_type": "business_intelligence",
                "report_data": {
                    "executive_summary": "Test summary",
                    "key_insights": ["Insight 1"],
                    "recommendations": ["Recommendation 1"]
                },
                "format": "json"
            }
        )
        
        result = await action_executor.process_task(task)
        
        assert result["task_type"] == "generate_report"
        assert "report_id" in result
        assert result["report_type"] == "business_intelligence"


class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.fixture
    def system_setup(self):
        """Set up a complete test system"""
        # Create agents
        data_collector = create_data_collector_agent("dc_001")
        analyzer = create_analyzer_agent("an_001")
        insight_generator = create_insight_generator_agent("ig_001")
        action_executor = create_action_executor_agent("ae_001")
        
        # Create registry and communication manager
        registry = AgentRegistry()
        comm_manager = CommunicationManager()
        
        # Register agents
        registry.register_agent(data_collector)
        registry.register_agent(analyzer)
        registry.register_agent(insight_generator)
        registry.register_agent(action_executor)
        
        return {
            "registry": registry,
            "comm_manager": comm_manager,
            "agents": {
                "data_collector": data_collector,
                "analyzer": analyzer,
                "insight_generator": insight_generator,
                "action_executor": action_executor
            }
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, system_setup):
        """Test complete end-to-end workflow"""
        registry = system_setup["registry"]
        comm_manager = system_setup["comm_manager"]
        
        # Start all agents
        for agent in registry.get_all_agents():
            await agent.start()
        
        # Initialize communication
        await comm_manager.initialize_protocols()
        
        # Test data collection
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><h1>Test Data</h1></html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            task_id = await comm_manager.send_task_request(
                "web_scraping",
                {
                    "urls": ["https://example.com"],
                    "selectors": {"title": "h1"}
                }
            )
            
            # Wait for task completion
            result = await comm_manager.task_coordinator.wait_for_task_completion(task_id, timeout=10)
            
            assert result is not None
            assert "scraped_data" in result
        
        # Stop all agents
        for agent in registry.get_all_agents():
            await agent.stop()


class TestErrorHandling:
    """Test cases for error handling"""
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test agent error handling"""
        agent = create_data_collector_agent("error_test_agent")
        
        # Create a task that will cause an error
        task = Task(
            name="invalid_task",
            description="Task that doesn't exist",
            agent_type=AgentType.DATA_COLLECTOR,
            parameters={}
        )
        
        # Process task and expect error handling
        with pytest.raises(ValueError):
            await agent.process_task(task)
    
    @pytest.mark.asyncio
    async def test_communication_error_handling(self):
        """Test communication error handling"""
        comm_manager = CommunicationManager()
        
        # Test with invalid task type
        with pytest.raises(ValueError):
            await comm_manager.send_task_request("invalid_task_type", {})
    
    @pytest.mark.asyncio
    async def test_agent_recovery(self):
        """Test agent recovery from errors"""
        agent = create_analyzer_agent("recovery_test_agent")
        
        # Start agent
        await agent.start()
        assert agent.status == AgentStatus.ONLINE
        
        # Simulate error
        agent.status = AgentStatus.ERROR
        
        # Test recovery
        await agent.start()
        assert agent.status == AgentStatus.ONLINE


# Performance tests
class TestPerformance:
    """Performance tests for the system"""
    
    @pytest.mark.asyncio
    async def test_concurrent_task_processing(self):
        """Test concurrent task processing performance"""
        agent = create_analyzer_agent("perf_test_agent")
        await agent.start()
        
        # Create multiple tasks
        tasks = []
        for i in range(10):
            task = Task(
                name="statistical_analysis",
                description=f"Performance test task {i}",
                agent_type=AgentType.ANALYZER,
                parameters={
                    "data": list(range(100))  # Sample data
                }
            )
            tasks.append(task)
        
        # Process tasks concurrently
        start_time = datetime.now()
        results = await asyncio.gather(*[agent.process_task(task) for task in tasks])
        end_time = datetime.now()
        
        # Verify all tasks completed
        assert len(results) == 10
        assert all(result["task_type"] == "statistical_analysis" for result in results)
        
        # Check performance (should complete within reasonable time)
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 30  # Should complete within 30 seconds
        
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_large_data_processing(self):
        """Test processing of large datasets"""
        analyzer = create_analyzer_agent("large_data_test_agent")
        await analyzer.start()
        
        # Create large dataset
        large_data = {
            "data": [
                {"timestamp": f"2023-01-{i:02d}", "value": i * 10}
                for i in range(1, 1001)  # 1000 data points
            ]
        }
        
        task = Task(
            name="analyze_trends",
            description="Large data trend analysis",
            agent_type=AgentType.ANALYZER,
            parameters=large_data
        )
        
        # Process large dataset
        start_time = datetime.now()
        result = await analyzer.process_task(task)
        end_time = datetime.now()
        
        # Verify processing
        assert result["task_type"] == "analyze_trends"
        assert "trend_analysis" in result
        
        # Check performance
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 60  # Should complete within 60 seconds
        
        await analyzer.stop()


# Utility functions for testing
def create_sample_data(size: int = 100) -> Dict[str, Any]:
    """Create sample data for testing"""
    return {
        "data": [
            {
                "id": i,
                "timestamp": f"2023-01-{i:02d}",
                "value": i * 10 + np.random.randint(-5, 5),
                "category": "A" if i % 2 == 0 else "B"
            }
            for i in range(1, size + 1)
        ]
    }


def create_sample_analysis_results() -> Dict[str, Any]:
    """Create sample analysis results for testing"""
    return {
        "trend_analysis": {
            "linear_trend": {
                "slope": 0.5,
                "r_squared": 0.8,
                "trend_direction": "increasing"
            }
        },
        "statistical_analysis": {
            "descriptive_stats": {
                "mean": 50.0,
                "std": 10.0
            }
        },
        "anomaly_detection": {
            "total_anomalies": 2
        }
    }


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 