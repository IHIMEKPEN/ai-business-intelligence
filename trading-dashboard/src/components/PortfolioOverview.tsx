import React from 'react';
import { DollarSign, TrendingUp, Activity, Target } from 'lucide-react';
import { PortfolioData } from '../types/trading';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface PortfolioOverviewProps {
  data: PortfolioData;
}

const PortfolioOverview: React.FC<PortfolioOverviewProps> = ({ data }) => {
  // Sample data for charts
  const portfolioHistory = [
    { time: '09:00', value: 10000 },
    { time: '10:00', value: 10150 },
    { time: '11:00', value: 10200 },
    { time: '12:00', value: 10180 },
    { time: '13:00', value: 10300 },
    { time: '14:00', value: 10450 },
    { time: '15:00', value: 10500 },
    { time: '16:00', value: 10480 },
  ];

  const performanceData = [
    { metric: 'Win Rate', value: data.performance.win_rate, target: 60, color: 'text-trading-green' },
    { metric: 'Max Drawdown', value: data.performance.max_drawdown, target: 10, color: 'text-trading-red' },
    { metric: 'Sharpe Ratio', value: 1.8, target: 1.5, color: 'text-trading-blue' },
    { metric: 'Total Return', value: data.performance.total_pnl_percent, target: 15, color: 'text-trading-green' },
  ];

  return (
    <div className="space-y-6">
      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="trading-card">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-trading-green mr-3" />
            <div>
              <p className="text-sm text-gray-400">Total Portfolio</p>
              <p className="text-2xl font-bold text-white">${data.total_value.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="trading-card">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-trading-green mr-3" />
            <div>
              <p className="text-sm text-gray-400">Total P&L</p>
              <p className={`text-2xl font-bold ${data.total_pnl >= 0 ? 'profit' : 'loss'}`}>
                {data.total_pnl >= 0 ? '+' : ''}${data.total_pnl.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="trading-card">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-trading-blue mr-3" />
            <div>
              <p className="text-sm text-gray-400">Daily P&L</p>
              <p className={`text-2xl font-bold ${data.daily_pnl >= 0 ? 'profit' : 'loss'}`}>
                {data.daily_pnl >= 0 ? '+' : ''}${data.daily_pnl.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="trading-card">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-trading-yellow mr-3" />
            <div>
              <p className="text-sm text-gray-400">Open Positions</p>
              <p className="text-2xl font-bold text-white">{data.positions.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio Value Chart */}
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">Portfolio Value Over Time</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={portfolioHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="time" 
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis 
                stroke="#9CA3AF"
                fontSize={12}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1e2328',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#ffffff'
                }}
                formatter={(value: any) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#00d4aa" 
                fill="#00d4aa" 
                fillOpacity={0.1}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="trading-card">
          <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
          <div className="space-y-4">
            {performanceData.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-gray-400">{item.metric}</span>
                <div className="flex items-center space-x-2">
                  <span className={`font-bold ${item.color}`}>
                    {item.metric === 'Max Drawdown' ? `${item.value.toFixed(1)}%` : 
                     item.metric === 'Win Rate' ? `${item.value.toFixed(1)}%` :
                     item.metric === 'Sharpe Ratio' ? item.value.toFixed(2) :
                     `${item.value.toFixed(1)}%`}
                  </span>
                  <span className="text-xs text-gray-500">/ {item.target}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="trading-card">
          <h3 className="text-lg font-semibold mb-4">AI Trading Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-trading-darker rounded">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-trading-green rounded-full mr-3"></div>
                <span className="text-white">Trading Bot Active</span>
              </div>
              <span className="text-sm text-gray-400">Online</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-trading-darker rounded">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-trading-blue rounded-full mr-3"></div>
                <span className="text-white">AI Analysis</span>
              </div>
              <span className="text-sm text-gray-400">Real-time</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-trading-darker rounded">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-trading-yellow rounded-full mr-3"></div>
                <span className="text-white">Risk Management</span>
              </div>
              <span className="text-sm text-gray-400">Active</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-trading-darker rounded">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-trading-green rounded-full mr-3"></div>
                <span className="text-white">Market Data</span>
              </div>
              <span className="text-sm text-gray-400">Connected</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">Recent Trading Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-trading-darker rounded">
            <div>
              <div className="font-medium text-white">BTC-USD Position Opened</div>
              <div className="text-sm text-gray-400">2 minutes ago</div>
            </div>
            <div className="text-right">
              <div className="text-trading-green font-bold">+$150.00</div>
              <div className="text-sm text-gray-400">Entry: $45,200</div>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 bg-trading-darker rounded">
            <div>
              <div className="font-medium text-white">ETH-USD Position Closed</div>
              <div className="text-sm text-gray-400">15 minutes ago</div>
            </div>
            <div className="text-right">
              <div className="text-trading-red font-bold">-$75.00</div>
              <div className="text-sm text-gray-400">Exit: $3,150</div>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 bg-trading-darker rounded">
            <div>
              <div className="font-medium text-white">ADA-USD Signal Generated</div>
              <div className="text-sm text-gray-400">1 hour ago</div>
            </div>
            <div className="text-right">
              <div className="text-trading-yellow font-bold">HOLD</div>
              <div className="text-sm text-gray-400">85% confidence</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioOverview; 