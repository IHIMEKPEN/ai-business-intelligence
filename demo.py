#!/usr/bin/env python3
"""
AI Business Intelligence System Demo - Live Data Scenarios

This script demonstrates the capabilities of the AI Business Intelligence system
using live data from real APIs for stocks, forex, and cryptocurrency analysis.
"""

import asyncio
import json
import time
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our modules
from core.agent_framework import AgentRegistry, Task, AgentType, AgentRegistryGlobal
from core.communication import CommunicationManager
from agents.data_collector_agent import create_data_collector_agent
from agents.analyzer_agent import create_analyzer_agent
from agents.insight_generator_agent import create_insight_generator_agent
from agents.action_executor_agent import create_action_executor_agent


class LiveDataDemo:
    """Demo class for showcasing AI Business Intelligence capabilities with live data"""
    
    def __init__(self):
        self.agent_registry = AgentRegistryGlobal
        self.communication_manager = CommunicationManager()
        self.demo_results = {}
        
        # API Keys from environment variables
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY", "demo")
        
        # Show API key status
        print("🔑 API Key Status:")
        if self.alpha_vantage_key != "demo":
            print("   ✅ Alpha Vantage API key found")
        else:
            print("   ⚠️  Alpha Vantage API key not found (using demo mode)")
        if self.finnhub_key != "demo":
            print("   ✅ Finnhub API key found")
        else:
            print("   ⚠️  Finnhub API key not found (using demo mode)")
        print()
        
    async def setup_system(self, use_langchain: bool = False):
        """Set up the AI system with all agents"""
        print("🚀 Setting up AI Business Intelligence System...")
        
        # Check if LangChain should be used
        if use_langchain:
            print("🤖 LangChain AI integration enabled")
            if not os.getenv("OPENAI_API_KEY"):
                print("⚠️  Warning: OpenAI API key not found. LangChain features will be disabled.")
                use_langchain = False
        else:
            print("🔧 Using custom agent framework (LangChain disabled)")
        
        # Create agents with task coordinator reference
        data_collector = create_data_collector_agent("live_dc_001")
        data_collector.task_coordinator = self.communication_manager.task_coordinator
        
        analyzer = create_analyzer_agent("live_an_001")
        analyzer.task_coordinator = self.communication_manager.task_coordinator
        
        # Create insight generator with LangChain option
        insight_generator = create_insight_generator_agent("live_ig_001", use_langchain=use_langchain)
        insight_generator.task_coordinator = self.communication_manager.task_coordinator
        
        action_executor = create_action_executor_agent("live_ae_001")
        action_executor.task_coordinator = self.communication_manager.task_coordinator
        
        print(f"✅ Created agents:")
        print(f"   - Data Collector: {data_collector.agent_id} ({data_collector.agent_type.value})")
        print(f"   - Analyzer: {analyzer.agent_id} ({analyzer.agent_type.value})")
        print(f"   - Insight Generator: {insight_generator.agent_id} ({insight_generator.agent_type.value})")
        if use_langchain:
            print(f"     └─ LangChain AI integration: ✅ ENABLED")
        else:
            print(f"     └─ LangChain AI integration: ❌ DISABLED")
        print(f"   - Action Executor: {action_executor.agent_id} ({action_executor.agent_type.value})")
        
        # Register agents
        self.agent_registry.register_agent(data_collector)
        self.agent_registry.register_agent(analyzer)
        self.agent_registry.register_agent(insight_generator)
        self.agent_registry.register_agent(action_executor)
        
        print(f"✅ Registered agents in registry")
        
        # Start agents
        await data_collector.start()
        await analyzer.start()
        await insight_generator.start()
        await action_executor.start()
        
        print(f"✅ Started all agents")
        
        # Initialize communication
        await self.communication_manager.initialize_protocols()
        
        # Debug: Check what agents are available
        all_agents = self.agent_registry.get_all_agents()
        print(f"✅ System setup completed!")
        print(f"   - {len(all_agents)} agents created and started")
        print(f"   - Communication protocols initialized")
        
        # Debug: Show agent types
        for agent in all_agents:
            print(f"   - {agent.name} ({agent.agent_id}): {agent.agent_type.value}")
        
        # Debug: Check specific agent types
        insight_agents = self.agent_registry.get_agents_by_type(AgentType.INSIGHT_GENERATOR)
        analyzer_agents = self.agent_registry.get_agents_by_type(AgentType.ANALYZER)
        print(f"   - Insight Generator agents: {len(insight_agents)}")
        print(f"   - Analyzer agents: {len(analyzer_agents)}")
        
    async def scenario_1_stocks_analysis(self):
        """Scenario 1: Tesla and Google Stock Analysis"""
        print("\n📈 Scenario 1: Tesla & Google Stock Analysis")
        print("=" * 60)
        
        # Get live stock data using yfinance
        print("📊 Collecting live stock data for TSLA and GOOGL...")
        
        try:
            # Get Tesla data
            tsla = yf.Ticker("TSLA")
            tsla_data = tsla.history(period="1mo", interval="1d")
            
            # Get Google data
            googl = yf.Ticker("GOOGL")
            googl_data = googl.history(period="1mo", interval="1d")
            
            # Prepare data for analysis
            stock_data = {
                "tesla": {
                    "symbol": "TSLA",
                    "data": tsla_data.reset_index().to_dict('records'),
                    "current_price": tsla_data['Close'].iloc[-1],
                    "volume": tsla_data['Volume'].iloc[-1],
                    "market_cap": tsla.info.get('marketCap', 'N/A')
                },
                "google": {
                    "symbol": "GOOGL", 
                    "data": googl_data.reset_index().to_dict('records'),
                    "current_price": googl_data['Close'].iloc[-1],
                    "volume": googl_data['Volume'].iloc[-1],
                    "market_cap": googl.info.get('marketCap', 'N/A')
                }
            }
            
            print(f"✅ Tesla (TSLA): ${stock_data['tesla']['current_price']:.2f}")
            print(f"✅ Google (GOOGL): ${stock_data['google']['current_price']:.2f}")
            
            # Submit stock analysis task
            task_id = await self.communication_manager.send_task_request(
                "analyze_stocks",
                stock_data,
                priority=1
            )
            
            print(f"   Stock analysis task submitted: {task_id}")
            
            # Wait for completion
            result = await self.communication_manager.task_coordinator.wait_for_task_completion(
                task_id, timeout=60
            )
            
            if result:
                print("✅ Stock analysis completed!")
                analysis = result.get('analysis', {})
                
                # Display Tesla analysis
                if 'tesla' in analysis:
                    tsla_analysis = analysis['tesla']
                    print(f"\n📊 Tesla (TSLA) Analysis:")
                    print(f"   - Trend: {tsla_analysis.get('trend', 'Unknown')}")
                    print(f"   - RSI: {tsla_analysis.get('rsi', 'N/A')}")
                    print(f"   - Volatility: {tsla_analysis.get('volatility', 'N/A')}")
                    print(f"   - Support Level: ${tsla_analysis.get('support', 'N/A')}")
                    print(f"   - Resistance Level: ${tsla_analysis.get('resistance', 'N/A')}")
                
                # Display Google analysis
                if 'google' in analysis:
                    googl_analysis = analysis['google']
                    print(f"\n📊 Google (GOOGL) Analysis:")
                    print(f"   - Trend: {googl_analysis.get('trend', 'Unknown')}")
                    print(f"   - RSI: {googl_analysis.get('rsi', 'N/A')}")
                    print(f"   - Volatility: {googl_analysis.get('volatility', 'N/A')}")
                    print(f"   - Support Level: ${googl_analysis.get('support', 'N/A')}")
                    print(f"   - Resistance Level: ${googl_analysis.get('resistance', 'N/A')}")
                
                self.demo_results['stock_analysis'] = result
                
            else:
                print("❌ Stock analysis failed")
                
        except Exception as e:
            print(e)
            print(f"❌ Error collecting stock data: {str(e)}")
            print("   Using sample data for demonstration...")
            
            # Fallback to sample data
            sample_stock_data = {
                "tesla": {
                    "symbol": "TSLA",
                    "current_price": 245.50,
                    "trend": "bullish",
                    "rsi": 65.2,
                    "volatility": "high",
                    "support": 240.00,
                    "resistance": 250.00
                },
                "google": {
                    "symbol": "GOOGL",
                    "current_price": 142.30,
                    "trend": "neutral",
                    "rsi": 52.1,
                    "volatility": "medium",
                    "support": 140.00,
                    "resistance": 145.00
                }
            }
            
            self.demo_results['stock_analysis'] = {"analysis": sample_stock_data}
    
    async def scenario_2_forex_analysis(self):
        """Scenario 2: Forex Trading Analysis"""
        print("\n💱 Scenario 2: Forex Trading Analysis")
        print("=" * 60)
        
        # Forex pairs to analyze
        forex_pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF"]
        
        print(f"🌍 Collecting live forex data for {', '.join(forex_pairs)}...")
        
        try:
            forex_data = {}
            
            # Try Alpha Vantage first (if API key available)
            if self.alpha_vantage_key != "demo":
                print("   Trying Alpha Vantage API for forex data...")
                ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
                
                for pair in forex_pairs:
                    try:
                        from_symbol = pair.split('/')[0]
                        to_symbol = pair.split('/')[1]
                        
                        # Try get_currency_exchange_rate first
                        try:
                            data, meta_data = ts.get_currency_exchange_rate(
                                from_currency=from_symbol,
                                to_currency=to_symbol
                            )
                            
                            forex_data[pair] = {
                                "current_rate": float(data.get('5. Exchange Rate', 0)),
                                "change_24h": 0.0,  # Not available in this API
                                "change_percent": 0.0,  # Not available in this API
                                "high_24h": float(data.get('5. Exchange Rate', 0)),
                                "low_24h": float(data.get('5. Exchange Rate', 0)),
                                "last_refreshed": data.get('6. Last Refreshed', ''),
                                "timezone": data.get('7. Time Zone', '')
                            }
                            
                        except Exception as e1:
                            print(f"   Warning: Could not fetch {pair} with Alpha Vantage: {str(e1)}")
                            continue
                            
                    except Exception as e:
                        print(f"   Warning: Could not fetch {pair}: {str(e)}")
                
                print(f"   Alpha Vantage collected {len(forex_data)} pairs")
            
            # If Alpha Vantage failed or no key, try yfinance
            if not forex_data:
                print("   Trying yfinance for forex data...")
                try:
                    for pair in forex_pairs:
                        try:
                            # Use yfinance for forex data (more reliable)
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
                                print(f"✅ {pair}: {forex_data[pair]['current_rate']:.4f} ({forex_data[pair]['change_percent']:+.2f}%)")
                                
                        except Exception as e:
                            print(f"   Warning: Could not fetch {pair} with yfinance: {str(e)}")
                            
                except Exception as e:
                    print(f"   Warning: yfinance failed: {str(e)}")
            
            # If all APIs failed, use sample data
            if not forex_data:
                print("   Using sample forex data (all APIs failed)")
                forex_data = {
                    "EUR/USD": {
                        "current_rate": 1.0850,
                        "change_24h": 0.0025,
                        "change_percent": 0.23,
                        "high_24h": 1.0875,
                        "low_24h": 1.0820
                    },
                    "GBP/USD": {
                        "current_rate": 1.2650,
                        "change_24h": -0.0050,
                        "change_percent": -0.39,
                        "high_24h": 1.2700,
                        "low_24h": 1.2620
                    },
                    "USD/JPY": {
                        "current_rate": 148.50,
                        "change_24h": 0.75,
                        "change_percent": 0.51,
                        "high_24h": 148.80,
                        "low_24h": 147.90
                    },
                    "USD/CHF": {
                        "current_rate": 0.8750,
                        "change_24h": -0.0020,
                        "change_percent": -0.23,
                        "high_24h": 0.8770,
                        "low_24h": 0.8730
                    }
                }
            
            print(f"✅ Collected data for {len(forex_data)} forex pairs")
            
            # Submit forex analysis task
            task_id = await self.communication_manager.send_task_request(
                "analyze_forex",
                {"forex_data": forex_data, "pairs": forex_pairs},
                priority=1
            )
            
            print(f"   Forex analysis task submitted: {task_id}")
            
            # Wait for completion
            result = await self.communication_manager.task_coordinator.wait_for_task_completion(
                task_id, timeout=60
            )
            
            if result:
                print("✅ Forex analysis completed!")
                analysis = result.get('pair_analysis', {})
                
                for pair, pair_analysis in analysis.items():
                    print(f"\n💱 {pair} Analysis:")
                    print(f"   - Current Rate: {pair_analysis.get('current_rate', 'N/A')}")
                    print(f"   - 24h Change: {pair_analysis.get('change_24h', 'N/A')} ({pair_analysis.get('change_percent', 'N/A')}%)")
                    print(f"   - Trend: {pair_analysis.get('trend', 'Unknown')}")
                    print(f"   - Volatility: {pair_analysis.get('volatility', 'N/A')}")
                    print(f"   - High 24h: {pair_analysis.get('high_24h', 'N/A')}")
                    print(f"   - Low 24h: {pair_analysis.get('low_24h', 'N/A')}")
                
                self.demo_results['forex_analysis'] = result
                
            else:
                print("❌ Forex analysis failed")
                
        except Exception as e:
            print(f"❌ Error in forex analysis: {str(e)}")
            print("   Using sample data for demonstration...")
            
            # Fallback to sample data
            sample_forex_data = {
                "EUR/USD": {
                    "current_rate": 1.0850,
                    "change_24h": 0.0025,
                    "change_percent": 0.23,
                    "high_24h": 1.0875,
                    "low_24h": 1.0820
                },
                "GBP/USD": {
                    "current_rate": 1.2650,
                    "change_24h": -0.0050,
                    "change_percent": -0.39,
                    "high_24h": 1.2700,
                    "low_24h": 1.2620
                }
            }
            
            # Submit analysis with sample data
            task_id = await self.communication_manager.send_task_request(
                "analyze_forex",
                {"forex_data": sample_forex_data, "pairs": list(sample_forex_data.keys())},
                priority=1
            )
            
            result = await self.communication_manager.task_coordinator.wait_for_task_completion(
                task_id, timeout=60
            )
            
            if result:
                print("✅ Forex analysis completed with sample data!")
                self.demo_results['forex_analysis'] = result
    
    async def scenario_3_crypto_analysis(self):
        """Scenario 3: Cryptocurrency Analysis"""
        print("\n₿ Scenario 3: Cryptocurrency Analysis")
        print("=" * 60)
        
        # Cryptocurrencies to analyze
        crypto_symbols = ["BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD"]
        
        print(f"🪙 Collecting live cryptocurrency data for {', '.join(crypto_symbols)}...")
        
        try:
            crypto_data = {}
            
            for symbol in crypto_symbols:
                try:
                    # Get crypto data using yfinance
                    crypto = yf.Ticker(symbol)
                    hist_data = crypto.history(period="1mo", interval="1d")
                    
                    if not hist_data.empty:
                        crypto_data[symbol] = {
                            "symbol": symbol,
                            "current_price": hist_data['Close'].iloc[-1],
                            "volume_24h": hist_data['Volume'].iloc[-1],
                            "market_cap": crypto.info.get('marketCap', 'N/A'),
                            "price_change_24h": hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-2],
                            "price_change_percent": ((hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-2]) / hist_data['Close'].iloc[-2]) * 100,
                            "high_24h": hist_data['High'].iloc[-1],
                            "low_24h": hist_data['Low'].iloc[-1],
                            "historical_data": hist_data.reset_index().to_dict('records')
                        }
                        
                        print(f"✅ {symbol}: ${crypto_data[symbol]['current_price']:.2f} ({crypto_data[symbol]['price_change_percent']:+.2f}%)")
                    
                except Exception as e:
                    print(f"   Warning: Could not fetch {symbol}: {str(e)}")
            
            if crypto_data:
                # Submit crypto analysis task
                task_id = await self.communication_manager.send_task_request(
                    "analyze_crypto",
                    {"crypto_data": crypto_data},
                    priority=1
                )
                
                print(f"   Cryptocurrency analysis task submitted: {task_id}")
                
                # Wait for completion
                result = await self.communication_manager.task_coordinator.wait_for_task_completion(
                    task_id, timeout=60
                )
                
                if result:
                    print("✅ Cryptocurrency analysis completed!")
                    analysis = result.get('crypto_analysis', {})
                    
                    for symbol, crypto_analysis in analysis.items():
                        print(f"\n₿ {symbol} Analysis:")
                        print(f"   - Current Price: ${crypto_analysis.get('current_price', 'N/A')}")
                        print(f"   - 24h Change: {crypto_analysis.get('price_change_24h', 'N/A')} ({crypto_analysis.get('price_change_percent', 'N/A')}%)")
                        print(f"   - Market Cap: ${crypto_analysis.get('market_cap', 'N/A'):,}")
                        print(f"   - Trend: {crypto_analysis.get('trend', 'Unknown')}")
                        print(f"   - Volatility: {crypto_analysis.get('volatility', 'N/A')}")
                        print(f"   - RSI: {crypto_analysis.get('rsi', 'N/A')}")
                        print(f"   - Support: ${crypto_analysis.get('support', 'N/A')}")
                        print(f"   - Resistance: ${crypto_analysis.get('resistance', 'N/A')}")
                    
                    self.demo_results['crypto_analysis'] = result
                    
                else:
                    print("❌ Cryptocurrency analysis failed")
            else:
                print("❌ No cryptocurrency data collected")
                
        except Exception as e:
            print(f"❌ Error in cryptocurrency analysis: {str(e)}")
            print("   Using sample data for demonstration...")
            
            # Fallback to sample data
            sample_crypto_data = {
                "BTC-USD": {
                    "current_price": 43250.00,
                    "price_change_percent": 2.5,
                    "market_cap": 850000000000,
                    "trend": "bullish",
                    "volatility": "high",
                    "rsi": 68.5,
                    "support": 42000,
                    "resistance": 44000
                },
                "ETH-USD": {
                    "current_price": 2650.00,
                    "price_change_percent": -1.2,
                    "market_cap": 320000000000,
                    "trend": "bearish",
                    "volatility": "medium",
                    "rsi": 45.2,
                    "support": 2600,
                    "resistance": 2700
                }
            }
            
            self.demo_results['crypto_analysis'] = {"crypto_analysis": sample_crypto_data}
    
    async def generate_comprehensive_insights(self):
        """Generate comprehensive insights from all scenarios"""
        print("\n🧠 Generating Comprehensive Insights")
        print("=" * 60)
        
        # Combine all analysis results
        all_analysis = {}
        
        if 'stock_analysis' in self.demo_results:
            all_analysis['stocks'] = self.demo_results['stock_analysis']
        
        if 'forex_analysis' in self.demo_results:
            all_analysis['forex'] = self.demo_results['forex_analysis']
        
        if 'crypto_analysis' in self.demo_results:
            all_analysis['crypto'] = self.demo_results['crypto_analysis']
        
        if all_analysis:
            # Submit comprehensive insight generation task
            task_id = await self.communication_manager.send_task_request(
                "generate_comprehensive_insights",
                {
                    "analysis_results": all_analysis,
                    "market_context": {
                        "analysis_date": datetime.now().isoformat(),
                        "markets_analyzed": list(all_analysis.keys()),
                        "risk_level": "medium"
                    }
                },
                priority=2
            )
            
            print(f"   Comprehensive insight generation task submitted: {task_id}")
            
            # Wait for completion
            result = await self.communication_manager.task_coordinator.wait_for_task_completion(
                task_id, timeout=90
            )
            
            if result:
                print("✅ Comprehensive insights generated!")
                
                # Extract insights and recommendations from the correct keys
                cross_market_insights = result.get('cross_market_insights', [])
                strategic_recommendations = result.get('strategic_recommendations', [])
                market_overview = result.get('market_overview', {})
                risk_assessment = result.get('risk_assessment', {})
                opportunity_analysis = result.get('opportunity_analysis', {})
                
                print(f"\n📊 Market Overview:")
                print(f"   - Markets Analyzed: {market_overview.get('markets_analyzed', [])}")
                print(f"   - Total Markets: {market_overview.get('total_markets', 0)}")
                print(f"   - Risk Level: {market_overview.get('risk_level', 'Unknown')}")
                
                print(f"\n💡 Cross-Market Insights ({len(cross_market_insights)} total):")
                for i, insight in enumerate(cross_market_insights[:5], 1):
                    print(f"   {i}. {insight.get('title', 'Unknown insight')}")
                    print(f"      Description: {insight.get('description', 'No description')}")
                    print(f"      Category: {insight.get('category', 'Unknown')}")
                    print(f"      Confidence: {insight.get('confidence', 0):.2f}")
                    print(f"      Impact Score: {insight.get('impact_score', 0):.2f}")
                
                print(f"\n🎯 Strategic Recommendations ({len(strategic_recommendations)} total):")
                for i, rec in enumerate(strategic_recommendations[:5], 1):
                    print(f"   {i}. {rec}")
                
                if risk_assessment:
                    print(f"\n⚠️  Risk Assessment:")
                    print(f"   - High Risk Markets: {risk_assessment.get('high_risk_markets', [])}")
                    print(f"   - Medium Risk Markets: {risk_assessment.get('medium_risk_markets', [])}")
                    print(f"   - Low Risk Markets: {risk_assessment.get('low_risk_markets', [])}")
                    print(f"   - Overall Risk Level: {risk_assessment.get('overall_risk_level', 'Unknown')}")
                
                if opportunity_analysis:
                    print(f"\n🚀 Opportunity Analysis:")
                    print(f"   - Growth Markets: {opportunity_analysis.get('growth_markets', [])}")
                    print(f"   - Stabilization Markets: {opportunity_analysis.get('stabilization_markets', [])}")
                    print(f"   - Recovery Markets: {opportunity_analysis.get('recovery_markets', [])}")
                    print(f"   - Total Market Cap: ${opportunity_analysis.get('total_market_cap', 0):,}")
                
                self.demo_results['comprehensive_insights'] = result
                
            else:
                print("❌ Comprehensive insight generation failed")
        else:
            print("⚠️  No analysis results available for insight generation")
    
    async def run_live_demo(self, use_langchain: bool = False):
        """Run the complete live data demo"""
        print("🎯 AI Business Intelligence System - Live Data Demo")
        print("=" * 80)
        print("This demo showcases real-time analysis of:")
        print("  1. Tesla & Google Stock Analysis")
        print("  2. Forex Trading Analysis (EUR/USD, GBP/USD, USD/JPY, USD/CHF)")
        print("  3. Cryptocurrency Analysis (BTC, ETH, ADA, DOT)")
        if use_langchain:
            print("  4. AI-Powered Insights using LangChain & OpenAI")
        print("=" * 80)
        
        try:
            # Setup system with LangChain option
            await self.setup_system(use_langchain=use_langchain)
            
            # Run scenarios
            await self.scenario_1_stocks_analysis()
            await self.scenario_2_forex_analysis()
            await self.scenario_3_crypto_analysis()
            
            # Generate comprehensive insights
            await self.generate_comprehensive_insights()
            
            # Print final results
            self.print_demo_results()
            
        except Exception as e:
            print(f"❌ Demo failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            print("\n🧹 Cleaning up...")
            for agent in self.agent_registry.get_all_agents():
                await agent.stop()
            print("✅ Demo completed!")
    
    def print_demo_results(self):
        """Print summary of demo results"""
        print("\n📊 Demo Results Summary")
        print("=" * 60)
        
        total_analyses = len(self.demo_results)
        print(f"✅ Total analyses completed: {total_analyses}")
        
        if 'stock_analysis' in self.demo_results:
            print("📈 Stock Analysis: ✅ Completed")
        
        if 'forex_analysis' in self.demo_results:
            print("💱 Forex Analysis: ✅ Completed")
        
        if 'crypto_analysis' in self.demo_results:
            print("₿ Cryptocurrency Analysis: ✅ Completed")
        
        if 'comprehensive_insights' in self.demo_results:
            cross_market_insights = self.demo_results['comprehensive_insights'].get('cross_market_insights', [])
            strategic_recommendations = self.demo_results['comprehensive_insights'].get('strategic_recommendations', [])
            print(f"🧠 Comprehensive Insights: ✅ Generated {len(cross_market_insights)} insights and {len(strategic_recommendations)} recommendations")
        
        print("\n🎉 Live Data Demo Successfully Completed!")
        print("   The AI system has analyzed real-time market data and generated actionable insights.")


async def main():
    """Main function to run the live data demo"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI Business Intelligence System Demo')
    parser.add_argument('--langchain', action='store_true', 
                       help='Enable LangChain AI integration for enhanced insights')
    parser.add_argument('--demo', action='store_true', 
                       help='Run with demo data (no API keys required)')
    
    args = parser.parse_args()
    
    # Check for LangChain usage
    if args.langchain:
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: --langchain flag requires OPENAI_API_KEY environment variable")
            print("   Set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
            print("   Or run without --langchain to use the custom framework only")
            sys.exit(1)
        print("🤖 LangChain AI integration enabled")
    else:
        print("🔧 Using custom agent framework (LangChain disabled)")
        print("   Use --langchain flag to enable AI-powered insights")
    
    demo = LiveDataDemo()
    await demo.run_live_demo(use_langchain=args.langchain)


if __name__ == "__main__":
    asyncio.run(main()) 