#!/usr/bin/env python3
"""
Test script to verify trading signal generation logic
"""

import asyncio
import aiohttp
from trading_bot.crypto_trading_bot import CryptoTradingBot, RiskLevel

async def test_signal_generation():
    """Test signal generation with current market data"""
    print("🧪 Testing Trading Signal Generation")
    print("=" * 50)
    
    # Create trading bot with different risk levels
    risk_levels = [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]
    
    for risk_level in risk_levels:
        print(f"\n📊 Testing {risk_level.value.upper()} strategy:")
        print("-" * 30)
        
        async with CryptoTradingBot(
            symbols=['BTC-USD', 'ETH-USD', 'ADA-USD'],
            risk_level=risk_level,
            max_positions=3,
            position_size=0.1,
            analysis_interval=10,
            portfolio_value=10000.0
        ) as bot:
            
            # Get market analysis
            analysis = await bot._get_market_analysis()
            
            if analysis:
                print(f"✅ Market analysis received")
                
                # Generate signals
                signals = await bot._generate_signals(analysis)
                
                print(f"📈 Generated {len(signals)} signals:")
                for signal in signals:
                    print(f"  • {signal.symbol}: {signal.signal_type.value} "
                          f"(confidence: {signal.confidence:.1f}, "
                          f"price: ${signal.price:.2f})")
                    print(f"    Reasoning: {signal.reasoning}")
            else:
                print("❌ Failed to get market analysis")
    
    print("\n" + "=" * 50)
    print("🎯 Signal Generation Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_signal_generation()) 