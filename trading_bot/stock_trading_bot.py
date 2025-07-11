#!/usr/bin/env python3
"""
Stock Trading Bot with AI Business Intelligence Integration

A sophisticated trading bot that uses AI agents for market analysis
and automated trading decisions in stock markets.
"""

import asyncio
import json
import aiohttp
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import structlog
from decimal import Decimal, ROUND_DOWN

logger = structlog.get_logger(__name__)

class SignalType(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class RiskLevel(Enum):
    """Risk management levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class TradingSignal:
    """Trading signal data structure"""
    symbol: str
    signal_type: SignalType
    confidence: float
    price: float
    timestamp: datetime
    reasoning: str
    risk_level: RiskLevel
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class Position:
    """Trading position data structure"""
    symbol: str
    entry_price: float
    quantity: float
    entry_time: datetime
    current_price: float
    pnl: float
    pnl_percent: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class StockTradingBot:
    """AI-Powered Stock Trading Bot"""
    
    def __init__(self, 
                 api_base_url: str = "http://localhost:8000",
                 symbols: List[str] = None,
                 risk_level: RiskLevel = RiskLevel.MODERATE,
                 max_positions: int = 5,
                 position_size: float = 0.1,  # 10% of portfolio per position
                 stop_loss_percent: float = 0.05,  # 5% stop loss
                 take_profit_percent: float = 0.15,  # 15% take profit
                 analysis_interval: int = 300,  # 5 minutes
                 portfolio_value: float = 10000.0,
                 trading_hours_only: bool = True):
        
        self.api_base_url = api_base_url
        self.session = None
        self.symbols = symbols or ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        self.risk_level = risk_level
        self.max_positions = max_positions
        self.position_size = position_size
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.analysis_interval = analysis_interval
        self.portfolio_value = portfolio_value
        self.trading_hours_only = trading_hours_only
        
        # Trading state
        self.positions: Dict[str, Position] = {}
        self.signals: List[TradingSignal] = []
        self.trade_history: List[Dict] = []
        self.is_running = False
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        
        # Market hours (EST)
        self.market_open = 9  # 9 AM EST
        self.market_close = 16  # 4 PM EST
        
        logger.info(
            "Stock Trading Bot initialized",
            symbols=self.symbols,
            risk_level=risk_level.value,
            max_positions=max_positions,
            portfolio_value=portfolio_value,
            trading_hours_only=trading_hours_only
        )
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _is_market_open(self) -> bool:
        """Check if stock market is open (simplified)"""
        if not self.trading_hours_only:
            return True
        
        # Get current time in EST (simplified)
        now = datetime.utcnow() - timedelta(hours=5)  # UTC to EST
        current_hour = now.hour
        
        # Check if it's a weekday and during market hours
        is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4
        is_market_hours = self.market_open <= current_hour < self.market_close
        
        return is_weekday and is_market_hours
    
    async def start(self):
        """Start the trading bot"""
        self.is_running = True
        logger.info("Stock Trading Bot started")
        
        try:
            while self.is_running:
                # Check if market is open
                if self._is_market_open():
                    await self._trading_cycle()
                else:
                    logger.info("Market closed - waiting for next cycle")
                
                await asyncio.sleep(self.analysis_interval)
                
        except Exception as e:
            logger.error("Error in trading bot", error=str(e))
            self.is_running = False
    
    async def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        logger.info("Stock Trading Bot stopped")
    
    async def _trading_cycle(self):
        """Main trading cycle"""
        try:
            # 1. Get market analysis from AI agents
            analysis = await self._get_market_analysis()
            
            # 2. Generate trading signals
            signals = await self._generate_signals(analysis)
            
            # 3. Update existing positions
            await self._update_positions()
            
            # 4. Execute new trades based on signals
            await self._execute_trades(signals)
            
            # 5. Risk management checks
            await self._risk_management()
            
            # 6. Log performance
            self._log_performance()
            
        except Exception as e:
            logger.error("Error in trading cycle", error=str(e))
    
    async def _get_market_analysis(self) -> Dict:
        """Get market analysis from AI agents"""
        try:
            payload = {
                "symbols": self.symbols,
                "period": "1mo",
                "interval": "1d"
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
                                    logger.info("Market analysis received", task_id=task_id)
                                    return result
                                else:
                                    logger.error("Analysis error", error=result['error'])
                                    return {}
                            else:
                                logger.warning("Analysis still in progress")
                                return {}
                else:
                    logger.error("API error", status=response.status, text=await response.text())
                    return {}
                    
        except Exception as e:
            logger.error("Error getting market analysis", error=str(e))
            return {}
    
    async def _generate_signals(self, analysis: Dict) -> List[TradingSignal]:
        """Generate trading signals based on AI analysis"""
        signals = []
        
        if not analysis:
            logger.warning("No analysis data provided for signal generation")
            return signals
        
        stock_analysis = analysis.get('stock_analysis', {})
        logger.info(f"Processing {len(stock_analysis)} stock symbols for signals")
        
        for symbol in self.symbols:
            try:
                symbol_key = symbol.lower()
                symbol_data = stock_analysis.get(symbol_key, {})
                
                if not symbol_data:
                    logger.warning(f"No data available for {symbol}")
                    continue
                
                current_price = symbol_data.get('current_price', 0)
                price_change_percent = symbol_data.get('price_change_percent', 0)
                trend = symbol_data.get('trend', 'neutral')
                volume = symbol_data.get('volume', 0)
                market_cap = symbol_data.get('market_cap', 0)
                
                # Calculate volatility from historical data
                historical_data = symbol_data.get('historical_data', [])
                volatility = self._calculate_volatility(historical_data)
                
                logger.info(
                    f"Analyzing {symbol}: price=${current_price:.2f}, "
                    f"change={price_change_percent:.2f}%, trend={trend}, "
                    f"volatility={volatility:.4f}, risk_level={self.risk_level.value}"
                )
                
                # Generate signal based on analysis and risk level
                signal = self._create_signal(
                    symbol=symbol,
                    current_price=current_price,
                    price_change=price_change_percent,
                    trend=trend,
                    volatility=volatility,
                    volume=volume,
                    market_cap=market_cap
                )
                
                if signal:
                    signals.append(signal)
                    logger.info(
                        "Signal generated",
                        symbol=symbol,
                        signal=signal.signal_type.value,
                        confidence=signal.confidence,
                        price=current_price,
                        reasoning=signal.reasoning
                    )
                else:
                    logger.info(f"No signal generated for {symbol} - conditions not met")
                
            except Exception as e:
                logger.error(f"Error generating signal for {symbol}", error=str(e))
        
        logger.info(f"Generated {len(signals)} trading signals")
        return signals
    
    def _calculate_volatility(self, historical_data: List[Dict]) -> float:
        """Calculate volatility from historical price data"""
        if len(historical_data) < 2:
            return 0.0
        
        try:
            prices = [float(day.get('Close', 0)) for day in historical_data if day.get('Close')]
            if len(prices) < 2:
                return 0.0
            
            # Calculate daily returns
            returns = []
            for i in range(1, len(prices)):
                if prices[i-1] > 0:
                    daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                    returns.append(daily_return)
            
            if not returns:
                return 0.0
            
            # Calculate standard deviation of returns
            import statistics
            return statistics.stdev(returns) if len(returns) > 1 else 0.0
            
        except Exception as e:
            logger.error("Error calculating volatility", error=str(e))
            return 0.0
    
    def _create_signal(self, 
                      symbol: str, 
                      current_price: float, 
                      price_change: float, 
                      trend: str, 
                      volatility: float,
                      volume: float,
                      market_cap: float) -> Optional[TradingSignal]:
        """Create trading signal based on analysis"""
        
        # Skip if already have a position
        if symbol in self.positions:
            logger.debug(f"Skipping {symbol} - already have position")
            return None
        
        # Skip if at max positions
        if len(self.positions) >= self.max_positions:
            logger.debug(f"Skipping {symbol} - at max positions ({self.max_positions})")
            return None
        
        signal_type = SignalType.HOLD
        confidence = 0.5
        reasoning = ""
        
        # Conservative strategy (for stocks)
        if self.risk_level == RiskLevel.CONSERVATIVE:
            if trend == 'bullish' and price_change > 2 and volatility < 0.03:
                signal_type = SignalType.BUY
                confidence = 0.7
                reasoning = "Strong bullish trend with low volatility"
            elif trend == 'bearish' and price_change < -2:
                signal_type = SignalType.SELL
                confidence = 0.6
                reasoning = "Bearish trend with significant decline"
            else:
                logger.debug(f"Conservative: {symbol} - trend={trend}, change={price_change:.2f}%, volatility={volatility:.4f} - conditions not met")
        
        # Moderate strategy (for stocks)
        elif self.risk_level == RiskLevel.MODERATE:
            if trend == 'bullish' and price_change > 1:
                signal_type = SignalType.BUY
                confidence = 0.6
                reasoning = "Bullish trend with positive momentum"
            elif trend == 'bearish' and price_change < -1:
                signal_type = SignalType.SELL
                confidence = 0.5
                reasoning = "Bearish trend"
            else:
                logger.debug(f"Moderate: {symbol} - trend={trend}, change={price_change:.2f}% - conditions not met")
        
        # Aggressive strategy (for stocks)
        elif self.risk_level == RiskLevel.AGGRESSIVE:
            if trend == 'bullish' and price_change > 0.5:
                signal_type = SignalType.BUY
                confidence = 0.5
                reasoning = "Bullish momentum"
            elif trend == 'bearish' and price_change < -0.5:
                signal_type = SignalType.SELL
                confidence = 0.4
                reasoning = "Bearish momentum"
            else:
                logger.debug(f"Aggressive: {symbol} - trend={trend}, change={price_change:.2f}% - conditions not met")
        
        if signal_type != SignalType.HOLD:
            # Calculate stop loss and take profit
            if signal_type == SignalType.BUY:
                stop_loss = current_price * (1 - self.stop_loss_percent)
                take_profit = current_price * (1 + self.take_profit_percent)
            else:  # SELL
                stop_loss = current_price * (1 + self.stop_loss_percent)
                take_profit = current_price * (1 - self.take_profit_percent)
            
            return TradingSignal(
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                price=current_price,
                timestamp=datetime.utcnow(),
                reasoning=reasoning,
                risk_level=self.risk_level,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
        
        return None
    
    async def _update_positions(self):
        """Update existing positions with current prices"""
        for symbol, position in list(self.positions.items()):
            try:
                # Get current price (in real implementation, this would be from exchange API)
                current_price = await self._get_current_price(symbol)
                
                if current_price:
                    position.current_price = current_price
                    position.pnl = (current_price - position.entry_price) * position.quantity
                    position.pnl_percent = ((current_price - position.entry_price) / position.entry_price) * 100
                    
                    # Check stop loss and take profit
                    if position.stop_loss and current_price <= position.stop_loss:
                        await self._close_position(symbol, "Stop loss triggered")
                    elif position.take_profit and current_price >= position.take_profit:
                        await self._close_position(symbol, "Take profit triggered")
                
            except Exception as e:
                logger.error(f"Error updating position for {symbol}", error=str(e))
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol (simulated)"""
        # In real implementation, this would call exchange API
        # For demo purposes, we'll simulate price movement
        import random
        
        # Simulate price movement based on trend
        base_price = 150.0  # Simulated base price for stocks
        movement = random.uniform(-0.01, 0.01)  # ±1% movement (stocks are less volatile)
        return base_price * (1 + movement)
    
    async def _execute_trades(self, signals: List[TradingSignal]):
        """Execute trades based on signals"""
        for signal in signals:
            try:
                if signal.signal_type == SignalType.BUY:
                    await self._open_position(signal)
                elif signal.signal_type == SignalType.SELL:
                    # For stocks, we can implement short selling
                    await self._open_short_position(signal)
                
            except Exception as e:
                logger.error(f"Error executing trade for {signal.symbol}", error=str(e))
    
    async def _open_position(self, signal: TradingSignal):
        """Open a new long position"""
        try:
            # Calculate position size
            position_value = self.portfolio_value * self.position_size
            quantity = position_value / signal.price
            
            # Create position
            position = Position(
                symbol=signal.symbol,
                entry_price=signal.price,
                quantity=quantity,
                entry_time=signal.timestamp,
                current_price=signal.price,
                pnl=0.0,
                pnl_percent=0.0,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit
            )
            
            self.positions[signal.symbol] = position
            
            # Log trade
            trade = {
                "timestamp": signal.timestamp,
                "symbol": signal.symbol,
                "action": "BUY",
                "price": signal.price,
                "quantity": quantity,
                "value": position_value,
                "confidence": signal.confidence,
                "reasoning": signal.reasoning
            }
            
            self.trade_history.append(trade)
            self.total_trades += 1
            
            logger.info(
                "Long position opened",
                symbol=signal.symbol,
                price=signal.price,
                quantity=quantity,
                value=position_value,
                confidence=signal.confidence
            )
            
        except Exception as e:
            logger.error(f"Error opening position for {signal.symbol}", error=str(e))
    
    async def _open_short_position(self, signal: TradingSignal):
        """Open a new short position (for advanced strategies)"""
        try:
            # Calculate position size
            position_value = self.portfolio_value * self.position_size
            quantity = position_value / signal.price
            
            # Create short position (negative quantity indicates short)
            position = Position(
                symbol=signal.symbol,
                entry_price=signal.price,
                quantity=-quantity,  # Negative for short
                entry_time=signal.timestamp,
                current_price=signal.price,
                pnl=0.0,
                pnl_percent=0.0,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit
            )
            
            self.positions[signal.symbol] = position
            
            # Log trade
            trade = {
                "timestamp": signal.timestamp,
                "symbol": signal.symbol,
                "action": "SELL_SHORT",
                "price": signal.price,
                "quantity": quantity,
                "value": position_value,
                "confidence": signal.confidence,
                "reasoning": signal.reasoning
            }
            
            self.trade_history.append(trade)
            self.total_trades += 1
            
            logger.info(
                "Short position opened",
                symbol=signal.symbol,
                price=signal.price,
                quantity=quantity,
                value=position_value,
                confidence=signal.confidence
            )
            
        except Exception as e:
            logger.error(f"Error opening short position for {signal.symbol}", error=str(e))
    
    async def _close_position(self, symbol: str, reason: str):
        """Close a trading position"""
        try:
            position = self.positions.get(symbol)
            if not position:
                return
            
            # Calculate final P&L
            if position.quantity > 0:  # Long position
                final_pnl = (position.current_price - position.entry_price) * position.quantity
            else:  # Short position
                final_pnl = (position.entry_price - position.current_price) * abs(position.quantity)
            
            final_pnl_percent = (final_pnl / (position.entry_price * abs(position.quantity))) * 100
            
            # Update portfolio
            self.total_pnl += final_pnl
            if final_pnl > 0:
                self.winning_trades += 1
            
            # Log trade
            trade = {
                "timestamp": datetime.utcnow(),
                "symbol": symbol,
                "action": "CLOSE",
                "price": position.current_price,
                "quantity": abs(position.quantity),
                "value": position.current_price * abs(position.quantity),
                "pnl": final_pnl,
                "pnl_percent": final_pnl_percent,
                "reason": reason
            }
            
            self.trade_history.append(trade)
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(
                "Position closed",
                symbol=symbol,
                price=position.current_price,
                pnl=final_pnl,
                pnl_percent=final_pnl_percent,
                reason=reason
            )
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}", error=str(e))
    
    async def _risk_management(self):
        """Perform risk management checks"""
        try:
            # Check portfolio drawdown
            total_value = self.portfolio_value + self.total_pnl
            drawdown = (self.portfolio_value - total_value) / self.portfolio_value
            
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown
            
            # Emergency stop if drawdown exceeds threshold
            if drawdown > 0.15:  # 15% drawdown (more conservative for stocks)
                logger.warning("Emergency stop triggered - high drawdown", drawdown=drawdown)
                await self._emergency_stop()
            
            # Check position concentration
            for symbol, position in self.positions.items():
                position_value = position.current_price * abs(position.quantity)
                concentration = position_value / total_value
                
                if concentration > 0.25:  # 25% concentration limit (more conservative for stocks)
                    logger.warning("High position concentration", symbol=symbol, concentration=concentration)
                    await self._close_position(symbol, "Concentration limit exceeded")
            
        except Exception as e:
            logger.error("Error in risk management", error=str(e))
    
    async def _emergency_stop(self):
        """Emergency stop - close all positions"""
        logger.warning("Emergency stop - closing all positions")
        
        for symbol in list(self.positions.keys()):
            await self._close_position(symbol, "Emergency stop")
    
    def _log_performance(self):
        """Log trading performance"""
        total_value = self.portfolio_value + self.total_pnl
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        logger.info(
            "Performance update",
            total_trades=self.total_trades,
            winning_trades=self.winning_trades,
            win_rate=f"{win_rate:.1f}%",
            total_pnl=self.total_pnl,
            portfolio_value=total_value,
            max_drawdown=f"{self.max_drawdown*100:.1f}%",
            open_positions=len(self.positions)
        )
    
    def get_performance_summary(self) -> Dict:
        """Get trading performance summary"""
        total_value = self.portfolio_value + self.total_pnl
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "win_rate": win_rate,
            "total_pnl": self.total_pnl,
            "total_pnl_percent": (self.total_pnl / self.portfolio_value) * 100,
            "portfolio_value": total_value,
            "max_drawdown": self.max_drawdown * 100,
            "open_positions": len(self.positions),
            "risk_level": self.risk_level.value,
            "symbols_traded": self.symbols
        }
    
    def get_positions(self) -> Dict[str, Position]:
        """Get current positions"""
        return self.positions.copy()
    
    def get_trade_history(self) -> List[Dict]:
        """Get trade history"""
        return self.trade_history.copy()


# Demo function
async def demo_stock_trading_bot():
    """Demo the stock trading bot"""
    print("🤖 AI-Powered Stock Trading Bot Demo")
    print("=" * 50)
    print("This bot uses AI agents for market analysis and automated trading")
    print("Press Ctrl+C to stop")
    print()
    
    # Create trading bot with moderate settings
    async with StockTradingBot(
        symbols=['AAPL', 'MSFT', 'GOOGL'],
        risk_level=RiskLevel.MODERATE,
        max_positions=3,
        position_size=0.1,
        analysis_interval=30,  # 30 seconds for demo
        portfolio_value=10000.0,
        trading_hours_only=False  # Allow trading outside market hours for demo
    ) as bot:
        
        try:
            # Start the bot
            await bot.start()
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping stock trading bot...")
            await bot.stop()
            
            # Show performance summary
            performance = bot.get_performance_summary()
            print("\n📊 Performance Summary:")
            print(f"Total Trades: {performance['total_trades']}")
            print(f"Win Rate: {performance['win_rate']:.1f}%")
            print(f"Total P&L: ${performance['total_pnl']:.2f} ({performance['total_pnl_percent']:.2f}%)")
            print(f"Max Drawdown: {performance['max_drawdown']:.1f}%")
            print(f"Final Portfolio Value: ${performance['portfolio_value']:.2f}")


if __name__ == "__main__":
    asyncio.run(demo_stock_trading_bot()) 