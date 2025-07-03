import React from 'react';
import { Position } from '../types/trading';
import { TrendingUp, X } from 'lucide-react';

interface ActivePositionsProps {
  positions: Position[];
}

const ActivePositions: React.FC<ActivePositionsProps> = ({ positions }) => {
  // Sample positions for demo
  const samplePositions: Position[] = [
    {
      symbol: 'BTC-USD',
      entry_price: 45200,
      quantity: 0.1,
      entry_time: '2024-01-15T10:30:00Z',
      current_price: 45480,
      pnl: 28.0,
      pnl_percent: 0.62,
      stop_loss: 42940,
      take_profit: 51980
    },
    {
      symbol: 'ETH-USD',
      entry_price: 3150,
      quantity: 1.5,
      entry_time: '2024-01-15T09:15:00Z',
      current_price: 3180,
      pnl: 45.0,
      pnl_percent: 0.95,
      stop_loss: 2992.5,
      take_profit: 3622.5
    }
  ];

  const displayPositions = positions.length > 0 ? positions : samplePositions;

  return (
    <div className="space-y-6">
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">Active Positions</h3>
        {displayPositions.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No active positions</p>
            <p className="text-sm">AI will open positions based on market signals</p>
          </div>
        ) : (
          <div className="space-y-4">
            {displayPositions.map((position, index) => (
              <div key={index} className="bg-trading-darker rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <h4 className="text-lg font-semibold text-white">{position.symbol}</h4>
                    <span className="ml-2 px-2 py-1 bg-trading-blue text-white text-xs rounded">
                      {position.quantity.toFixed(3)}
                    </span>
                  </div>
                  <button className="text-gray-400 hover:text-trading-red transition-colors">
                    <X className="h-4 w-4" />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-3">
                  <div>
                    <p className="text-sm text-gray-400">Entry Price</p>
                    <p className="text-white font-medium">${position.entry_price.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Current Price</p>
                    <p className="text-white font-medium">${position.current_price.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">P&L</p>
                    <p className={`font-medium ${position.pnl >= 0 ? 'profit' : 'loss'}`}>
                      {position.pnl >= 0 ? '+' : ''}${position.pnl.toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">P&L %</p>
                    <p className={`font-medium ${position.pnl_percent >= 0 ? 'profit' : 'loss'}`}>
                      {position.pnl_percent >= 0 ? '+' : ''}{position.pnl_percent.toFixed(2)}%
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-400">Stop Loss</p>
                    <p className="text-trading-red font-medium">${position.stop_loss?.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Take Profit</p>
                    <p className="text-trading-green font-medium">${position.take_profit?.toLocaleString()}</p>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t border-gray-700">
                  <p className="text-sm text-gray-400">Entry Time</p>
                  <p className="text-white text-sm">
                    {new Date(position.entry_time).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ActivePositions; 