import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TradingChart: React.FC = () => {
  // Sample price data
  const priceData = [
    { time: '09:00', price: 45200, volume: 1200 },
    { time: '10:00', price: 45350, volume: 1500 },
    { time: '11:00', price: 45200, volume: 1800 },
    { time: '12:00', price: 45180, volume: 1400 },
    { time: '13:00', price: 45300, volume: 1600 },
    { time: '14:00', price: 45450, volume: 2000 },
    { time: '15:00', price: 45500, volume: 2200 },
    { time: '16:00', price: 45480, volume: 1900 },
  ];

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={priceData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="time" 
            stroke="#9CA3AF"
            fontSize={10}
          />
          <YAxis 
            stroke="#9CA3AF"
            fontSize={10}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: '#1e2328',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#ffffff'
            }}
            formatter={(value: any) => [`$${value.toLocaleString()}`, 'Price']}
          />
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="#3b82f6" 
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TradingChart; 