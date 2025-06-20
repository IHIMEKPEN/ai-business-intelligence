"""
Insight Generator Agent

Responsible for generating business insights and recommendations:
- Business intelligence analysis
- Insight generation
- Recommendation creation
- Report generation
- Predictive analytics
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Tuple
import structlog
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass

# LangChain imports for AI-powered insights
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.chains import LLMChain
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger = structlog.get_logger(__name__)
    logger.warning("LangChain not available. Using custom framework only.")

from core.agent_framework import BaseAgent, AgentType, Task, Message
from core.communication import communication_manager

logger = structlog.get_logger(__name__)


@dataclass
class BusinessInsight:
    """Business insight data structure"""
    insight_id: str
    title: str
    description: str
    category: str
    confidence: float
    impact_score: float
    data_sources: List[str]
    recommendations: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class Recommendation:
    """Business recommendation data structure"""
    recommendation_id: str
    title: str
    description: str
    category: str
    priority: str  # high, medium, low
    expected_impact: str
    implementation_effort: str
    timeline: str
    cost_estimate: Optional[str]
    risk_level: str
    dependencies: List[str]
    timestamp: datetime


class InsightGeneratorAgent(BaseAgent):
    """
    Insight Generator Agent for business intelligence and recommendations
    
    Capabilities:
    - Business intelligence analysis
    - Insight generation
    - Recommendation creation
    - Report generation
    - Predictive analytics
    - KPI analysis
    - Competitive analysis
    - AI-powered insights (LangChain integration)
    """
    
    def __init__(self, agent_id: str = None, use_langchain: bool = False):
        super().__init__(
            agent_id=agent_id or f"insight_generator_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            agent_type=AgentType.INSIGHT_GENERATOR,
            name="Insight Generator Agent"
        )
        
        self.capabilities = [
            "business_intelligence",
            "insight_generation",
            "recommendation_creation",
            "report_generation",
            "predictive_analytics",
            "kpi_analysis",
            "competitive_analysis"
        ]
        
        # Add LangChain capability if available
        if LANGCHAIN_AVAILABLE:
            self.capabilities.append("ai_powered_insights")
        
        self.insights_database = {}
        self.recommendations_database = {}
        self.business_context = {}
        self.kpi_frameworks = {}
        
        # LangChain configuration
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.langchain_llm = None
        self.langchain_chains = {}
        
        if self.use_langchain:
            self._initialize_langchain()
        
        # Initialize business context
        self._initialize_business_context()
        
        logger.info(
            "Insight Generator Agent initialized",
            agent_id=self.agent_id,
            capabilities=self.capabilities,
            use_langchain=self.use_langchain
        )
    
    def _initialize_langchain(self):
        """Initialize LangChain components for AI-powered insights"""
        try:
            # Initialize OpenAI LLM
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OpenAI API key not found. LangChain features disabled.")
                self.use_langchain = False
                return
            
            self.langchain_llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                api_key=api_key
            )
            
            # Create specialized chains for different types of insights
            self._create_langchain_chains()
            
            logger.info("LangChain initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain: {str(e)}")
            self.use_langchain = False
    
    def _create_langchain_chains(self):
        """Create specialized LangChain chains for different insight types"""
        try:
            # Trend Analysis Chain
            trend_prompt = ChatPromptTemplate.from_template("""
            You are a business intelligence expert. Analyze the following trend data and provide insights:
            
            Trend Data: {trend_data}
            Business Context: {business_context}
            
            Provide insights in the following JSON format:
            {{
                "insights": [
                    {{
                        "title": "Insight title",
                        "description": "Detailed insight description",
                        "confidence": 0.85,
                        "impact_score": 0.8,
                        "recommendations": ["Recommendation 1", "Recommendation 2"]
                    }}
                ]
            }}
            """)
            self.langchain_chains["trend_analysis"] = LLMChain(
                llm=self.langchain_llm, 
                prompt=trend_prompt
            )
            
            # Pattern Recognition Chain
            pattern_prompt = ChatPromptTemplate.from_template("""
            You are a data scientist specializing in pattern recognition. Analyze the following pattern data:
            
            Pattern Data: {pattern_data}
            Business Context: {business_context}
            
            Provide insights in the following JSON format:
            {{
                "insights": [
                    {{
                        "title": "Pattern insight title",
                        "description": "Detailed pattern analysis",
                        "confidence": 0.9,
                        "impact_score": 0.7,
                        "recommendations": ["Action based on pattern"]
                    }}
                ]
            }}
            """)
            self.langchain_chains["pattern_recognition"] = LLMChain(
                llm=self.langchain_llm, 
                prompt=pattern_prompt
            )
            
            # Anomaly Detection Chain
            anomaly_prompt = ChatPromptTemplate.from_template("""
            You are a business analyst expert in anomaly detection. Analyze the following anomaly data:
            
            Anomaly Data: {anomaly_data}
            Business Context: {business_context}
            
            Provide insights in the following JSON format:
            {{
                "insights": [
                    {{
                        "title": "Anomaly insight title",
                        "description": "Detailed anomaly analysis and implications",
                        "confidence": 0.8,
                        "impact_score": 0.9,
                        "recommendations": ["Immediate actions", "Investigation steps"]
                    }}
                ]
            }}
            """)
            self.langchain_chains["anomaly_detection"] = LLMChain(
                llm=self.langchain_llm, 
                prompt=anomaly_prompt
            )
            
            # Comprehensive Analysis Chain
            comprehensive_prompt = ChatPromptTemplate.from_template("""
            You are a senior business intelligence analyst. Provide comprehensive insights from the following data:
            
            Analysis Results: {analysis_results}
            Business Context: {business_context}
            
            Provide comprehensive insights in the following JSON format:
            {{
                "executive_summary": "High-level summary",
                "key_insights": [
                    {{
                        "title": "Key insight title",
                        "description": "Detailed insight",
                        "priority": "high/medium/low",
                        "business_impact": "Impact description"
                    }}
                ],
                "recommendations": [
                    {{
                        "title": "Recommendation title",
                        "description": "Detailed recommendation",
                        "priority": "high/medium/low",
                        "implementation_effort": "effort level"
                    }}
                ],
                "risk_assessment": "Risk analysis",
                "opportunities": "Opportunity analysis"
            }}
            """)
            self.langchain_chains["comprehensive"] = LLMChain(
                llm=self.langchain_llm, 
                prompt=comprehensive_prompt
            )
            
        except Exception as e:
            logger.error(f"Failed to create LangChain chains: {str(e)}")
            self.use_langchain = False
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process insight generation tasks"""
        task_type = task.name
        parameters = task.parameters
        
        logger.info(
            "Processing insight generation task",
            task_id=task.id,
            task_type=task_type,
            parameters=parameters
        )
        
        try:
            if task_type == "generate_insights":
                return await self._generate_insights(parameters)
            elif task_type == "create_recommendations":
                return await self._create_recommendations(parameters)
            elif task_type == "generate_report":
                return await self._generate_report(parameters)
            elif task_type == "predictive_analysis":
                return await self._predictive_analysis(parameters)
            elif task_type == "kpi_analysis":
                return await self._kpi_analysis(parameters)
            elif task_type == "competitive_analysis":
                return await self._competitive_analysis(parameters)
            elif task_type == "generate_comprehensive_insights":
                return await self._generate_comprehensive_insights(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            logger.error(
                "Task processing failed",
                task_id=task.id,
                task_type=task_type,
                error=str(e)
            )
            raise
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages"""
        message_type = message.message_type
        
        if message_type == "insight_request":
            return await self._handle_insight_request(message)
        elif message_type == "data_analysis_result":
            return await self._handle_data_analysis_result(message)
        elif message_type == "business_context_update":
            return await self._handle_business_context_update(message)
        else:
            logger.warning(
                "Unknown message type",
                message_type=message_type,
                agent_id=self.agent_id
            )
            return None
    
    async def _generate_insights(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business insights from data"""
        data = parameters.get("data")
        analysis_results = parameters.get("analysis_results", {})
        business_context = parameters.get("business_context", {})
        insight_categories = parameters.get("categories", ["performance", "trends", "anomalies"])
        
        if not data and not analysis_results:
            raise ValueError("No data or analysis results provided for insight generation")
        
        try:
            insights = []
            
            # Generate insights based on analysis results
            if "trend_analysis" in analysis_results:
                trend_insights = await self._generate_trend_insights(
                    analysis_results["trend_analysis"], business_context
                )
                insights.extend(trend_insights)
            
            if "pattern_recognition" in analysis_results:
                pattern_insights = await self._generate_pattern_insights(
                    analysis_results["pattern_recognition"], business_context
                )
                insights.extend(pattern_insights)
            
            if "anomaly_detection" in analysis_results:
                anomaly_insights = await self._generate_anomaly_insights(
                    analysis_results["anomaly_detection"], business_context
                )
                insights.extend(anomaly_insights)
            
            if "statistical_analysis" in analysis_results:
                statistical_insights = await self._generate_statistical_insights(
                    analysis_results["statistical_analysis"], business_context
                )
                insights.extend(statistical_insights)
            
            # Generate KPI insights if KPI data is available
            if "kpi_data" in parameters:
                kpi_insights = await self._generate_kpi_insights(
                    parameters["kpi_data"], business_context
                )
                insights.extend(kpi_insights)
            
            # Use LangChain for AI-powered insights if enabled
            if self.use_langchain:
                ai_insights = await self._generate_ai_powered_insights(
                    analysis_results, business_context, insight_categories
                )
                insights.extend(ai_insights)
            
            # Store insights in database
            for insight in insights:
                self.insights_database[insight.insight_id] = insight
            
            # Generate recommendations for insights
            all_recommendations = []
            for insight in insights:
                recommendations = await self._generate_recommendations_for_insight(
                    insight, business_context
                )
                all_recommendations.extend(recommendations)
            
            # Prioritize recommendations
            prioritized_recommendations = self._prioritize_recommendations(all_recommendations)
            
            logger.info(
                "Insights generated successfully",
                insight_count=len(insights),
                recommendation_count=len(prioritized_recommendations),
                use_langchain=self.use_langchain,
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "generate_insights",
                "insights": [self._insight_to_dict(insight) for insight in insights],
                "recommendations": [self._recommendation_to_dict(rec) for rec in prioritized_recommendations],
                "insight_count": len(insights),
                "recommendation_count": len(prioritized_recommendations),
                "use_langchain": self.use_langchain,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Insight generation failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _generate_ai_powered_insights(self, analysis_results: Dict[str, Any], business_context: Dict[str, Any], categories: List[str]) -> List[BusinessInsight]:
        """Generate AI-powered insights using LangChain"""
        if not self.use_langchain or not self.langchain_chains:
            return []
        
        ai_insights = []
        
        try:
            # Generate AI insights for trend analysis
            if "trend_analysis" in analysis_results and "trends" in categories:
                trend_insights = await self._generate_ai_trend_insights(
                    analysis_results["trend_analysis"], business_context
                )
                ai_insights.extend(trend_insights)
            
            # Generate AI insights for pattern recognition
            if "pattern_recognition" in analysis_results and "patterns" in categories:
                pattern_insights = await self._generate_ai_pattern_insights(
                    analysis_results["pattern_recognition"], business_context
                )
                ai_insights.extend(pattern_insights)
            
            # Generate AI insights for anomaly detection
            if "anomaly_detection" in analysis_results and "anomalies" in categories:
                anomaly_insights = await self._generate_ai_anomaly_insights(
                    analysis_results["anomaly_detection"], business_context
                )
                ai_insights.extend(anomaly_insights)
            
            # Generate comprehensive AI insights
            if "comprehensive" in categories:
                comprehensive_insights = await self._generate_ai_comprehensive_insights(
                    analysis_results, business_context
                )
                ai_insights.extend(comprehensive_insights)
            
            logger.info(
                "AI-powered insights generated",
                ai_insight_count=len(ai_insights),
                agent_id=self.agent_id
            )
            
        except Exception as e:
            logger.error(f"Failed to generate AI-powered insights: {str(e)}")
        
        return ai_insights
    
    async def _generate_ai_trend_insights(self, trend_data: Dict[str, Any], business_context: Dict[str, Any]) -> List[BusinessInsight]:
        """Generate AI-powered trend insights using LangChain"""
        try:
            chain = self.langchain_chains.get("trend_analysis")
            if not chain:
                return []
            
            # Prepare data for LangChain
            trend_data_str = json.dumps(trend_data, indent=2)
            business_context_str = json.dumps(business_context, indent=2)
            
            # Run LangChain analysis
            result = await chain.arun(
                trend_data=trend_data_str,
                business_context=business_context_str
            )
            
            # Parse the result
            try:
                parsed_result = json.loads(result)
                insights = []
                
                for insight_data in parsed_result.get("insights", []):
                    insight = BusinessInsight(
                        insight_id=f"ai_trend_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                        title=insight_data.get("title", "AI Trend Insight"),
                        description=insight_data.get("description", ""),
                        category="trend_analysis",
                        confidence=insight_data.get("confidence", 0.8),
                        impact_score=insight_data.get("impact_score", 0.7),
                        data_sources=["AI Analysis"],
                        recommendations=insight_data.get("recommendations", []),
                        timestamp=datetime.utcnow(),
                        metadata={"source": "langchain", "model": "gpt-3.5-turbo"}
                    )
                    insights.append(insight)
                
                return insights
                
            except json.JSONDecodeError:
                logger.error("Failed to parse LangChain trend analysis result")
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate AI trend insights: {str(e)}")
            return []
    
    async def _generate_ai_pattern_insights(self, pattern_data: Dict[str, Any], business_context: Dict[str, Any]) -> List[BusinessInsight]:
        """Generate AI-powered pattern insights using LangChain"""
        try:
            chain = self.langchain_chains.get("pattern_recognition")
            if not chain:
                return []
            
            # Prepare data for LangChain
            pattern_data_str = json.dumps(pattern_data, indent=2)
            business_context_str = json.dumps(business_context, indent=2)
            
            # Run LangChain analysis
            result = await chain.arun(
                pattern_data=pattern_data_str,
                business_context=business_context_str
            )
            
            # Parse the result
            try:
                parsed_result = json.loads(result)
                insights = []
                
                for insight_data in parsed_result.get("insights", []):
                    insight = BusinessInsight(
                        insight_id=f"ai_pattern_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                        title=insight_data.get("title", "AI Pattern Insight"),
                        description=insight_data.get("description", ""),
                        category="pattern_recognition",
                        confidence=insight_data.get("confidence", 0.9),
                        impact_score=insight_data.get("impact_score", 0.7),
                        data_sources=["AI Analysis"],
                        recommendations=insight_data.get("recommendations", []),
                        timestamp=datetime.utcnow(),
                        metadata={"source": "langchain", "model": "gpt-3.5-turbo"}
                    )
                    insights.append(insight)
                
                return insights
                
            except json.JSONDecodeError:
                logger.error("Failed to parse LangChain pattern analysis result")
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate AI pattern insights: {str(e)}")
            return []
    
    async def _generate_ai_anomaly_insights(self, anomaly_data: Dict[str, Any], business_context: Dict[str, Any]) -> List[BusinessInsight]:
        """Generate AI-powered anomaly insights using LangChain"""
        try:
            chain = self.langchain_chains.get("anomaly_detection")
            if not chain:
                return []
            
            # Prepare data for LangChain
            anomaly_data_str = json.dumps(anomaly_data, indent=2)
            business_context_str = json.dumps(business_context, indent=2)
            
            # Run LangChain analysis
            result = await chain.arun(
                anomaly_data=anomaly_data_str,
                business_context=business_context_str
            )
            
            # Parse the result
            try:
                parsed_result = json.loads(result)
                insights = []
                
                for insight_data in parsed_result.get("insights", []):
                    insight = BusinessInsight(
                        insight_id=f"ai_anomaly_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                        title=insight_data.get("title", "AI Anomaly Insight"),
                        description=insight_data.get("description", ""),
                        category="anomaly_detection",
                        confidence=insight_data.get("confidence", 0.8),
                        impact_score=insight_data.get("impact_score", 0.9),
                        data_sources=["AI Analysis"],
                        recommendations=insight_data.get("recommendations", []),
                        timestamp=datetime.utcnow(),
                        metadata={"source": "langchain", "model": "gpt-3.5-turbo"}
                    )
                    insights.append(insight)
                
                return insights
                
            except json.JSONDecodeError:
                logger.error("Failed to parse LangChain anomaly analysis result")
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate AI anomaly insights: {str(e)}")
            return []
    
    async def _generate_ai_comprehensive_insights(self, analysis_results: Dict[str, Any], business_context: Dict[str, Any]) -> List[BusinessInsight]:
        """Generate comprehensive AI-powered insights using LangChain"""
        try:
            chain = self.langchain_chains.get("comprehensive")
            if not chain:
                return []
            
            # Prepare data for LangChain
            analysis_results_str = json.dumps(analysis_results, indent=2)
            business_context_str = json.dumps(business_context, indent=2)
            
            # Run LangChain analysis
            result = await chain.arun(
                analysis_results=analysis_results_str,
                business_context=business_context_str
            )
            
            # Parse the result
            try:
                parsed_result = json.loads(result)
                insights = []
                
                # Process key insights
                for insight_data in parsed_result.get("key_insights", []):
                    insight = BusinessInsight(
                        insight_id=f"ai_comprehensive_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                        title=insight_data.get("title", "AI Comprehensive Insight"),
                        description=insight_data.get("description", ""),
                        category="comprehensive_analysis",
                        confidence=0.85,
                        impact_score=0.8,
                        data_sources=["AI Analysis"],
                        recommendations=parsed_result.get("recommendations", []),
                        timestamp=datetime.utcnow(),
                        metadata={
                            "source": "langchain", 
                            "model": "gpt-3.5-turbo",
                            "executive_summary": parsed_result.get("executive_summary", ""),
                            "risk_assessment": parsed_result.get("risk_assessment", ""),
                            "opportunities": parsed_result.get("opportunities", "")
                        }
                    )
                    insights.append(insight)
                
                return insights
                
            except json.JSONDecodeError:
                logger.error("Failed to parse LangChain comprehensive analysis result")
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate AI comprehensive insights: {str(e)}")
            return []
    
    async def _create_recommendations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create business recommendations based on insights"""
        insights = parameters.get("insights", [])
        business_context = parameters.get("business_context", {})
        recommendation_categories = parameters.get("categories", ["operational", "strategic", "tactical"])
        
        if not insights:
            raise ValueError("No insights provided for recommendation creation")
        
        try:
            recommendations = []
            
            # Convert insight dicts to BusinessInsight objects if needed
            insight_objects = []
            for insight in insights:
                if isinstance(insight, dict):
                    insight_objects.append(self._dict_to_insight(insight))
                else:
                    insight_objects.append(insight)
            
            # Generate recommendations for each insight
            for insight in insight_objects:
                insight_recommendations = await self._generate_recommendations_for_insight(
                    insight, business_context
                )
                recommendations.extend(insight_recommendations)
            
            # Prioritize recommendations
            prioritized_recommendations = self._prioritize_recommendations(recommendations)
            
            # Store recommendations in database
            for recommendation in prioritized_recommendations:
                self.recommendations_database[recommendation.recommendation_id] = recommendation
            
            logger.info(
                "Recommendations created",
                recommendation_count=len(prioritized_recommendations),
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "create_recommendations",
                "recommendations": [self._recommendation_to_dict(rec) for rec in prioritized_recommendations],
                "recommendation_count": len(prioritized_recommendations),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Recommendation creation failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _generate_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive business intelligence report"""
        insights = parameters.get("insights", [])
        recommendations = parameters.get("recommendations", [])
        analysis_results = parameters.get("analysis_results", {})
        report_type = parameters.get("report_type", "comprehensive")
        time_period = parameters.get("time_period", "monthly")
        
        try:
            report = {
                "report_id": f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "report_type": report_type,
                "time_period": time_period,
                "generated_at": datetime.utcnow().isoformat(),
                "executive_summary": await self._generate_executive_summary(insights, recommendations),
                "key_findings": await self._extract_key_findings(insights),
                "recommendations": await self._summarize_recommendations(recommendations),
                "data_summary": await self._summarize_data(analysis_results),
                "risk_assessment": await self._assess_risks(insights, recommendations),
                "opportunity_analysis": await self._analyze_opportunities(insights, recommendations),
                "next_steps": await self._suggest_next_steps(recommendations)
            }
            
            logger.info(
                "Report generated",
                report_id=report["report_id"],
                report_type=report_type,
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "generate_report",
                "report": report,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Report generation failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _predictive_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform predictive analysis and forecasting"""
        historical_data = parameters.get("historical_data")
        forecast_periods = parameters.get("forecast_periods", 12)
        forecast_variables = parameters.get("forecast_variables", [])
        confidence_level = parameters.get("confidence_level", 0.95)
        
        if not historical_data:
            raise ValueError("No historical data provided for predictive analysis")
        
        try:
            predictions = {}
            
            # Simple trend-based forecasting
            for variable in forecast_variables:
                if variable in historical_data:
                    variable_predictions = await self._forecast_variable(
                        historical_data[variable], forecast_periods, confidence_level
                    )
                    predictions[variable] = variable_predictions
            
            # Scenario analysis
            scenarios = await self._generate_scenarios(predictions, parameters)
            
            # Risk assessment for predictions
            risk_assessment = await self._assess_prediction_risks(predictions, historical_data)
            
            logger.info(
                "Predictive analysis completed",
                variables_forecasted=len(predictions),
                forecast_periods=forecast_periods,
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "predictive_analysis",
                "predictions": predictions,
                "scenarios": scenarios,
                "risk_assessment": risk_assessment,
                "forecast_periods": forecast_periods,
                "confidence_level": confidence_level,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Predictive analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _kpi_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Key Performance Indicators"""
        kpi_data = parameters.get("kpi_data")
        kpi_framework = parameters.get("kpi_framework", "balanced_scorecard")
        target_values = parameters.get("target_values", {})
        time_period = parameters.get("time_period", "monthly")
        
        if not kpi_data:
            raise ValueError("No KPI data provided for analysis")
        
        try:
            kpi_analysis = {
                "framework": kpi_framework,
                "time_period": time_period,
                "kpi_performance": {},
                "target_achievement": {},
                "trend_analysis": {},
                "recommendations": []
            }
            
            # Analyze each KPI
            for kpi_name, kpi_values in kpi_data.items():
                kpi_performance = await self._analyze_kpi_performance(
                    kpi_name, kpi_values, target_values.get(kpi_name)
                )
                kpi_analysis["kpi_performance"][kpi_name] = kpi_performance
                
                # Check target achievement
                if kpi_name in target_values:
                    achievement = await self._assess_target_achievement(
                        kpi_values, target_values[kpi_name]
                    )
                    kpi_analysis["target_achievement"][kpi_name] = achievement
                
                # Trend analysis
                trend = await self._analyze_kpi_trend(kpi_values)
                kpi_analysis["trend_analysis"][kpi_name] = trend
            
            # Generate KPI-specific recommendations
            kpi_recommendations = await self._generate_kpi_recommendations(kpi_analysis)
            kpi_analysis["recommendations"] = kpi_recommendations
            
            logger.info(
                "KPI analysis completed",
                kpi_count=len(kpi_data),
                framework=kpi_framework,
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "kpi_analysis",
                "kpi_analysis": kpi_analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "KPI analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _competitive_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform competitive analysis"""
        competitor_data = parameters.get("competitor_data")
        market_data = parameters.get("market_data")
        company_data = parameters.get("company_data")
        analysis_dimensions = parameters.get("dimensions", ["performance", "positioning", "capabilities"])
        
        if not competitor_data:
            raise ValueError("No competitor data provided for analysis")
        
        try:
            competitive_analysis = {
                "market_position": await self._analyze_market_position(company_data, competitor_data),
                "competitive_advantages": await self._identify_competitive_advantages(company_data, competitor_data),
                "threat_analysis": await self._analyze_competitive_threats(competitor_data, market_data),
                "opportunity_analysis": await self._analyze_competitive_opportunities(competitor_data, market_data),
                "benchmarking": await self._perform_benchmarking(company_data, competitor_data),
                "strategic_recommendations": []
            }
            
            # Generate strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(competitive_analysis)
            competitive_analysis["strategic_recommendations"] = strategic_recommendations
            
            logger.info(
                "Competitive analysis completed",
                competitor_count=len(competitor_data),
                dimensions=analysis_dimensions,
                agent_id=self.agent_id
            )
            
            return {
                "task_type": "competitive_analysis",
                "competitive_analysis": competitive_analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Competitive analysis failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _generate_comprehensive_insights(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive insights from multiple market analysis results"""
        analysis_results = parameters.get("analysis_results", {})
        market_context = parameters.get("market_context", {})
        
        if not analysis_results:
            raise ValueError("No analysis results provided for comprehensive insight generation")
        
        try:
            comprehensive_insights = {
                "task_type": "generate_comprehensive_insights",
                "timestamp": datetime.utcnow().isoformat(),
                "market_overview": {},
                "cross_market_insights": [],
                "risk_assessment": {},
                "opportunity_analysis": {},
                "strategic_recommendations": []
            }
            
            # Analyze market overview
            markets_analyzed = list(analysis_results.keys())
            comprehensive_insights["market_overview"] = {
                "markets_analyzed": markets_analyzed,
                "total_markets": len(markets_analyzed),
                "analysis_date": market_context.get("analysis_date", datetime.utcnow().isoformat()),
                "risk_level": market_context.get("risk_level", "medium")
            }
            
            # Generate cross-market insights
            market_sentiments = {}
            total_market_cap = 0
            
            for market_type, market_data in analysis_results.items():
                if isinstance(market_data, dict):
                    # Extract market sentiment
                    if "market_overview" in market_data:
                        market_overview = market_data["market_overview"]
                        if "market_sentiment" in market_overview:
                            market_sentiments[market_type] = market_overview["market_sentiment"]
                    
                    # Extract market cap if available
                    if market_type == "stocks" and "market_overview" in market_data:
                        total_market_cap += market_data["market_overview"].get("total_market_cap", 0)
                    elif market_type == "crypto" and "market_overview" in market_data:
                        total_market_cap += market_data["market_overview"].get("total_market_cap", 0)
            
            # Cross-market sentiment analysis
            bullish_markets = sum(1 for sentiment in market_sentiments.values() if sentiment == "bullish")
            bearish_markets = sum(1 for sentiment in market_sentiments.values() if sentiment == "bearish")
            
            if len(market_sentiments) > 0:
                overall_sentiment = "bullish" if bullish_markets > bearish_markets else "bearish" if bearish_markets > bullish_markets else "neutral"
                
                comprehensive_insights["cross_market_insights"].append({
                    "insight_id": f"cross_market_sentiment_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    "title": f"Overall market sentiment is {overall_sentiment}",
                    "description": f"Analysis across {len(market_sentiments)} markets shows {bullish_markets} bullish, {bearish_markets} bearish markets",
                    "category": "market_sentiment",
                    "confidence": 0.8,
                    "impact_score": 0.9
                })
            
            # Risk assessment
            comprehensive_insights["risk_assessment"] = {
                "high_risk_markets": [market for market, sentiment in market_sentiments.items() if sentiment == "bearish"],
                "medium_risk_markets": [market for market, sentiment in market_sentiments.items() if sentiment == "neutral"],
                "low_risk_markets": [market for market, sentiment in market_sentiments.items() if sentiment == "bullish"],
                "overall_risk_level": "high" if bearish_markets > bullish_markets else "low" if bullish_markets > bearish_markets else "medium"
            }
            
            # Opportunity analysis
            comprehensive_insights["opportunity_analysis"] = {
                "growth_markets": [market for market, sentiment in market_sentiments.items() if sentiment == "bullish"],
                "stabilization_markets": [market for market, sentiment in market_sentiments.items() if sentiment == "neutral"],
                "recovery_markets": [market for market, sentiment in market_sentiments.items() if sentiment == "bearish"],
                "total_market_cap": total_market_cap
            }
            
            # Strategic recommendations
            if overall_sentiment == "bullish":
                comprehensive_insights["strategic_recommendations"].extend([
                    "Consider increasing exposure to growth markets",
                    "Monitor for potential market corrections",
                    "Diversify across multiple market types"
                ])
            elif overall_sentiment == "bearish":
                comprehensive_insights["strategic_recommendations"].extend([
                    "Implement defensive strategies",
                    "Focus on capital preservation",
                    "Look for contrarian opportunities"
                ])
            else:
                comprehensive_insights["strategic_recommendations"].extend([
                    "Maintain balanced portfolio allocation",
                    "Monitor market developments closely",
                    "Prepare for potential trend changes"
                ])
            
            logger.info(
                "Comprehensive insights generated",
                markets_analyzed=len(markets_analyzed),
                overall_sentiment=overall_sentiment if 'overall_sentiment' in locals() else "unknown",
                agent_id=self.agent_id
            )
            
            return comprehensive_insights
            
        except Exception as e:
            logger.error(
                "Comprehensive insight generation failed",
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    # Helper methods for insight generation
    async def _generate_trend_insights(self, trend_analysis: Dict[str, Any], business_context: Dict[str, Any]) -> List[BusinessInsight]:
        """Generate insights from trend analysis"""
        insights = []
        
        if "linear_trend" in trend_analysis:
            trend = trend_analysis["linear_trend"]
            slope = trend.get("slope", 0)
            r_squared = trend.get("r_squared", 0)
            trend_direction = trend.get("trend_direction", "stable")
            
            if abs(slope) > 0.1 and r_squared > 0.3:
                insight = BusinessInsight(
                    insight_id=f"trend_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    title=f"Strong {trend_direction} trend detected",
                    description=f"Data shows a {trend_direction} trend with {r_squared:.2%} confidence",
                    category="trends",
                    confidence=r_squared,
                    impact_score=min(abs(slope) * 10, 1.0),
                    data_sources=["trend_analysis"],
                    recommendations=[
                        "Monitor trend continuation",
                        "Adjust strategies based on trend direction",
                        "Set up alerts for trend changes"
                    ],
                    timestamp=datetime.utcnow(),
                    metadata={"slope": slope, "r_squared": r_squared}
                )
                insights.append(insight)
        
        return insights
    
    async def _generate_pattern_insights(self, pattern_analysis: Dict[str, Any], business_context: Dict[str, Any]) -> List[BusinessInsight]:
        """Generate insights from pattern recognition"""
        insights = []
        
        if "numerical_patterns" in pattern_analysis:
            for column, patterns in pattern_analysis["numerical_patterns"].items():
                if "outliers" in patterns and len(patterns["outliers"]) > 0:
                    insight = BusinessInsight(
                        insight_id=f"outlier_{column}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        title=f"Outliers detected in {column}",
                        description=f"Found {len(patterns['outliers'])} outliers in {column} data",
                        category="anomalies",
                        confidence=0.8,
                        impact_score=0.7,
                        data_sources=["pattern_analysis"],
                        recommendations=[
                            "Investigate outlier causes",
                            "Consider data quality improvements",
                            "Review business processes"
                        ],
                        timestamp=datetime.utcnow(),
                        metadata={"column": column, "outlier_count": len(patterns["outliers"])}
                    )
                    insights.append(insight)
        
        return insights
    
    async def _generate_anomaly_insights(self, anomaly_analysis: Dict[str, Any], business_context: Dict[str, Any]) -> List[BusinessInsight]:
        """Generate insights from anomaly detection"""
        insights = []
        
        total_anomalies = anomaly_analysis.get("total_anomalies", 0)
        
        if total_anomalies > 0:
            insight = BusinessInsight(
                insight_id=f"anomaly_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                title=f"{total_anomalies} anomalies detected",
                description=f"Anomaly detection identified {total_anomalies} unusual data points",
                category="anomalies",
                confidence=0.9,
                impact_score=0.8,
                data_sources=["anomaly_detection"],
                recommendations=[
                    "Investigate anomaly root causes",
                    "Implement anomaly monitoring",
                    "Review data collection processes"
                ],
                timestamp=datetime.utcnow(),
                metadata={"total_anomalies": total_anomalies}
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_statistical_insights(self, statistical_analysis: Dict[str, Any], business_context: Dict[str, Any]) -> List[BusinessInsight]:
        """Generate insights from statistical analysis"""
        insights = []
        
        if "correlations" in statistical_analysis:
            strong_correlations = statistical_analysis["correlations"].get("strong_correlations", [])
            
            for correlation in strong_correlations:
                insight = BusinessInsight(
                    insight_id=f"correlation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    title=f"Strong correlation between {correlation['feature1']} and {correlation['feature2']}",
                    description=f"Correlation coefficient: {correlation['correlation']:.3f}",
                    category="relationships",
                    confidence=abs(correlation['correlation']),
                    impact_score=0.6,
                    data_sources=["statistical_analysis"],
                    recommendations=[
                        "Investigate causal relationships",
                        "Consider feature engineering",
                        "Monitor correlation stability"
                    ],
                    timestamp=datetime.utcnow(),
                    metadata=correlation
                )
                insights.append(insight)
        
        return insights
    
    async def _generate_kpi_insights(self, kpi_data: Dict[str, Any], business_context: Dict[str, Any]) -> List[BusinessInsight]:
        """Generate insights from KPI data"""
        insights = []
        
        for kpi_name, kpi_values in kpi_data.items():
            if isinstance(kpi_values, (list, tuple)) and len(kpi_values) > 1:
                # Calculate KPI trend
                trend = np.polyfit(range(len(kpi_values)), kpi_values, 1)[0]
                
                if abs(trend) > 0.01:  # Significant trend
                    direction = "improving" if trend > 0 else "declining"
                    insight = BusinessInsight(
                        insight_id=f"kpi_{kpi_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        title=f"KPI {kpi_name} is {direction}",
                        description=f"{kpi_name} shows a {direction} trend over time",
                        category="performance",
                        confidence=0.7,
                        impact_score=0.8,
                        data_sources=["kpi_data"],
                        recommendations=[
                            f"Continue monitoring {kpi_name}",
                            "Identify factors driving the trend",
                            "Set up automated KPI tracking"
                        ],
                        timestamp=datetime.utcnow(),
                        metadata={"kpi_name": kpi_name, "trend": trend}
                    )
                    insights.append(insight)
        
        return insights
    
    async def _generate_recommendations_for_insight(self, insight: BusinessInsight, business_context: Dict[str, Any]) -> List[Recommendation]:
        """Generate recommendations for a specific insight"""
        recommendations = []
        
        # Generate recommendations based on insight category
        if insight.category == "trends":
            recommendations.extend([
                Recommendation(
                    recommendation_id=f"rec_{insight.insight_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    title="Implement trend monitoring",
                    description="Set up automated monitoring for the identified trend",
                    category="operational",
                    priority="medium",
                    expected_impact="Improved decision making",
                    implementation_effort="low",
                    timeline="2-4 weeks",
                    cost_estimate="Low",
                    risk_level="low",
                    dependencies=["data infrastructure"],
                    timestamp=datetime.utcnow()
                )
            ])
        
        elif insight.category == "anomalies":
            recommendations.extend([
                Recommendation(
                    recommendation_id=f"rec_{insight.insight_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    title="Investigate anomaly root causes",
                    description="Conduct thorough investigation of identified anomalies",
                    category="operational",
                    priority="high",
                    expected_impact="Risk mitigation",
                    implementation_effort="medium",
                    timeline="1-2 weeks",
                    cost_estimate="Medium",
                    risk_level="medium",
                    dependencies=["data access", "domain expertise"],
                    timestamp=datetime.utcnow()
                )
            ])
        
        return recommendations
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Prioritize recommendations based on impact and effort"""
        # Simple prioritization based on priority field
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: priority_order.get(x.priority, 0),
            reverse=True
        )
        
        return sorted_recommendations
    
    # Helper methods for report generation
    async def _generate_executive_summary(self, insights: List[Any], recommendations: List[Any]) -> str:
        """Generate executive summary for report"""
        insight_count = len(insights)
        recommendation_count = len(recommendations)
        
        summary = f"""
        Executive Summary
        
        This report presents {insight_count} key business insights and {recommendation_count} strategic recommendations 
        based on comprehensive data analysis. The analysis reveals important trends, patterns, and opportunities 
        that require immediate attention from leadership.
        
        Key Highlights:
        - {insight_count} critical insights identified
        - {recommendation_count} actionable recommendations developed
        - Risk assessment completed
        - Opportunity analysis performed
        
        Next Steps:
        - Review and prioritize recommendations
        - Assign ownership for implementation
        - Establish monitoring and tracking mechanisms
        """
        
        return summary.strip()
    
    async def _extract_key_findings(self, insights: List[Any]) -> List[Dict[str, Any]]:
        """Extract key findings from insights"""
        key_findings = []
        
        for insight in insights:
            if isinstance(insight, dict):
                key_findings.append({
                    "title": insight.get("title", "Unknown"),
                    "description": insight.get("description", ""),
                    "category": insight.get("category", "general"),
                    "confidence": insight.get("confidence", 0.0),
                    "impact_score": insight.get("impact_score", 0.0)
                })
            else:
                key_findings.append({
                    "title": insight.title,
                    "description": insight.description,
                    "category": insight.category,
                    "confidence": insight.confidence,
                    "impact_score": insight.impact_score
                })
        
        return key_findings
    
    async def _summarize_recommendations(self, recommendations: List[Any]) -> List[Dict[str, Any]]:
        """Summarize recommendations for report"""
        summary = []
        
        for rec in recommendations:
            if isinstance(rec, dict):
                summary.append({
                    "title": rec.get("title", "Unknown"),
                    "priority": rec.get("priority", "medium"),
                    "expected_impact": rec.get("expected_impact", ""),
                    "timeline": rec.get("timeline", ""),
                    "effort": rec.get("implementation_effort", "")
                })
            else:
                summary.append({
                    "title": rec.title,
                    "priority": rec.priority,
                    "expected_impact": rec.expected_impact,
                    "timeline": rec.timeline,
                    "effort": rec.implementation_effort
                })
        
        return summary
    
    async def _summarize_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize data analysis results"""
        summary = {
            "analysis_types": list(analysis_results.keys()),
            "data_points": 0,
            "time_range": {},
            "key_metrics": {}
        }
        
        # Extract basic information from analysis results
        for analysis_type, results in analysis_results.items():
            if isinstance(results, dict):
                if "data_points" in results:
                    summary["data_points"] = max(summary["data_points"], results["data_points"])
                
                if "time_range" in results:
                    summary["time_range"] = results["time_range"]
        
        return summary
    
    async def _assess_risks(self, insights: List[Any], recommendations: List[Any]) -> Dict[str, Any]:
        """Assess risks based on insights and recommendations"""
        risk_assessment = {
            "high_risks": [],
            "medium_risks": [],
            "low_risks": [],
            "risk_mitigation_strategies": []
        }
        
        # Analyze insights for risks
        for insight in insights:
            if isinstance(insight, dict):
                category = insight.get("category", "")
                impact_score = insight.get("impact_score", 0.0)
            else:
                category = insight.category
                impact_score = insight.impact_score
            
            if category == "anomalies" and impact_score > 0.7:
                risk_assessment["high_risks"].append(f"Anomaly detected in {category}")
            elif impact_score > 0.5:
                risk_assessment["medium_risks"].append(f"Moderate risk in {category}")
            else:
                risk_assessment["low_risks"].append(f"Low risk in {category}")
        
        return risk_assessment
    
    async def _analyze_opportunities(self, insights: List[Any], recommendations: List[Any]) -> Dict[str, Any]:
        """Analyze opportunities based on insights and recommendations"""
        opportunities = {
            "immediate_opportunities": [],
            "medium_term_opportunities": [],
            "long_term_opportunities": [],
            "opportunity_priorities": []
        }
        
        # Analyze insights for opportunities
        for insight in insights:
            if isinstance(insight, dict):
                category = insight.get("category", "")
                impact_score = insight.get("impact_score", 0.0)
            else:
                category = insight.category
                impact_score = insight.impact_score
            
            if category == "trends" and impact_score > 0.6:
                opportunities["immediate_opportunities"].append(f"Leverage {category} trend")
            elif impact_score > 0.4:
                opportunities["medium_term_opportunities"].append(f"Explore {category} opportunities")
            else:
                opportunities["long_term_opportunities"].append(f"Monitor {category} developments")
        
        return opportunities
    
    async def _suggest_next_steps(self, recommendations: List[Any]) -> List[str]:
        """Suggest next steps based on recommendations"""
        next_steps = [
            "Review and prioritize all recommendations",
            "Assign ownership and timelines for implementation",
            "Establish monitoring and tracking mechanisms",
            "Schedule follow-up review meetings",
            "Communicate findings to stakeholders"
        ]
        
        return next_steps
    
    # Helper methods for predictive analysis
    async def _forecast_variable(self, historical_data: List[float], periods: int, confidence_level: float) -> Dict[str, Any]:
        """Forecast a single variable"""
        if len(historical_data) < 2:
            return {"error": "Insufficient historical data"}
        
        try:
            # Simple linear trend forecasting
            x = np.arange(len(historical_data))
            slope, intercept = np.polyfit(x, historical_data, 1)
            
            # Generate forecast
            future_x = np.arange(len(historical_data), len(historical_data) + periods)
            forecast_values = slope * future_x + intercept
            
            # Calculate confidence intervals (simplified)
            residuals = historical_data - (slope * x + intercept)
            std_error = np.std(residuals)
            confidence_interval = stats.norm.ppf((1 + confidence_level) / 2) * std_error
            
            return {
                "forecast_values": forecast_values.tolist(),
                "confidence_intervals": {
                    "upper": (forecast_values + confidence_interval).tolist(),
                    "lower": (forecast_values - confidence_interval).tolist()
                },
                "trend_slope": float(slope),
                "confidence_level": confidence_level
            }
            
        except Exception as e:
            return {"error": f"Forecasting failed: {str(e)}"}
    
    async def _generate_scenarios(self, predictions: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate different scenarios for predictions"""
        scenarios = {
            "optimistic": {},
            "baseline": {},
            "pessimistic": {}
        }
        
        for variable, prediction in predictions.items():
            if "forecast_values" in prediction:
                baseline = prediction["forecast_values"]
                scenarios["baseline"][variable] = baseline
                scenarios["optimistic"][variable] = [v * 1.1 for v in baseline]  # 10% better
                scenarios["pessimistic"][variable] = [v * 0.9 for v in baseline]  # 10% worse
        
        return scenarios
    
    async def _assess_prediction_risks(self, predictions: Dict[str, Any], historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with predictions"""
        risk_assessment = {
            "data_quality_risks": [],
            "model_uncertainty": {},
            "external_factors": [],
            "confidence_levels": {}
        }
        
        for variable, prediction in predictions.items():
            if "error" not in prediction:
                # Assess model uncertainty based on historical volatility
                if variable in historical_data:
                    historical_values = historical_data[variable]
                    if len(historical_values) > 1:
                        volatility = np.std(historical_values) / np.mean(historical_values)
                        risk_assessment["model_uncertainty"][variable] = {
                            "volatility": float(volatility),
                            "risk_level": "high" if volatility > 0.5 else "medium" if volatility > 0.2 else "low"
                        }
        
        return risk_assessment
    
    # Helper methods for KPI analysis
    async def _analyze_kpi_performance(self, kpi_name: str, kpi_values: List[float], target_value: Optional[float]) -> Dict[str, Any]:
        """Analyze performance of a specific KPI"""
        if not kpi_values:
            return {"error": "No KPI values provided"}
        
        analysis = {
            "kpi_name": kpi_name,
            "current_value": kpi_values[-1] if kpi_values else None,
            "average_value": float(np.mean(kpi_values)),
            "trend": "stable",
            "performance_status": "unknown"
        }
        
        # Calculate trend
        if len(kpi_values) > 1:
            trend_slope = np.polyfit(range(len(kpi_values)), kpi_values, 1)[0]
            if trend_slope > 0.01:
                analysis["trend"] = "improving"
            elif trend_slope < -0.01:
                analysis["trend"] = "declining"
        
        # Compare with target
        if target_value is not None:
            current_value = kpi_values[-1] if kpi_values else 0
            if current_value >= target_value:
                analysis["performance_status"] = "on_target"
            else:
                analysis["performance_status"] = "below_target"
                analysis["gap"] = target_value - current_value
        
        return analysis
    
    async def _assess_target_achievement(self, kpi_values: List[float], target_value: float) -> Dict[str, Any]:
        """Assess achievement of KPI target"""
        if not kpi_values:
            return {"achievement_rate": 0.0, "status": "no_data"}
        
        current_value = kpi_values[-1]
        achievement_rate = (current_value / target_value) * 100 if target_value > 0 else 0
        
        return {
            "achievement_rate": float(achievement_rate),
            "status": "achieved" if achievement_rate >= 100 else "below_target",
            "gap_percentage": float(100 - achievement_rate) if achievement_rate < 100 else 0.0
        }
    
    async def _analyze_kpi_trend(self, kpi_values: List[float]) -> Dict[str, Any]:
        """Analyze trend of KPI values"""
        if len(kpi_values) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend
        x = np.arange(len(kpi_values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, kpi_values)
        
        return {
            "trend_direction": "increasing" if slope > 0 else "decreasing",
            "trend_strength": abs(r_value),
            "slope": float(slope),
            "r_squared": float(r_value ** 2),
            "p_value": float(p_value)
        }
    
    async def _generate_kpi_recommendations(self, kpi_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on KPI analysis"""
        recommendations = []
        
        for kpi_name, performance in kpi_analysis.get("kpi_performance", {}).items():
            if performance.get("performance_status") == "below_target":
                recommendations.append(f"Develop action plan to improve {kpi_name}")
            
            if performance.get("trend") == "declining":
                recommendations.append(f"Investigate causes of declining {kpi_name}")
        
        return recommendations
    
    # Helper methods for competitive analysis
    async def _analyze_market_position(self, company_data: Dict[str, Any], competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company's market position relative to competitors"""
        return {
            "market_share": "To be calculated",
            "competitive_position": "To be analyzed",
            "strengths": [],
            "weaknesses": []
        }
    
    async def _identify_competitive_advantages(self, company_data: Dict[str, Any], competitor_data: Dict[str, Any]) -> List[str]:
        """Identify competitive advantages"""
        return ["To be analyzed based on data"]
    
    async def _analyze_competitive_threats(self, competitor_data: Dict[str, Any], market_data: Dict[str, Any]) -> List[str]:
        """Analyze competitive threats"""
        return ["To be analyzed based on data"]
    
    async def _analyze_competitive_opportunities(self, competitor_data: Dict[str, Any], market_data: Dict[str, Any]) -> List[str]:
        """Analyze competitive opportunities"""
        return ["To be analyzed based on data"]
    
    async def _perform_benchmarking(self, company_data: Dict[str, Any], competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform benchmarking analysis"""
        return {
            "performance_benchmarks": {},
            "best_practices": [],
            "improvement_areas": []
        }
    
    async def _generate_strategic_recommendations(self, competitive_analysis: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on competitive analysis"""
        return ["To be generated based on analysis results"]
    
    # Message handling methods
    async def _handle_insight_request(self, message: Message) -> Optional[Message]:
        """Handle insight requests from other agents"""
        content = message.content
        request_type = content.get("request_type")
        parameters = content.get("parameters", {})
        
        try:
            if request_type == "generate_insights":
                result = await self._generate_insights(parameters)
            elif request_type == "create_recommendations":
                result = await self._create_recommendations(parameters)
            elif request_type == "generate_report":
                result = await self._generate_report(parameters)
            else:
                result = {"error": f"Unknown request type: {request_type}"}
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="insight_response",
                content=result,
                correlation_id=message.id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Insight request handling failed",
                request_type=request_type,
                error=str(e),
                agent_id=self.agent_id
            )
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="insight_response",
                content={"error": str(e)},
                correlation_id=message.id
            )
            
            return response
    
    async def _handle_data_analysis_result(self, message: Message) -> Optional[Message]:
        """Handle data analysis results from analyzer agent"""
        content = message.content
        analysis_results = content.get("analysis_results", {})
        
        # Generate insights from analysis results
        try:
            insights = await self._generate_insights({
                "analysis_results": analysis_results,
                "business_context": self.business_context
            })
            
            logger.info(
                "Insights generated from analysis results",
                insight_count=insights.get("insight_count", 0),
                agent_id=self.agent_id
            )
            
        except Exception as e:
            logger.error(
                "Failed to generate insights from analysis results",
                error=str(e),
                agent_id=self.agent_id
            )
        
        return None
    
    async def _handle_business_context_update(self, message: Message) -> Optional[Message]:
        """Handle business context updates"""
        content = message.content
        self.business_context.update(content.get("context", {}))
        
        logger.info(
            "Business context updated",
            context_keys=list(content.get("context", {}).keys()),
            agent_id=self.agent_id
        )
        
        return None
    
    # Utility methods
    def _initialize_business_context(self):
        """Initialize default business context"""
        self.business_context = {
            "industry": "technology",
            "company_size": "medium",
            "business_model": "b2b",
            "key_metrics": ["revenue", "customer_satisfaction", "operational_efficiency"],
            "strategic_priorities": ["growth", "efficiency", "innovation"]
        }
    
    def _insight_to_dict(self, insight: BusinessInsight) -> Dict[str, Any]:
        """Convert BusinessInsight to dictionary"""
        return {
            "insight_id": insight.insight_id,
            "title": insight.title,
            "description": insight.description,
            "category": insight.category,
            "confidence": insight.confidence,
            "impact_score": insight.impact_score,
            "data_sources": insight.data_sources,
            "recommendations": insight.recommendations,
            "timestamp": insight.timestamp.isoformat(),
            "metadata": insight.metadata
        }
    
    def _dict_to_insight(self, insight_dict: Dict[str, Any]) -> BusinessInsight:
        """Convert dictionary to BusinessInsight"""
        return BusinessInsight(
            insight_id=insight_dict.get("insight_id", ""),
            title=insight_dict.get("title", ""),
            description=insight_dict.get("description", ""),
            category=insight_dict.get("category", ""),
            confidence=insight_dict.get("confidence", 0.0),
            impact_score=insight_dict.get("impact_score", 0.0),
            data_sources=insight_dict.get("data_sources", []),
            recommendations=insight_dict.get("recommendations", []),
            timestamp=datetime.fromisoformat(insight_dict.get("timestamp", datetime.utcnow().isoformat())),
            metadata=insight_dict.get("metadata", {})
        )
    
    def _recommendation_to_dict(self, recommendation: Recommendation) -> Dict[str, Any]:
        """Convert Recommendation to dictionary"""
        return {
            "recommendation_id": recommendation.recommendation_id,
            "title": recommendation.title,
            "description": recommendation.description,
            "category": recommendation.category,
            "priority": recommendation.priority,
            "expected_impact": recommendation.expected_impact,
            "implementation_effort": recommendation.implementation_effort,
            "timeline": recommendation.timeline,
            "cost_estimate": recommendation.cost_estimate,
            "risk_level": recommendation.risk_level,
            "dependencies": recommendation.dependencies,
            "timestamp": recommendation.timestamp.isoformat()
        }


# Factory function to create insight generator agent
def create_insight_generator_agent(agent_id: str = None, use_langchain: bool = False) -> InsightGeneratorAgent:
    """Create and return an Insight Generator Agent instance"""
    return InsightGeneratorAgent(agent_id=agent_id, use_langchain=use_langchain) 