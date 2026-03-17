import React from 'react';
import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const Analytics = () => {
  // Dummy time-series data
  const generateData = () => {
    return Array.from({ length: 12 }, (_, i) => ({
      time: `${i * 2}:00`,
      distance: 100 + Math.random() * 50,
      temperature: 25 + Math.random() * 5,
      waterLevel: 60 + Math.random() * 20,
      waterPercentage: 50 + Math.random() * 30,
    }));
  };

  const data = generateData();

  const ChartSection = ({ title, dataKey, color, unit }) => (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="premium-card col-span-1"
    >
      <h3 className="text-xl font-outfit font-bold mb-6 text-slate-800 dark:text-slate-200">
        {title} ({unit})
      </h3>
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={color} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" opacity={0.5} />
            <XAxis 
              dataKey="time" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fill: '#64748b' }} 
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fill: '#64748b' }} 
            />
            <Tooltip 
              contentStyle={{ 
                borderRadius: '16px', 
                border: 'none', 
                boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(8px)'
              }} 
            />
            <Legend verticalAlign="top" height={36}/>
            <Area 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              strokeWidth={3}
              fillOpacity={1} 
              fill={`url(#gradient-${dataKey})`} 
              animationDuration={1500}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen pt-28 pb-12 px-6 lg:px-12 max-w-7xl mx-auto">
      <header className="mb-10">
        <motion.h1 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-4xl font-outfit font-bold text-slate-900 dark:text-white"
        >
          Data Analytics
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="text-slate-500 dark:text-slate-400 mt-2"
        >
          Historical trends and sensor performance over time.
        </motion.p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ChartSection title="Distance" dataKey="distance" color="#3B82F6" unit="cm" />
        <ChartSection title="Temperature" dataKey="temperature" color="#F97316" unit="°C" />
        <ChartSection title="Water Level" dataKey="waterLevel" color="#0EA5E9" unit="%" />
        <ChartSection title="Water Percentage" dataKey="waterPercentage" color="#06B6D4" unit="%" />
      </div>
    </div>
  );
};

export default Analytics;
