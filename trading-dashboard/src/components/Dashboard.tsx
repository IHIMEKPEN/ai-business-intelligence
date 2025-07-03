import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, Target, AlertTriangle, Settings, BarChart3 } from 'lucide-react';
import { PortfolioData } from '../types/trading';
import PortfolioOverview from './PortfolioOverview';
import ActivePositions from './ActivePositions';
import TradingChart from './TradingChart';
import AIAnalysis from './AIAnalysis';
import TradeHistory from './TradeHistory';
import PerformanceMetrics from './PerformanceMetrics';
import RiskManagement from './RiskManagement';

const Dashboard: React.FC = () => {
  const [portfolioData, setPortfolioData] = useState<PortfolioData>({
    total_value: 10000,
    available_cash: 8500,
    total_pnl: 1500,
    daily_pnl: 250,
    positions: [],
    performance: {
      total_trades: 0,
      winning_trades: 0,
      win_rate: 0,
      total_pnl: 0,
      total_pnl_percent: 0,
      portfolio_value: 10000,
      max_drawdown: 0,
      open_positions: 0,
      risk_level: 'moderate',
      symbols_traded: []
    }
  });

  const [activeTab, setActiveTab] = useState('overview');

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate price movements and updates
      setPortfolioData(prev => ({
        ...prev,
        total_pnl: prev.total_pnl + (Math.random() - 0.5) * 100,
        daily_pnl: prev.daily_pnl + (Math.random() - 0.5) * 50
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'positions', label: 'Positions', icon: Target },
    { id: 'analysis', label: 'AI Analysis', icon: Activity },
    { id: 'history', label: 'Trade History', icon: TrendingUp },
    { id: 'performance', label: 'Performance', icon: TrendingDown },
    { id: 'risk', label: 'Risk Management', icon: AlertTriangle },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <PortfolioOverview data={portfolioData} />;
      case 'positions':
        return <ActivePositions positions={portfolioData.positions} />;
      case 'analysis':
        return <AIAnalysis />;
      case 'history':
        return <TradeHistory />;
      case 'performance':
        return <PerformanceMetrics performance={portfolioData.performance} />;
      case 'risk':
        return <RiskManagement />;
      case 'settings':
        return <div className="trading-card">Settings Panel</div>;
      default:
        return <PortfolioOverview data={portfolioData} />;
    }
  };

  return (
    <div className="min-h-screen bg-trading-dark">
      {/* Header */}
      <header className="bg-trading-darker border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-trading-green mr-3" />
              <h1 className="text-xl font-bold text-white">AI Business Intelligence Trading Platform</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm text-gray-400">Portfolio Value</div>
                <div className="text-lg font-bold text-white">
                  ${portfolioData.total_value.toLocaleString()}
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-400">Daily P&L</div>
                <div className={`text-lg font-bold ${portfolioData.daily_pnl >= 0 ? 'profit' : 'loss'}`}>
                  {portfolioData.daily_pnl >= 0 ? '+' : ''}${portfolioData.daily_pnl.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-trading-light border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'border-trading-blue text-trading-blue'
                      : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {renderTabContent()}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="trading-card">
              <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total P&L</span>
                  <span className={`font-bold ${portfolioData.total_pnl >= 0 ? 'profit' : 'loss'}`}>
                    {portfolioData.total_pnl >= 0 ? '+' : ''}${portfolioData.total_pnl.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Win Rate</span>
                  <span className="font-bold text-white">
                    {portfolioData.performance.win_rate.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Open Positions</span>
                  <span className="font-bold text-white">
                    {portfolioData.positions.length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Risk Level</span>
                  <span className="font-bold text-trading-yellow capitalize">
                    {portfolioData.performance.risk_level}
                  </span>
                </div>
              </div>
            </div>

            {/* Trading Chart */}
            <div className="trading-card">
              <h3 className="text-lg font-semibold mb-4">Price Chart</h3>
              <TradingChart />
            </div>

            {/* Recent Signals */}
            <div className="trading-card">
              <h3 className="text-lg font-semibold mb-4">Recent AI Signals</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-trading-darker rounded">
                  <div>
                    <div className="font-medium text-white">BTC-USD</div>
                    <div className="text-sm text-gray-400">Strong buy signal</div>
                  </div>
                  <div className="text-right">
                    <div className="text-trading-green font-bold">BUY</div>
                    <div className="text-sm text-gray-400">85% confidence</div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-trading-darker rounded">
                  <div>
                    <div className="font-medium text-white">ETH-USD</div>
                    <div className="text-sm text-gray-400">Hold position</div>
                  </div>
                  <div className="text-right">
                    <div className="text-trading-yellow font-bold">HOLD</div>
                    <div className="text-sm text-gray-400">72% confidence</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard; 