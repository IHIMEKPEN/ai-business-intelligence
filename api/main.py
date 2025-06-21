"""
Main API Server for AI Business Intelligence System

Provides REST API endpoints for:
- Agent management
- Task submission and monitoring
- Data collection and analysis
- Insight generation
- Report generation
- System monitoring
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from contextlib import asynccontextmanager

# Import core modules
from core.agent_framework import AgentRegistry, Task, Message, AgentType, AgentStatus, AgentRegistryGlobal
from core.communication import communication_manager
from agents.data_collector_agent import create_data_collector_agent
from agents.analyzer_agent import create_analyzer_agent
from agents.insight_generator_agent import create_insight_generator_agent
from agents.action_executor_agent import create_action_executor_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger(__name__)

# Global variables
agent_registry = AgentRegistryGlobal
app = None


# Pydantic models for API requests/responses
class TaskRequest(BaseModel):
    """Request model for task submission"""
    task_type: str = Field(..., description="Type of task to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    priority: int = Field(default=1, description="Task priority (1-10)")
    agent_type: Optional[str] = Field(None, description="Specific agent type to handle task")


class TaskResponse(BaseModel):
    """Response model for task submission"""
    task_id: str
    status: str
    message: str
    timestamp: str


class AgentInfo(BaseModel):
    """Model for agent information"""
    agent_id: str
    name: str
    agent_type: str
    status: str
    capabilities: List[str]
    created_at: str
    last_active: str


class SystemStatus(BaseModel):
    """Model for system status"""
    total_agents: int
    active_agents: int
    pending_tasks: int
    completed_tasks: int
    system_health: str
    uptime: str


class DataCollectionRequest(BaseModel):
    """Request model for data collection"""
    data_sources: List[str] = Field(..., description="List of data sources to collect from")
    collection_type: str = Field(default="standard", description="Type of collection")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Collection parameters")


class AnalysisRequest(BaseModel):
    """Request model for data analysis"""
    data: Dict[str, Any] = Field(..., description="Data to analyze")
    analysis_type: str = Field(..., description="Type of analysis to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Analysis parameters")


class InsightRequest(BaseModel):
    """Request model for insight generation"""
    analysis_results: Dict[str, Any] = Field(..., description="Analysis results")
    business_context: Dict[str, Any] = Field(default_factory=dict, description="Business context")
    categories: List[str] = Field(default_factory=list, description="Insight categories")


class ReportRequest(BaseModel):
    """Request model for report generation"""
    report_type: str = Field(..., description="Type of report to generate")
    report_data: Dict[str, Any] = Field(..., description="Data for report")
    format: str = Field(default="json", description="Report format")
    output_path: Optional[str] = Field(None, description="Output path for report")


class NotificationRequest(BaseModel):
    """Request model for notifications"""
    notification_type: str = Field(..., description="Type of notification")
    recipients: List[str] = Field(..., description="List of recipients")
    message: str = Field(..., description="Notification message")
    subject: str = Field(default="AI Business Intelligence Notification", description="Notification subject")
    priority: str = Field(default="normal", description="Notification priority")


class CryptoAnalysisRequest(BaseModel):
    """Request model for crypto analysis"""
    symbols: List[str] = Field(..., description="List of crypto symbols to analyze")


class StockAnalysisRequest(BaseModel):
    """Request model for stock analysis"""
    symbols: List[str] = Field(..., description="List of stock symbols to analyze")
    period: str = Field(default="1mo", description="Time period for analysis")
    interval: str = Field(default="1d", description="Data interval")


class ForexAnalysisRequest(BaseModel):
    """Request model for forex analysis"""
    pairs: List[str] = Field(..., description="List of forex pairs to analyze")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Business Intelligence API Server")
    
    # Initialize communication manager
    await communication_manager.initialize_protocols()
    
    # Create default agents
    await create_default_agents()
    
    logger.info("API Server startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Business Intelligence API Server")
    
    # Cleanup agents
    await cleanup_agents()
    
    logger.info("API Server shutdown completed")


# Create FastAPI app
app = FastAPI(
    title="AI Business Intelligence API",
    description="REST API for AI-powered business intelligence system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup and shutdown functions
async def create_default_agents():
    """Create default agents for the system"""
    try:
        # Create one agent of each type
        data_collector = create_data_collector_agent()
        analyzer = create_analyzer_agent()
        insight_generator = create_insight_generator_agent()
        action_executor = create_action_executor_agent()
        
        # Set task coordinator for each agent
        data_collector.task_coordinator = communication_manager.task_coordinator
        analyzer.task_coordinator = communication_manager.task_coordinator
        insight_generator.task_coordinator = communication_manager.task_coordinator
        action_executor.task_coordinator = communication_manager.task_coordinator
        
        # Register agents in global registry
        AgentRegistryGlobal.register_agent(data_collector)
        AgentRegistryGlobal.register_agent(analyzer)
        AgentRegistryGlobal.register_agent(insight_generator)
        AgentRegistryGlobal.register_agent(action_executor)
        
        # Start agents
        await data_collector.start()
        await analyzer.start()
        await insight_generator.start()
        await action_executor.start()
        
        logger.info(
            "Default agents created and started",
            agent_count=4,
            agent_types=["data_collector", "analyzer", "insight_generator", "action_executor"]
        )
        
    except Exception as e:
        logger.error("Failed to create default agents", error=str(e))
        raise


async def cleanup_agents():
    """Cleanup and stop all agents"""
    try:
        agents = AgentRegistryGlobal.get_all_agents()
        for agent in agents:
            await agent.stop()
        
        logger.info("All agents stopped", agent_count=len(agents))
        
    except Exception as e:
        logger.error("Failed to cleanup agents", error=str(e))


# Dependency functions
async def get_agent_registry() -> AgentRegistry:
    """Dependency to get agent registry"""
    return AgentRegistryGlobal


async def get_communication_manager():
    """Dependency to get communication manager"""
    return communication_manager


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Business Intelligence API",
        "version": "1.0.0"
    }


# System status endpoint
@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status and statistics"""
    try:
        agents = AgentRegistryGlobal.get_all_agents()
        active_agents = [agent for agent in agents if agent.status in [AgentStatus.IDLE, AgentStatus.BUSY]]
        
        # Get task statistics
        pending_tasks = sum(len(agent.task_queue) for agent in agents)
        completed_tasks = sum(len(agent.completed_tasks) for agent in agents)
        
        # Determine system health
        if len(active_agents) == len(agents) and len(agents) > 0:
            system_health = "healthy"
        elif len(active_agents) > 0:
            system_health = "degraded"
        else:
            system_health = "unhealthy"
        
        return SystemStatus(
            total_agents=len(agents),
            active_agents=len(active_agents),
            pending_tasks=pending_tasks,
            completed_tasks=completed_tasks,
            system_health=system_health,
            uptime=datetime.utcnow().isoformat()  # Simplified uptime
        )
        
    except Exception as e:
        logger.error("Failed to get system status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


# Agent management endpoints
@app.get("/agents", response_model=List[AgentInfo])
async def get_agents():
    """Get list of all agents"""
    try:
        agents = AgentRegistryGlobal.get_all_agents()
        agent_info_list = []
        
        for agent in agents:
            agent_info = AgentInfo(
                agent_id=agent.agent_id,
                name=agent.name,
                agent_type=agent.agent_type.value,
                status=agent.status.value,
                capabilities=agent.capabilities,
                created_at=agent.created_at.isoformat(),
                last_active=agent.last_active.isoformat() if agent.last_active else ""
            )
            agent_info_list.append(agent_info)
        
        return agent_info_list
        
    except Exception as e:
        logger.error("Failed to get agents", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")


@app.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """Get specific agent information"""
    try:
        agent = AgentRegistryGlobal.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return AgentInfo(
            agent_id=agent.agent_id,
            name=agent.name,
            agent_type=agent.agent_type.value,
            status=agent.status.value,
            capabilities=agent.capabilities,
            created_at=agent.created_at.isoformat(),
            last_active=agent.last_active.isoformat() if agent.last_active else ""
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")


@app.post("/agents")
async def create_agent(agent_type: str, agent_id: Optional[str] = None):
    """Create a new agent"""
    try:
        # Create agent based on type
        if agent_type == "data_collector":
            agent = create_data_collector_agent(agent_id)
        elif agent_type == "analyzer":
            agent = create_analyzer_agent(agent_id)
        elif agent_type == "insight_generator":
            agent = create_insight_generator_agent(agent_id)
        elif agent_type == "action_executor":
            agent = create_action_executor_agent(agent_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        # Set task coordinator for the agent
        agent.task_coordinator = communication_manager.task_coordinator
        
        # Register and start agent
        AgentRegistryGlobal.register_agent(agent)
        await agent.start()
        
        logger.info("Agent created", agent_id=agent.agent_id, agent_type=agent_type)
        
        return {
            "agent_id": agent.agent_id,
            "agent_type": agent_type,
            "status": "created",
            "message": f"Agent {agent.agent_id} created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create agent", agent_type=agent_type, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    try:
        agent = AgentRegistryGlobal.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Stop and remove agent
        await agent.stop()
        AgentRegistryGlobal.unregister_agent(agent_id)
        
        logger.info("Agent deleted", agent_id=agent_id)
        
        return {
            "agent_id": agent_id,
            "status": "deleted",
            "message": f"Agent {agent_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete agent", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")


# Task management endpoints
@app.post("/tasks", response_model=TaskResponse)
async def submit_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Submit a task for execution"""
    try:
        # Create task
        task = Task(
            name=task_request.task_type,
            description=f"Task of type {task_request.task_type}",
            agent_type=AgentType(task_request.agent_type) if task_request.agent_type else None,
            parameters=task_request.parameters,
            priority=task_request.priority
        )
        
        # Submit task to communication manager
        task_id = await communication_manager.send_task_request(
            task_request.task_type,
            task_request.parameters,
            task_request.priority
        )
        
        logger.info("Task submitted", task_id=task_id, task_type=task_request.task_type)
        
        return TaskResponse(
            task_id=task_id,
            status="submitted",
            message=f"Task {task_id} submitted successfully",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error("Failed to submit task", task_type=task_request.task_type, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and result"""
    try:
        # Get task result from communication manager
        result = await communication_manager.get_task_result(task_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return {
            "task_id": task_id,
            "status": "completed" if result else "pending",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get task status", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


# Data collection endpoints
@app.post("/data/collect")
async def collect_data(request: DataCollectionRequest, background_tasks: BackgroundTasks):
    """Collect data from specified sources"""
    try:
        # Submit data collection task
        task_id = await communication_manager.send_task_request(
            "collect_data",
            {
                "data_sources": request.data_sources,
                "collection_type": request.collection_type,
                "parameters": request.parameters
            },
            priority=1
        )
        
        logger.info("Data collection task submitted", task_id=task_id, sources=request.data_sources)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": f"Data collection task {task_id} submitted",
            "data_sources": request.data_sources,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to submit data collection task", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit data collection task: {str(e)}")


@app.get("/data/sources")
async def get_data_sources():
    """Get available data sources"""
    try:
        # Get data collector agents
        data_collectors = AgentRegistryGlobal.get_agents_by_type(AgentType.DATA_COLLECTOR)
        
        available_sources = []
        for agent in data_collectors:
            if hasattr(agent, 'get_available_sources'):
                sources = agent.get_available_sources()
                available_sources.extend(sources)
        
        return {
            "available_sources": list(set(available_sources)),  # Remove duplicates
            "total_sources": len(set(available_sources)),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get data sources", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get data sources: {str(e)}")


# Analysis endpoints
@app.post("/analysis")
async def analyze_data(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze data using specified analysis type"""
    try:
        # Submit analysis task
        task_id = await communication_manager.send_task_request(
            "analyze_data",
            {
                "data": request.data,
                "analysis_type": request.analysis_type,
                "parameters": request.parameters
            },
            priority=2
        )
        
        logger.info("Analysis task submitted", task_id=task_id, analysis_type=request.analysis_type)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": f"Analysis task {task_id} submitted",
            "analysis_type": request.analysis_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to submit analysis task", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit analysis task: {str(e)}")


@app.post("/analysis/stocks")
async def analyze_stocks(request: StockAnalysisRequest, background_tasks: BackgroundTasks = None):
    """Analyze stock data for given symbols"""
    try:
        import yfinance as yf
        import pandas as pd
        
        # Collect stock data
        stock_data = {}
        
        for symbol in request.symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period=request.period, interval=request.interval)
                
                if not hist_data.empty:
                    stock_data[symbol.lower()] = {
                        "symbol": symbol,
                        "data": hist_data.reset_index().to_dict('records'),
                        "current_price": float(hist_data['Close'].iloc[-1]),
                        "volume": int(hist_data['Volume'].iloc[-1]),
                        "market_cap": ticker.info.get('marketCap', 0)
                    }
                    logger.info(f"Collected data for {symbol}")
                else:
                    logger.warning(f"No data available for {symbol}")
                    
            except Exception as e:
                logger.error(f"Failed to collect data for {symbol}: {str(e)}")
        
        if not stock_data:
            raise HTTPException(status_code=400, detail="No stock data could be collected")
        
        # Submit stock analysis task with collected data
        task_id = await communication_manager.send_task_request(
            "analyze_stocks",
            stock_data,
            priority=2
        )
        
        logger.info("Stock analysis task submitted", task_id=task_id, symbols=request.symbols)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": f"Stock analysis task {task_id} submitted",
            "symbols": request.symbols,
            "data_collected": list(stock_data.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit stock analysis task", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit stock analysis task: {str(e)}")


@app.post("/analysis/forex")
async def analyze_forex(request: ForexAnalysisRequest, background_tasks: BackgroundTasks = None):
    """Analyze forex data for given currency pairs"""
    try:
        import yfinance as yf
        
        # Collect forex data
        forex_data = {}
        
        for pair in request.pairs:
            try:
                # Use yfinance for forex data
                ticker = yf.Ticker(f"{pair}=X")
                hist_data = ticker.history(period="5d", interval="1d")
                
                if not hist_data.empty:
                    latest = hist_data.iloc[-1]
                    previous = hist_data.iloc[-2] if len(hist_data) > 1 else latest
                    
                    forex_data[pair] = {
                        "current_rate": float(latest['Close']),
                        "change_24h": float(latest['Close']) - float(previous['Close']),
                        "change_percent": ((float(latest['Close']) - float(previous['Close'])) / float(previous['Close'])) * 100,
                        "high_24h": float(latest['High']),
                        "low_24h": float(latest['Low']),
                        "volume": float(latest['Volume'])
                    }
                    logger.info(f"Collected data for {pair}")
                else:
                    logger.warning(f"No data available for {pair}")
                    
            except Exception as e:
                logger.error(f"Failed to collect data for {pair}: {str(e)}")
        
        if not forex_data:
            raise HTTPException(status_code=400, detail="No forex data could be collected")
        
        # Submit forex analysis task with collected data
        task_id = await communication_manager.send_task_request(
            "analyze_forex",
            {"forex_data": forex_data, "pairs": request.pairs},
            priority=2
        )
        
        logger.info("Forex analysis task submitted", task_id=task_id, pairs=request.pairs)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": f"Forex analysis task {task_id} submitted",
            "pairs": request.pairs,
            "data_collected": list(forex_data.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit forex analysis task", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit forex analysis task: {str(e)}")


@app.post("/analysis/crypto")
async def analyze_crypto(request: CryptoAnalysisRequest, background_tasks: BackgroundTasks = None):
    """Analyze cryptocurrency data for given symbols"""
    try:
        import yfinance as yf
        
        # Collect crypto data
        crypto_data = {}
        
        for symbol in request.symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period="5d", interval="1d")
                
                if not hist_data.empty:
                    latest = hist_data.iloc[-1]
                    previous = hist_data.iloc[-2] if len(hist_data) > 1 else latest
                    
                    crypto_data[symbol] = {
                        "current_price": float(latest['Close']),
                        "volume_24h": float(latest['Volume']),
                        "market_cap": 0,  # Not available in yfinance
                        "price_change_24h": float(latest['Close']) - float(previous['Close']),
                        "price_change_percent": ((float(latest['Close']) - float(previous['Close'])) / float(previous['Close'])) * 100,
                        "high_24h": float(latest['High']),
                        "low_24h": float(latest['Low']),
                        "historical_data": hist_data.reset_index().to_dict('records')
                    }
                    logger.info(f"Collected data for {symbol}")
                else:
                    logger.warning(f"No data available for {symbol}")
                    
            except Exception as e:
                logger.error(f"Failed to collect data for {symbol}: {str(e)}")
        
        if not crypto_data:
            raise HTTPException(status_code=400, detail="No crypto data could be collected")
        
        # Submit crypto analysis task with collected data
        task_id = await communication_manager.send_task_request(
            "analyze_crypto",
            {"crypto_data": crypto_data},
            priority=2
        )
        
        logger.info("Crypto analysis task submitted", task_id=task_id, symbols=request.symbols)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": f"Crypto analysis task {task_id} submitted",
            "symbols": request.symbols,
            "data_collected": list(crypto_data.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit crypto analysis task", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit crypto analysis task: {str(e)}")


@app.get("/analysis/types")
async def get_analysis_types():
    """Get available analysis types"""
    try:
        # Get analyzer agents
        analyzers = AgentRegistryGlobal.get_agents_by_type(AgentType.ANALYZER)
        
        analysis_types = []
        for agent in analyzers:
            if hasattr(agent, 'capabilities'):
                analysis_types.extend(agent.capabilities)
        
        return {
            "available_analysis_types": list(set(analysis_types)),  # Remove duplicates
            "total_types": len(set(analysis_types)),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get analysis types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get analysis types: {str(e)}")


# Insight generation endpoints
@app.post("/insights")
async def generate_insights(request: InsightRequest, background_tasks: BackgroundTasks):
    """Generate business insights from analysis results"""
    try:
        # Submit insight generation task
        task_id = await communication_manager.send_task_request(
            "generate_insights",
            {
                "analysis_results": request.analysis_results,
                "business_context": request.business_context,
                "categories": request.categories
            },
            priority=3
        )
        
        logger.info("Insight generation task submitted", task_id=task_id)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": f"Insight generation task {task_id} submitted",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to submit insight generation task", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit insight generation task: {str(e)}")


@app.get("/insights/recent")
async def get_recent_insights(limit: int = 10):
    """Get recent insights"""
    try:
        # Get insight generator agents
        insight_generators = AgentRegistryGlobal.get_agents_by_type(AgentType.INSIGHT_GENERATOR)
        
        recent_insights = []
        for agent in insight_generators:
            if hasattr(agent, 'insights_database'):
                insights = list(agent.insights_database.values())
                recent_insights.extend(insights)
        
        # Sort by timestamp and limit
        recent_insights.sort(key=lambda x: x.timestamp if hasattr(x, 'timestamp') else datetime.min, reverse=True)
        recent_insights = recent_insights[:limit]
        
        # Convert to dict format
        insights_data = []
        for insight in recent_insights:
            if hasattr(insight, 'insight_id'):
                insights_data.append({
                    "insight_id": insight.insight_id,
                    "title": insight.title,
                    "description": insight.description,
                    "category": insight.category,
                    "confidence": insight.confidence,
                    "timestamp": insight.timestamp.isoformat() if hasattr(insight.timestamp, 'isoformat') else str(insight.timestamp)
                })
        
        return {
            "recent_insights": insights_data,
            "total_insights": len(insights_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get recent insights", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get recent insights: {str(e)}")


# Report generation endpoints
@app.post("/reports")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Generate a report"""
    try:
        # Submit report generation task
        task_id = await communication_manager.send_task_request(
            "generate_report",
            {
                "report_type": request.report_type,
                "report_data": request.report_data,
                "format": request.format,
                "output_path": request.output_path
            },
            priority=4
        )
        
        logger.info("Report generation task submitted", task_id=task_id, report_type=request.report_type)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": f"Report generation task {task_id} submitted",
            "report_type": request.report_type,
            "format": request.format,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to submit report generation task", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit report generation task: {str(e)}")


@app.get("/reports/types")
async def get_report_types():
    """Get available report types"""
    try:
        # Get action executor agents
        action_executors = AgentRegistryGlobal.get_agents_by_type(AgentType.ACTION_EXECUTOR)
        
        report_types = []
        for agent in action_executors:
            if hasattr(agent, 'capabilities'):
                # Filter capabilities related to reports
                report_capabilities = [cap for cap in agent.capabilities if 'report' in cap.lower()]
                report_types.extend(report_capabilities)
        
        return {
            "available_report_types": list(set(report_types)),  # Remove duplicates
            "total_types": len(set(report_types)),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get report types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get report types: {str(e)}")


# Notification endpoints
@app.post("/notifications")
async def send_notification(request: NotificationRequest, background_tasks: BackgroundTasks):
    """Send a notification"""
    try:
        # Submit notification task
        task_id = await communication_manager.send_task_request(
            "send_notification",
            {
                "notification_type": request.notification_type,
                "recipients": request.recipients,
                "message": request.message,
                "subject": request.subject,
                "priority": request.priority
            },
            priority=5
        )
        
        logger.info("Notification task submitted", task_id=task_id, notification_type=request.notification_type)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": f"Notification task {task_id} submitted",
            "notification_type": request.notification_type,
            "recipients": request.recipients,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to submit notification task", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit notification task: {str(e)}")


# Communication endpoints
@app.get("/communication/stats")
async def get_communication_stats():
    """Get communication statistics"""
    try:
        stats = communication_manager.get_communication_stats()
        
        return {
            "communication_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get communication stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get communication stats: {str(e)}")


# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Main function to run the server
def main():
    """Main function to run the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Business Intelligence API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    
    # Run the server
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main() 