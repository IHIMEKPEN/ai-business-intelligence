import React from 'react';
import { PerformanceSummary } from '../types/trading';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface PerformanceMetricsProps {
  performance: PerformanceSummary;
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ performance }) => {
  const monthlyReturns = [
    { month: 'Jan', return: 5.2 },
    { month: 'Feb', return: 3.8 },
    { month: 'Mar', return: 7.1 },
    { month: 'Apr', return: 4.5 },
    { month: 'May', return: 6.2 },
    { month: 'Jun', return: 8.9 },
  ];

  const assetAllocation = [
    { name: 'BTC-USD', value: 45, color: '#00d4aa' },
    { name: 'ETH-USD', value: 30, color: '#3b82f6' },
    { name: 'ADA-USD', value: 15, color: '#fbbf24' },
    { name: 'Cash', value: 10, color: '#6b7280' },
  ];

  const riskMetrics = [
    { metric: 'Sharpe Ratio', value: 1.8, target: 1.5, status: 'good' },
    { metric: 'Max Drawdown', value: performance.max_drawdown, target: 10, status: 'warning' },
    { metric: 'Volatility', value: 12.5, target: 15, status: 'good' },
    { metric: 'Beta', value: 0.85, target: 1.0, status: 'good' },
  ];

  return (
    <div className="space-y-6">
      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="trading-card text-center">
          <div className="text-3xl font-bold text-trading-green mb-1">
            {performance.win_rate.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-400">Win Rate</div>
        </div>
        
        <div className="trading-card text-center">
          <div className="text-3xl font-bold text-white mb-1">
            {performance.total_trades}
          </div>
          <div className="text-sm text-gray-400">Total Trades</div>
        </div>
        
        <div className="trading-card text-center">
          <div className={`text-3xl font-bold mb-1 ${performance.total_pnl >= 0 ? 'profit' : 'loss'}`}>
            {performance.total_pnl >= 0 ? '+' : ''}${performance.total_pnl.toFixed(2)}
          </div>
          <div className="text-sm text-gray-400">Total P&L</div>
        </div>
        
        <div className="trading-card text-center">
          <div className="text-3xl font-bold text-trading-red mb-1">
            {performance.max_drawdown.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-400">Max Drawdown</div>
        </div>
      </div>

      {/* Monthly Returns Chart */}
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">Monthly Returns</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthlyReturns}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="month" stroke="#9CA3AF" fontSize={12} />
              <YAxis stroke="#9CA3AF" fontSize={12} tickFormatter={(value) => `${value}%`} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1e2328',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#ffffff'
                }}
                formatter={(value: any) => [`${value}%`, 'Return']}
              />
              <Bar dataKey="return" fill="#00d4aa" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Asset Allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="trading-card">
          <h3 className="text-lg font-semibold mb-4">Asset Allocation</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={assetAllocation}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {assetAllocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1e2328',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#ffffff'
                  }}
                  formatter={(value: any) => [`${value}%`, 'Allocation']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {assetAllocation.map((asset, index) => (
              <div key={index} className="flex items-center">
                <div 
                  className="w-3 h-3 rounded mr-2" 
                  style={{ backgroundColor: asset.color }}
                ></div>
                <span className="text-sm text-gray-400">{asset.name}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="trading-card">
          <h3 className="text-lg font-semibold mb-4">Risk Metrics</h3>
          <div className="space-y-4">
            {riskMetrics.map((metric, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-trading-darker rounded">
                <div>
                  <p className="text-white font-medium">{metric.metric}</p>
                  <p className="text-sm text-gray-400">Target: {metric.target}</p>
                </div>
                <div className="text-right">
                  <p className={`font-bold ${
                    metric.status === 'good' ? 'text-trading-green' : 
                    metric.status === 'warning' ? 'text-trading-yellow' : 'text-trading-red'
                  }`}>
                    {metric.metric === 'Max Drawdown' || metric.metric === 'Volatility' ? 
                      `${metric.value.toFixed(1)}%` : metric.value.toFixed(2)}
                  </p>
                  <div className={`w-3 h-3 rounded-full mt-1 ${
                    metric.status === 'good' ? 'bg-trading-green' : 
                    metric.status === 'warning' ? 'bg-trading-yellow' : 'bg-trading-red'
                  }`}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trading Statistics */}
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">Trading Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium text-white mb-3">Trade Distribution</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Winning Trades</span>
                <span className="text-trading-green font-medium">{performance.winning_trades}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Losing Trades</span>
                <span className="text-trading-red font-medium">{performance.total_trades - performance.winning_trades}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Average Win</span>
                <span className="text-trading-green font-medium">$125.50</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Average Loss</span>
                <span className="text-trading-red font-medium">-$85.20</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-white mb-3">Risk Management</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Risk Level</span>
                <span className="text-trading-yellow font-medium capitalize">{performance.risk_level}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Position Size</span>
                <span className="text-white font-medium">10%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Stop Loss</span>
                <span className="text-white font-medium">5%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Take Profit</span>
                <span className="text-white font-medium">15%</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-white mb-3">Performance Summary</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Total Return</span>
                <span className={`font-medium ${performance.total_pnl_percent >= 0 ? 'profit' : 'loss'}`}>
                  {performance.total_pnl_percent >= 0 ? '+' : ''}{performance.total_pnl_percent.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Annualized Return</span>
                <span className="text-trading-green font-medium">18.5%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Best Trade</span>
                <span className="text-trading-green font-medium">+$450.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Worst Trade</span>
                <span className="text-trading-red font-medium">-$180.00</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics; 