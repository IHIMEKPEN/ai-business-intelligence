import React, { useState } from 'react';
import { AlertTriangle, Shield, Settings, TrendingDown, Activity } from 'lucide-react';

const RiskManagement: React.FC = () => {
  const [riskLevel, setRiskLevel] = useState('moderate');
  const [stopLossPercent, setStopLossPercent] = useState(5);
  const [takeProfitPercent, setTakeProfitPercent] = useState(15);
  const [maxPositions, setMaxPositions] = useState(5);

  const riskAlerts = [
    {
      type: 'warning',
      message: 'High volatility detected in BTC-USD',
      time: '2 minutes ago',
      severity: 'medium'
    },
    {
      type: 'info',
      message: 'Portfolio drawdown approaching limit',
      time: '15 minutes ago',
      severity: 'low'
    },
    {
      type: 'success',
      message: 'Risk parameters within acceptable range',
      time: '1 hour ago',
      severity: 'low'
    }
  ];

  const riskMetrics = [
    { metric: 'Current Drawdown', value: 8.5, limit: 20, status: 'safe' },
    { metric: 'Portfolio Volatility', value: 12.3, limit: 25, status: 'safe' },
    { metric: 'Position Concentration', value: 35, limit: 40, status: 'warning' },
    { metric: 'Daily Loss Limit', value: 2.1, limit: 5, status: 'safe' }
  ];

  return (
    <div className="space-y-6">
      {/* Risk Overview */}
      <div className="trading-card">
        <div className="flex items-center mb-4">
          <Shield className="h-6 w-6 text-trading-blue mr-2" />
          <h3 className="text-lg font-semibold">Risk Management Overview</h3>
          <div className="ml-auto flex items-center">
            <div className="w-3 h-3 bg-trading-green rounded-full mr-2"></div>
            <span className="text-sm text-gray-400">All Systems Normal</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {riskMetrics.map((metric, index) => (
            <div key={index} className="bg-trading-darker rounded p-3">
              <div className="text-sm text-gray-400 mb-1">{metric.metric}</div>
              <div className="text-lg font-bold text-white mb-1">
                {metric.metric.includes('Drawdown') || metric.metric.includes('Volatility') || metric.metric.includes('Loss') ? 
                  `${metric.value}%` : `${metric.value}%`}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">Limit: {metric.limit}%</span>
                <div className={`w-2 h-2 rounded-full ${
                  metric.status === 'safe' ? 'bg-trading-green' : 
                  metric.status === 'warning' ? 'bg-trading-yellow' : 'bg-trading-red'
                }`}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="trading-card">
          <h3 className="text-lg font-semibold mb-4">Risk Configuration</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Risk Level
              </label>
              <select 
                value={riskLevel}
                onChange={(e) => setRiskLevel(e.target.value)}
                className="trading-input w-full"
              >
                <option value="conservative">Conservative</option>
                <option value="moderate">Moderate</option>
                <option value="aggressive">Aggressive</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Stop Loss Percentage
              </label>
              <input 
                type="number"
                value={stopLossPercent}
                onChange={(e) => setStopLossPercent(Number(e.target.value))}
                className="trading-input w-full"
                min="1"
                max="20"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Take Profit Percentage
              </label>
              <input 
                type="number"
                value={takeProfitPercent}
                onChange={(e) => setTakeProfitPercent(Number(e.target.value))}
                className="trading-input w-full"
                min="5"
                max="50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Maximum Positions
              </label>
              <input 
                type="number"
                value={maxPositions}
                onChange={(e) => setMaxPositions(Number(e.target.value))}
                className="trading-input w-full"
                min="1"
                max="10"
              />
            </div>

            <button className="trading-button-primary w-full">
              Update Risk Settings
            </button>
          </div>
        </div>

        <div className="trading-card">
          <h3 className="text-lg font-semibold mb-4">Risk Alerts</h3>
          
          <div className="space-y-3">
            {riskAlerts.map((alert, index) => (
              <div key={index} className={`p-3 rounded-lg border ${
                alert.type === 'warning' ? 'border-trading-yellow bg-yellow-900/20' :
                alert.type === 'info' ? 'border-trading-blue bg-blue-900/20' :
                'border-trading-green bg-green-900/20'
              }`}>
                <div className="flex items-start">
                  <AlertTriangle className={`h-4 w-4 mt-0.5 mr-2 ${
                    alert.type === 'warning' ? 'text-trading-yellow' :
                    alert.type === 'info' ? 'text-trading-blue' : 'text-trading-green'
                  }`} />
                  <div className="flex-1">
                    <p className="text-white text-sm">{alert.message}</p>
                    <p className="text-gray-400 text-xs mt-1">{alert.time}</p>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${
                    alert.severity === 'high' ? 'bg-trading-red' :
                    alert.severity === 'medium' ? 'bg-trading-yellow' : 'bg-trading-green'
                  }`}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Emergency Controls */}
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">Emergency Controls</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="trading-button-danger flex items-center justify-center">
            <TrendingDown className="h-4 w-4 mr-2" />
            Emergency Stop
          </button>
          
          <button className="trading-button-primary flex items-center justify-center">
            <Activity className="h-4 w-4 mr-2" />
            Pause Trading
          </button>
          
          <button className="trading-button-success flex items-center justify-center">
            <Settings className="h-4 w-4 mr-2" />
            Reset Limits
          </button>
        </div>
      </div>

      {/* Risk Limits */}
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">Risk Limits</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-white mb-3">Portfolio Limits</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-2 bg-trading-darker rounded">
                <span className="text-gray-400">Max Daily Loss</span>
                <span className="text-white font-medium">5%</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-trading-darker rounded">
                <span className="text-gray-400">Max Drawdown</span>
                <span className="text-white font-medium">20%</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-trading-darker rounded">
                <span className="text-gray-400">Max Position Size</span>
                <span className="text-white font-medium">10%</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-trading-darker rounded">
                <span className="text-gray-400">Max Leverage</span>
                <span className="text-white font-medium">1x</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-white mb-3">Trading Limits</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-2 bg-trading-darker rounded">
                <span className="text-gray-400">Max Open Positions</span>
                <span className="text-white font-medium">5</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-trading-darker rounded">
                <span className="text-gray-400">Min Trade Size</span>
                <span className="text-white font-medium">$100</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-trading-darker rounded">
                <span className="text-gray-400">Max Trade Size</span>
                <span className="text-white font-medium">$1,000</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-trading-darker rounded">
                <span className="text-gray-400">Cooldown Period</span>
                <span className="text-white font-medium">5 min</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskManagement; 