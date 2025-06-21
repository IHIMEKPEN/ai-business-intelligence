#!/usr/bin/env python3
"""
Test Real-Time Use Cases for AI Business Intelligence System

This script demonstrates both the AI Trading Assistant Chatbot and
Crypto Trading Bot integration with the AI Business Intelligence system.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from chatbot.trading_assistant import TradingAssistant
from trading_bot.crypto_trading_bot import CryptoTradingBot, RiskLevel

async def test_trading_assistant():
    """Test the AI Trading Assistant Chatbot"""
    print("🤖 Testing AI Trading Assistant Chatbot")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found. Skipping chatbot test.")
        print("   Set OPENAI_API_KEY environment variable to test the chatbot.")
        return
    
    try:
        async with TradingAssistant() as assistant:
            # Test messages
            test_messages = [
                "What's the current market outlook for Tesla stock?",
                "Should I invest in Bitcoin right now?",
                "Analyze my portfolio: AAPL, MSFT, GOOGL",
                "What are the best crypto investments for 2024?"
            ]
            
            for i, message in enumerate(test_messages, 1):
                print(f"\n📝 Test {i}: {message}")
                print("-" * 40)
                
                try:
                    response = await assistant.process_message(message)
                    print(f"🤖 Assistant: {response}")
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                
                # Small delay between messages
                await asyncio.sleep(2)
        
        print("\n✅ Trading Assistant test completed!")
        
    except Exception as e:
        print(f"❌ Trading Assistant test failed: {str(e)}")

async def test_crypto_trading_bot():
    """Test the Crypto Trading Bot"""
    print("\n🤖 Testing Crypto Trading Bot")
    print("=" * 50)
    
    try:
        # Create trading bot with demo settings
        async with CryptoTradingBot(
            symbols=['BTC-USD', 'ETH-USD', 'ADA-USD'],
            risk_level=RiskLevel.CONSERVATIVE,
            max_positions=3,
            position_size=0.1,
            analysis_interval=10,  # 10 seconds for demo
            portfolio_value=10000.0
        ) as bot:
            
            print("🚀 Starting trading bot demo...")
            print("   This will run for 30 seconds to demonstrate functionality.")
            print("   Press Ctrl+C to stop early.")
            
            # Run for 30 seconds
            start_time = asyncio.get_event_loop().time()
            
            try:
                while (asyncio.get_event_loop().time() - start_time) < 30:
                    # Simulate one trading cycle
                    await bot._trading_cycle()
                    
                    # Show current status
                    performance = bot.get_performance_summary()
                    positions = bot.get_positions()
                    
                    print(f"\n📊 Status Update:")
                    print(f"   Total Trades: {performance['total_trades']}")
                    print(f"   Win Rate: {performance['win_rate']:.1f}%")
                    print(f"   Total P&L: ${performance['total_pnl']:.2f}")
                    print(f"   Open Positions: {len(positions)}")
                    
                    if positions:
                        print("   Current Positions:")
                        for symbol, pos in positions.items():
                            print(f"     {symbol}: ${pos.current_price:.2f} (P&L: {pos.pnl_percent:.2f}%)")
                    
                    await asyncio.sleep(10)
                    
            except KeyboardInterrupt:
                print("\n🛑 Demo stopped by user")
            
            # Show final performance
            final_performance = bot.get_performance_summary()
            print(f"\n📈 Final Performance:")
            print(f"   Total Trades: {final_performance['total_trades']}")
            print(f"   Win Rate: {final_performance['win_rate']:.1f}%")
            print(f"   Total P&L: ${final_performance['total_pnl']:.2f} ({final_performance['total_pnl_percent']:.2f}%)")
            print(f"   Max Drawdown: {final_performance['max_drawdown']:.1f}%")
            print(f"   Final Portfolio Value: ${final_performance['portfolio_value']:.2f}")
        
        print("\n✅ Crypto Trading Bot test completed!")
        
    except Exception as e:
        print(f"❌ Crypto Trading Bot test failed: {str(e)}")

async def test_api_connectivity():
    """Test API connectivity"""
    print("🔌 Testing API Connectivity")
    print("=" * 50)
    
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API Health: {data.get('status', 'Unknown')}")
                else:
                    print(f"❌ API Health Check Failed: {response.status}")
                    return False
            
            # Test status endpoint
            async with session.get("http://localhost:8000/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API Status: {data.get('status', 'Unknown')}")
                    print(f"   Active Agents: {data.get('active_agents', 0)}")
                    print(f"   Total Tasks: {data.get('total_tasks', 0)}")
                else:
                    print(f"❌ API Status Check Failed: {response.status}")
                    return False
        
        print("✅ API connectivity test passed!")
        return True
        
    except Exception as e:
        print(f"❌ API connectivity test failed: {str(e)}")
        print("   Make sure the AI Business Intelligence API is running:")
        print("   python demo.py --api-only")
        return False

async def main():
    """Main test function"""
    print("🚀 AI Business Intelligence - Real-Time Use Cases Test")
    print("=" * 60)
    print("This script tests both the AI Trading Assistant and Crypto Trading Bot")
    print()
    
    # Test API connectivity first
    api_ok = await test_api_connectivity()
    
    if not api_ok:
        print("\n❌ Cannot proceed without API connectivity.")
        print("Please start the AI Business Intelligence API first:")
        print("   python demo.py --api-only")
        return
    
    print("\n" + "="*60)
    
    # Test trading assistant
    await test_trading_assistant()
    
    print("\n" + "="*60)
    
    # Test crypto trading bot
    await test_crypto_trading_bot()
    
    print("\n" + "="*60)
    print("🎉 All tests completed!")
    print("\n📚 For more information, see:")
    print("   - REALTIME_USE_CASES.md - Detailed use case documentation")
    print("   - chatbot/trading_assistant.py - Trading assistant implementation")
    print("   - trading_bot/crypto_trading_bot.py - Trading bot implementation")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}") 