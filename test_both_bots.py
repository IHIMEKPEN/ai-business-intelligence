#!/usr/bin/env python3
"""
Test script to compare Crypto and Stock Trading Bots

This script demonstrates both trading bots and compares their performance
and signal generation strategies.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from trading_bot.crypto_trading_bot import CryptoTradingBot, RiskLevel
from trading_bot.stock_trading_bot import StockTradingBot

async def test_crypto_bot():
    """Test the crypto trading bot"""
    print("🪙 Testing Crypto Trading Bot")
    print("=" * 40)
    
    try:
        async with CryptoTradingBot(
            symbols=['BTC-USD', 'ETH-USD', 'ADA-USD'],
            risk_level=RiskLevel.MODERATE,
            max_positions=3,
            position_size=0.1,
            analysis_interval=10,
            portfolio_value=10000.0
        ) as bot:
            
            # Get market analysis
            analysis = await bot._get_market_analysis()
            
            if analysis:
                print("✅ Crypto market analysis received")
                
                # Generate signals
                signals = await bot._generate_signals(analysis)
                
                print(f"📈 Generated {len(signals)} crypto signals:")
                for signal in signals:
                    print(f"  • {signal.symbol}: {signal.signal_type.value} "
                          f"(confidence: {signal.confidence:.1f}, "
                          f"price: ${signal.price:.2f})")
                    print(f"    Reasoning: {signal.reasoning}")
            else:
                print("❌ Failed to get crypto market analysis")
                
    except Exception as e:
        print(f"❌ Crypto bot test failed: {str(e)}")

async def test_stock_bot():
    """Test the stock trading bot"""
    print("\n📈 Testing Stock Trading Bot")
    print("=" * 40)
    
    try:
        async with StockTradingBot(
            symbols=['AAPL', 'MSFT', 'GOOGL'],
            risk_level=RiskLevel.MODERATE,
            max_positions=3,
            position_size=0.1,
            analysis_interval=10,
            portfolio_value=10000.0,
            trading_hours_only=False
        ) as bot:
            
            # Get market analysis
            analysis = await bot._get_market_analysis()
            
            if analysis:
                print("✅ Stock market analysis received")
                
                # Generate signals
                signals = await bot._generate_signals(analysis)
                
                print(f"📈 Generated {len(signals)} stock signals:")
                for signal in signals:
                    print(f"  • {signal.symbol}: {signal.signal_type.value} "
                          f"(confidence: {signal.confidence:.1f}, "
                          f"price: ${signal.price:.2f})")
                    print(f"    Reasoning: {signal.reasoning}")
            else:
                print("❌ Failed to get stock market analysis")
                
    except Exception as e:
        print(f"❌ Stock bot test failed: {str(e)}")

async def compare_strategies():
    """Compare different risk strategies for both bots"""
    print("\n🎯 Comparing Risk Strategies")
    print("=" * 40)
    
    risk_levels = [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]
    
    for risk_level in risk_levels:
        print(f"\n📊 {risk_level.value.upper()} Strategy:")
        print("-" * 25)
        
        # Test crypto bot
        try:
            async with CryptoTradingBot(
                symbols=['BTC-USD'],
                risk_level=risk_level,
                max_positions=1,
                position_size=0.1,
                analysis_interval=10,
                portfolio_value=10000.0
            ) as crypto_bot:
                
                analysis = await crypto_bot._get_market_analysis()
                if analysis:
                    signals = await crypto_bot._generate_signals(analysis)
                    print(f"  Crypto: {len(signals)} signals generated")
                else:
                    print("  Crypto: No analysis available")
                    
        except Exception as e:
            print(f"  Crypto: Error - {str(e)}")
        
        # Test stock bot
        try:
            async with StockTradingBot(
                symbols=['AAPL'],
                risk_level=risk_level,
                max_positions=1,
                position_size=0.1,
                analysis_interval=10,
                portfolio_value=10000.0,
                trading_hours_only=False
            ) as stock_bot:
                
                analysis = await stock_bot._get_market_analysis()
                if analysis:
                    signals = await stock_bot._generate_signals(analysis)
                    print(f"  Stock:  {len(signals)} signals generated")
                else:
                    print("  Stock:  No analysis available")
                    
        except Exception as e:
            print(f"  Stock:  Error - {str(e)}")

async def main():
    """Main test function"""
    print("🤖 AI Trading Bots Comparison Test")
    print("=" * 60)
    print("This script tests both crypto and stock trading bots")
    print()
    
    # Test crypto bot
    await test_crypto_bot()
    
    # Test stock bot
    await test_stock_bot()
    
    # Compare strategies
    await compare_strategies()
    
    print("\n" + "=" * 60)
    print("🎉 Bot comparison test completed!")
    print("\n📚 Key Differences:")
    print("   • Crypto Bot: Higher volatility, smaller price movements")
    print("   • Stock Bot: Lower volatility, market hours awareness")
    print("   • Both use AI agents for market analysis")
    print("   • Different risk thresholds for each market type")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}") 