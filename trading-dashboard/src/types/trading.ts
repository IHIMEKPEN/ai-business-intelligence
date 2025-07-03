export enum SignalType {
  BUY = "BUY",
  SELL = "SELL",
  HOLD = "HOLD"
}

export enum RiskLevel {
  CONSERVATIVE = "conservative",
  MODERATE = "moderate",
  AGGRESSIVE = "aggressive"
}

export interface TradingSignal {
  symbol: string;
  signal_type: SignalType;
  confidence: number;
  price: number;
  timestamp: string;
  reasoning: string;
  risk_level: RiskLevel;
  stop_loss?: number;
  take_profit?: number;
}

export interface Position {
  symbol: string;
  entry_price: number;
  quantity: number;
  entry_time: string;
  current_price: number;
  pnl: number;
  pnl_percent: number;
  stop_loss?: number;
  take_profit?: number;
}

export interface Trade {
  timestamp: string;
  symbol: string;
  action: string;
  price: number;
  quantity: number;
  value: number;
  confidence?: number;
  reasoning?: string;
  pnl?: number;
  pnl_percent?: number;
  reason?: string;
}

export interface PerformanceSummary {
  total_trades: number;
  winning_trades: number;
  win_rate: number;
  total_pnl: number;
  total_pnl_percent: number;
  portfolio_value: number;
  max_drawdown: number;
  open_positions: number;
  risk_level: string;
  symbols_traded: string[];
}

export interface MarketAnalysis {
  symbol: string;
  current_price: number;
  price_change_percent: number;
  trend: string;
  high_24h: number;
  low_24h: number;
  volume: number;
  volatility: number;
  ai_confidence: number;
  ai_recommendation: string;
}

export interface PortfolioData {
  total_value: number;
  available_cash: number;
  total_pnl: number;
  daily_pnl: number;
  positions: Position[];
  performance: PerformanceSummary;
} 