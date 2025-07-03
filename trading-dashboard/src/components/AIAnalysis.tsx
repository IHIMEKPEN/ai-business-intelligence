import React from 'react';
import { Brain, Activity } from 'lucide-react';

const AIAnalysis: React.FC = () => {
  const marketAnalysis = [
    {
      symbol: 'BTC-USD',
      current_price: 45480,
      price_change: 2.1,
      trend: 'bullish',
      confidence: 85,
      recommendation: 'Strong Buy',
      reasoning: 'Strong momentum with low volatility, technical indicators show upward trend',
      risk_level: 'Low'
    },
    {
      symbol: 'ETH-USD',
      current_price: 3180,
      price_change: -0.8,
      trend: 'neutral',
      confidence: 72,
      recommendation: 'Hold',
      reasoning: 'Mixed signals, waiting for clearer direction',
      risk_level: 'Medium'
    },
    {
      symbol: 'ADA-USD',
      current_price: 0.52,
      price_change: 1.5,
      trend: 'bullish',
      confidence: 78,
      recommendation: 'Buy',
      reasoning: 'Positive volume increase with breakout pattern',
      risk_level: 'Medium'
    }
  ];

  const aiInsights = [
    {
      type: 'Market Sentiment',
      value: 'Bullish',
      confidence: 78,
      description: 'Overall market sentiment is positive with increasing institutional adoption'
    },
    {
      type: 'Volatility Forecast',
      value: 'Low',
      confidence: 85,
      description: 'Expected low volatility period, good for trend following strategies'
    },
    {
      type: 'Risk Assessment',
      value: 'Moderate',
      confidence: 82,
      description: 'Current risk levels are within acceptable parameters'
    }
  ];

  return (
    <div className="space-y-6">
      {/* AI Status */}
      <div className="trading-card">
        <div className="flex items-center mb-4">
          <Brain className="h-6 w-6 text-trading-blue mr-2" />
          <h3 className="text-lg font-semibold">AI Analysis Engine</h3>
          <div className="ml-auto flex items-center">
            <div className="w-3 h-3 bg-trading-green rounded-full mr-2"></div>
            <span className="text-sm text-gray-400">Active</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-trading-darker rounded p-3">
            <div className="text-sm text-gray-400">Analysis Frequency</div>
            <div className="text-white font-medium">Every 5 minutes</div>
          </div>
          <div className="bg-trading-darker rounded p-3">
            <div className="text-sm text-gray-400">Signals Generated</div>
            <div className="text-white font-medium">24 today</div>
          </div>
          <div className="bg-trading-darker rounded p-3">
            <div className="text-sm text-gray-400">Accuracy Rate</div>
            <div className="text-trading-green font-medium">78.5%</div>
          </div>
        </div>
      </div>

      {/* Market Analysis */}
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">Real-time Market Analysis</h3>
        <div className="space-y-4">
          {marketAnalysis.map((analysis, index) => (
            <div key={index} className="bg-trading-darker rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  <h4 className="text-lg font-semibold text-white">{analysis.symbol}</h4>
                  <span className={`ml-2 px-2 py-1 text-xs rounded ${
                    analysis.trend === 'bullish' ? 'bg-trading-green text-white' :
                    analysis.trend === 'bearish' ? 'bg-trading-red text-white' :
                    'bg-trading-yellow text-white'
                  }`}>
                    {analysis.trend.toUpperCase()}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-white font-medium">${analysis.current_price.toLocaleString()}</div>
                  <div className={`text-sm ${analysis.price_change >= 0 ? 'profit' : 'loss'}`}>
                    {analysis.price_change >= 0 ? '+' : ''}{analysis.price_change}%
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-3">
                <div>
                  <p className="text-sm text-gray-400">AI Recommendation</p>
                  <p className={`font-medium ${
                    analysis.recommendation === 'Strong Buy' || analysis.recommendation === 'Buy' ? 'text-trading-green' :
                    analysis.recommendation === 'Sell' ? 'text-trading-red' : 'text-trading-yellow'
                  }`}>
                    {analysis.recommendation}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Confidence</p>
                  <p className="text-white font-medium">{analysis.confidence}%</p>
                </div>
              </div>

              <div className="mb-3">
                <p className="text-sm text-gray-400">AI Reasoning</p>
                <p className="text-white text-sm">{analysis.reasoning}</p>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Risk Level</p>
                  <p className={`font-medium ${
                    analysis.risk_level === 'Low' ? 'text-trading-green' :
                    analysis.risk_level === 'Medium' ? 'text-trading-yellow' : 'text-trading-red'
                  }`}>
                    {analysis.risk_level}
                  </p>
                </div>
                <button className="trading-button-primary text-sm">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Insights */}
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">AI Market Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {aiInsights.map((insight, index) => (
            <div key={index} className="bg-trading-darker rounded-lg p-4 border border-gray-700">
              <div className="flex items-center mb-3">
                <Activity className="h-5 w-5 text-trading-blue mr-2" />
                <h4 className="font-medium text-white">{insight.type}</h4>
              </div>
              
              <div className="mb-3">
                <div className="text-2xl font-bold text-white mb-1">{insight.value}</div>
                <div className="text-sm text-gray-400">{insight.confidence}% confidence</div>
              </div>
              
              <p className="text-sm text-gray-300">{insight.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* AI Performance Metrics */}
      <div className="trading-card">
        <h3 className="text-lg font-semibold mb-4">AI Performance Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-trading-darker rounded p-4 text-center">
            <div className="text-2xl font-bold text-trading-green mb-1">78.5%</div>
            <div className="text-sm text-gray-400">Signal Accuracy</div>
          </div>
          <div className="bg-trading-darker rounded p-4 text-center">
            <div className="text-2xl font-bold text-trading-blue mb-1">24</div>
            <div className="text-sm text-gray-400">Signals Today</div>
          </div>
          <div className="bg-trading-darker rounded p-4 text-center">
            <div className="text-2xl font-bold text-trading-yellow mb-1">156</div>
            <div className="text-sm text-gray-400">Total Signals</div>
          </div>
          <div className="bg-trading-darker rounded p-4 text-center">
            <div className="text-2xl font-bold text-trading-green mb-1">15.2%</div>
            <div className="text-sm text-gray-400">Avg Return</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAnalysis; 