import React from 'react';
import { History } from 'lucide-react';

const TradeHistory: React.FC = () => {
  const trades = [
    {
      timestamp: '2024-01-15T16:30:00Z',
      symbol: 'BTC-USD',
      action: 'SELL',
      price: 45480,
      quantity: 0.1,
      value: 4548,
      pnl: 28.0,
      pnl_percent: 0.62,
      reason: 'Take profit triggered'
    },
    {
      timestamp: '2024-01-15T10:30:00Z',
      symbol: 'BTC-USD',
      action: 'BUY',
      price: 45200,
      quantity: 0.1,
      value: 4520,
      confidence: 85,
      reasoning: 'Strong bullish trend with low volatility'
    },
    {
      timestamp: '2024-01-15T09:15:00Z',
      symbol: 'ETH-USD',
      action: 'BUY',
      price: 3150,
      quantity: 1.5,
      value: 4725,
      confidence: 78,
      reasoning: 'Positive volume increase with breakout pattern'
    }
  ];

  return (
    <div className="trading-card">
      <div className="flex items-center mb-4">
        <History className="h-6 w-6 text-trading-blue mr-2" />
        <h3 className="text-lg font-semibold">Trade History</h3>
      </div>
      
      <div className="space-y-3">
        {trades.map((trade, index) => (
          <div key={index} className="bg-trading-darker rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                <h4 className="text-lg font-semibold text-white">{trade.symbol}</h4>
                <span className={`ml-2 px-2 py-1 text-xs rounded ${
                  trade.action === 'BUY' ? 'bg-trading-green text-white' : 'bg-trading-red text-white'
                }`}>
                  {trade.action}
                </span>
              </div>
              <div className="text-right">
                <div className="text-white font-medium">${trade.price.toLocaleString()}</div>
                <div className="text-sm text-gray-400">
                  {new Date(trade.timestamp).toLocaleString()}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-3">
              <div>
                <p className="text-sm text-gray-400">Quantity</p>
                <p className="text-white font-medium">{trade.quantity}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Value</p>
                <p className="text-white font-medium">${trade.value.toLocaleString()}</p>
              </div>
              {trade.pnl !== undefined && (
                <>
                  <div>
                    <p className="text-sm text-gray-400">P&L</p>
                    <p className={`font-medium ${trade.pnl >= 0 ? 'profit' : 'loss'}`}>
                      {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">P&L %</p>
                    <p className={`font-medium ${trade.pnl_percent >= 0 ? 'profit' : 'loss'}`}>
                      {trade.pnl_percent >= 0 ? '+' : ''}{trade.pnl_percent.toFixed(2)}%
                    </p>
                  </div>
                </>
              )}
            </div>

            {trade.confidence && (
              <div className="mb-3">
                <p className="text-sm text-gray-400">AI Confidence</p>
                <p className="text-white font-medium">{trade.confidence}%</p>
              </div>
            )}

            <div>
              <p className="text-sm text-gray-400">
                {trade.reason ? 'Reason' : 'AI Reasoning'}
              </p>
              <p className="text-white text-sm">{trade.reason || trade.reasoning}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TradeHistory; 