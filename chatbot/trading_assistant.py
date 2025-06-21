#!/usr/bin/env python3
"""
AI-Powered Trading Assistant with OpenAI + AI Agents

Uses OpenAI for natural language understanding and conversation,
while calling the AI Business Intelligence agents as tools for market analysis.
"""

import asyncio
import json
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = structlog.get_logger(__name__)

class TradingAssistant:
    """AI-Powered Trading Assistant using OpenAI + AI Agents"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.session = None
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history = []
        
        # Define available tools (your AI agents)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "analyze_stocks",
                    "description": "Analyze stock market data for given symbols using AI agents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbols": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of stock symbols to analyze (e.g., ['TSLA', 'AAPL'])"
                            },
                            "period": {
                                "type": "string",
                                "description": "Time period for analysis (e.g., '1d', '1mo', '3mo')",
                                "default": "1mo"
                            },
                            "interval": {
                                "type": "string",
                                "description": "Data interval (e.g., '1h', '1d')",
                                "default": "1d"
                            }
                        },
                        "required": ["symbols"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_crypto",
                    "description": "Analyze cryptocurrency data for given symbols using AI agents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbols": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of crypto symbols to analyze (e.g., ['BTC-USD', 'ETH-USD'])"
                            }
                        },
                        "required": ["symbols"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_forex",
                    "description": "Analyze forex market data for given currency pairs using AI agents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pairs": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of forex pairs to analyze (e.g., ['EUR/USD', 'GBP/USD'])"
                            }
                        },
                        "required": ["pairs"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_market_overview",
                    "description": "Get overall market overview and sentiment analysis using AI agents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "market_type": {
                                "type": "string",
                                "enum": ["stocks", "crypto", "forex", "all"],
                                "description": "Type of market to analyze",
                                "default": "all"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_trading_recommendations",
                    "description": "Get AI-powered trading recommendations based on market analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbols": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of symbols to get recommendations for"
                            },
                            "market_type": {
                                "type": "string",
                                "enum": ["stocks", "crypto", "forex"],
                                "description": "Type of market"
                            },
                            "risk_tolerance": {
                                "type": "string",
                                "enum": ["conservative", "moderate", "aggressive"],
                                "description": "User's risk tolerance level",
                                "default": "moderate"
                            }
                        },
                        "required": ["symbols", "market_type"]
                    }
                }
            }
        ]
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def process_message(self, user_message: str, user_id: str = "default") -> str:
        """Process user message using OpenAI and AI agents"""
        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Call OpenAI with tools
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an AI-powered trading assistant that helps users with market analysis and trading decisions. 

You have access to specialized AI agents that can:
1. Analyze stocks, crypto, and forex markets
2. Provide real-time market data and insights
3. Generate trading recommendations
4. Monitor market sentiment and trends

Your role is to:
- Understand user requests and call the appropriate tools
- Provide conversational, helpful responses
- Explain complex market concepts in simple terms
- Give actionable trading advice based on AI analysis
- Be honest about risks and limitations

Always be professional, informative, and helpful. When providing analysis, include:
- Current market conditions
- Key technical indicators
- Risk assessment
- Clear recommendations
- Important disclaimers about trading risks

Remember: Past performance doesn't guarantee future results. Always encourage users to do their own research."""
                    },
                    *self.conversation_history
                ],
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Check if OpenAI wants to call a tool
            if message.tool_calls:
                # Add assistant message to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls
                })
                
                # Execute tool calls
                tool_results = []
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Call the appropriate AI agent function
                    result = await self._execute_tool(function_name, function_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                
                # Add tool results to conversation history
                self.conversation_history.extend(tool_results)
                
                # Get final response from OpenAI
                final_response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are an AI-powered trading assistant that helps users with market analysis and trading decisions. 

You have access to specialized AI agents that can:
1. Analyze stocks, crypto, and forex markets
2. Provide real-time market data and insights
3. Generate trading recommendations
4. Monitor market sentiment and trends

Your role is to:
- Understand user requests and call the appropriate tools
- Provide conversational, helpful responses
- Explain complex market concepts in simple terms
- Give actionable trading advice based on AI analysis
- Be honest about risks and limitations

Always be professional, informative, and helpful. When providing analysis, include:
- Current market conditions
- Key technical indicators
- Risk assessment
- Clear recommendations
- Important disclaimers about trading risks

Remember: Past performance doesn't guarantee future results. Always encourage users to do their own research."""
                        },
                        *self.conversation_history
                    ]
                )
                
                final_message = final_response.choices[0].message.content
                
                # Add final response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_message
                })
                
                return final_message
            else:
                # No tool calls needed, return direct response
                response_content = message.content
                
                # Add assistant message to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_content
                })
                
                return response_content
                
        except Exception as e:
            logger.error("Error processing message", error=str(e))
            return "I apologize, but I encountered an error while processing your request. Please try again."
    
    async def _execute_tool(self, function_name: str, function_args: Dict) -> Dict:
        """Execute tool calls by calling the AI Business Intelligence API"""
        try:
            if function_name == "analyze_stocks":
                return await self._analyze_stocks(function_args)
            elif function_name == "analyze_crypto":
                return await self._analyze_crypto(function_args)
            elif function_name == "analyze_forex":
                return await self._analyze_forex(function_args)
            elif function_name == "get_market_overview":
                return await self._get_market_overview(function_args)
            elif function_name == "get_trading_recommendations":
                return await self._get_trading_recommendations(function_args)
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            logger.error(f"Error executing tool {function_name}", error=str(e))
            return {"error": f"Error executing {function_name}: {str(e)}"}
    
    async def _analyze_stocks(self, args: Dict) -> Dict:
        """Analyze stocks using AI agents"""
        symbols = args.get("symbols", [])
        period = args.get("period", "1mo")
        interval = args.get("interval", "1d")
        
        if not symbols:
            return {"error": "No stock symbols provided"}
        
        try:
            payload = {
                "symbols": symbols[:5],  # Limit to 5 symbols
                "period": period,
                "interval": interval
            }
            
            async with self.session.post(f"{self.api_base_url}/analysis/stocks", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    task_id = data.get('task_id')
                    
                    if task_id:
                        # Wait for analysis completion
                        await asyncio.sleep(3)
                        
                        # Get results
                        async with self.session.get(f"{self.api_base_url}/tasks/{task_id}") as task_response:
                            if task_response.status == 200:
                                task_data = await task_response.json()
                                result = task_data.get('result', {})
                                
                                if 'error' not in result:
                                    return {
                                        "success": True,
                                        "task_id": task_id,
                                        "symbols": symbols,
                                        "analysis": result
                                    }
                                else:
                                    return {"error": result['error']}
                            else:
                                return {"error": "Analysis still in progress"}
                else:
                    return {"error": f"API error: {response.status}"}
                    
        except Exception as e:
            logger.error("Error in stock analysis", error=str(e))
            return {"error": f"Error analyzing stocks: {str(e)}"}
    
    async def _analyze_crypto(self, args: Dict) -> Dict:
        """Analyze crypto using AI agents"""
        symbols = args.get("symbols", [])
        
        if not symbols:
            return {"error": "No crypto symbols provided"}
        
        try:
            payload = {
                "symbols": symbols[:5]  # Limit to 5 symbols
            }
            
            async with self.session.post(f"{self.api_base_url}/analysis/crypto", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    task_id = data.get('task_id')
                    
                    if task_id:
                        # Wait for analysis completion
                        await asyncio.sleep(3)
                        
                        # Get results
                        async with self.session.get(f"{self.api_base_url}/tasks/{task_id}") as task_response:
                            if task_response.status == 200:
                                task_data = await task_response.json()
                                result = task_data.get('result', {})
                                
                                if 'error' not in result:
                                    return {
                                        "success": True,
                                        "task_id": task_id,
                                        "symbols": symbols,
                                        "analysis": result
                                    }
                                else:
                                    return {"error": result['error']}
                            else:
                                return {"error": "Analysis still in progress"}
                else:
                    return {"error": f"API error: {response.status}"}
                    
        except Exception as e:
            logger.error("Error in crypto analysis", error=str(e))
            return {"error": f"Error analyzing crypto: {str(e)}"}
    
    async def _analyze_forex(self, args: Dict) -> Dict:
        """Analyze forex using AI agents"""
        pairs = args.get("pairs", [])
        
        if not pairs:
            return {"error": "No forex pairs provided"}
        
        try:
            payload = {
                "pairs": pairs[:5]  # Limit to 5 pairs
            }
            
            async with self.session.post(f"{self.api_base_url}/analysis/forex", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    task_id = data.get('task_id')
                    
                    if task_id:
                        # Wait for analysis completion
                        await asyncio.sleep(3)
                        
                        # Get results
                        async with self.session.get(f"{self.api_base_url}/tasks/{task_id}") as task_response:
                            if task_response.status == 200:
                                task_data = await task_response.json()
                                result = task_data.get('result', {})
                                
                                if 'error' not in result:
                                    return {
                                        "success": True,
                                        "task_id": task_id,
                                        "pairs": pairs,
                                        "analysis": result
                                    }
                                else:
                                    return {"error": result['error']}
                            else:
                                return {"error": "Analysis still in progress"}
                else:
                    return {"error": f"API error: {response.status}"}
                    
        except Exception as e:
            logger.error("Error in forex analysis", error=str(e))
            return {"error": f"Error analyzing forex: {str(e)}"}
    
    async def _get_market_overview(self, args: Dict) -> Dict:
        """Get market overview using AI agents"""
        market_type = args.get("market_type", "all")
        
        try:
            if market_type in ["stocks", "all"]:
                # Analyze major indices
                major_stocks = ['SPY', 'QQQ', 'IWM']  # S&P 500, NASDAQ, Russell 2000
                
                payload = {
                    "symbols": major_stocks,
                    "period": "1d",
                    "interval": "1h"
                }
                
                async with self.session.post(f"{self.api_base_url}/analysis/stocks", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        task_id = data.get('task_id')
                        
                        if task_id:
                            await asyncio.sleep(3)
                            
                            async with self.session.get(f"{self.api_base_url}/tasks/{task_id}") as task_response:
                                if task_response.status == 200:
                                    task_data = await task_response.json()
                                    result = task_data.get('result', {})
                                    
                                    if 'error' not in result:
                                        return {
                                            "success": True,
                                            "market_type": "stocks",
                                            "overview": result
                                        }
                                    else:
                                        return {"error": result['error']}
                                else:
                                    return {"error": "Market overview still in progress"}
                    else:
                        return {"error": f"API error: {response.status}"}
            
            # Add crypto and forex overview if needed
            return {"error": "Market overview not implemented for this market type"}
                    
        except Exception as e:
            logger.error("Error in market overview", error=str(e))
            return {"error": f"Error getting market overview: {str(e)}"}
    
    async def _get_trading_recommendations(self, args: Dict) -> Dict:
        """Get trading recommendations using AI agents"""
        symbols = args.get("symbols", [])
        market_type = args.get("market_type", "stocks")
        risk_tolerance = args.get("risk_tolerance", "moderate")
        
        if not symbols:
            return {"error": "No symbols provided for recommendations"}
        
        try:
            # First analyze the symbols
            if market_type == "stocks":
                analysis_result = await self._analyze_stocks({"symbols": symbols})
            elif market_type == "crypto":
                analysis_result = await self._analyze_crypto({"symbols": symbols})
            elif market_type == "forex":
                analysis_result = await self._analyze_forex({"pairs": symbols})
            else:
                return {"error": f"Unsupported market type: {market_type}"}
            
            if "error" in analysis_result:
                return analysis_result
            
            # Generate recommendations based on analysis
            analysis = analysis_result.get("analysis", {})
            
            recommendations = []
            for symbol in symbols:
                if market_type == "stocks":
                    stock_key = symbol.lower()
                    stock_analysis = analysis.get(f"{stock_key}_analysis", {})
                    
                    if stock_analysis:
                        trend = stock_analysis.get('price_trend', {}).get('trend_direction', 'stable')
                        price_change = stock_analysis.get('price_trend', {}).get('price_change_30d', 0)
                        current_price = stock_analysis.get('current_price', 0)
                        
                        # Generate recommendation based on analysis and risk tolerance
                        if trend == 'up' and price_change > 5:
                            if risk_tolerance == "aggressive":
                                recommendation = "BUY"
                                confidence = "High"
                                reasoning = "Strong bullish momentum with significant price appreciation"
                            elif risk_tolerance == "moderate":
                                recommendation = "BUY"
                                confidence = "Medium"
                                reasoning = "Bullish trend but consider waiting for pullback"
                            else:  # conservative
                                recommendation = "HOLD"
                                confidence = "Medium"
                                reasoning = "Bullish but high volatility - wait for confirmation"
                        elif trend == 'down' and price_change < -5:
                            recommendation = "SELL"
                            confidence = "High"
                            reasoning = "Bearish trend with significant decline"
                        else:
                            recommendation = "HOLD"
                            confidence = "Medium"
                            reasoning = "Sideways movement - monitor for breakout"
                        
                        recommendations.append({
                            "symbol": symbol,
                            "recommendation": recommendation,
                            "confidence": confidence,
                            "reasoning": reasoning,
                            "current_price": current_price,
                            "trend": trend,
                            "price_change_30d": price_change
                        })
            
            return {
                "success": True,
                "market_type": market_type,
                "risk_tolerance": risk_tolerance,
                "recommendations": recommendations,
                "analysis": analysis
            }
                    
        except Exception as e:
            logger.error("Error in trading recommendations", error=str(e))
            return {"error": f"Error generating recommendations: {str(e)}"}
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


# Interactive demo function
async def demo_chatbot():
    """Demo the trading assistant chatbot"""
    print("🤖 AI Trading Assistant with OpenAI + AI Agents")
    print("=" * 60)
    print("This chatbot uses OpenAI for conversation and AI agents for analysis")
    print("Type 'quit' to exit, 'clear' to clear history")
    print()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file or environment variable")
        return
    
    async with TradingAssistant() as assistant:
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Assistant: Goodbye! Happy trading! 📈")
                    break
                
                if user_input.lower() == 'clear':
                    assistant.clear_history()
                    print("Assistant: Conversation history cleared!")
                    continue
                
                if not user_input:
                    continue
                
                print("Assistant: ", end="", flush=True)
                
                # Get AI response
                response = await assistant.process_message(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\nAssistant: Goodbye! Happy trading! 📈")
                break
            except Exception as e:
                print(f"Assistant: I encountered an error: {str(e)}")
                print()


if __name__ == "__main__":
    asyncio.run(demo_chatbot()) 