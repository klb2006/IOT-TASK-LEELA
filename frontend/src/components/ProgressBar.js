import React from 'react';

const ProgressBar = ({ percentage, color = "blue", title, loading = false }) => {
  const colorClasses = {
    blue: 'bg-gradient-to-r from-blue-500 to-blue-400',
    orange: 'bg-gradient-to-r from-orange-500 to-orange-400',
    green: 'bg-gradient-to-r from-green-500 to-green-400',
    sky: 'bg-gradient-to-r from-sky-500 to-sky-400',
    purple: 'bg-gradient-to-r from-purple-500 to-purple-400',
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <div className="flex justify-between items-end mb-4">
        <h3 className="text-slate-500 dark:text-slate-400 font-medium text-sm uppercase tracking-wider">
          {title}
        </h3>
        <span className="text-3xl font-bold text-slate-900 dark:text-white">
          {loading ? '--' : `${percentage.toFixed(1)}%`}
        </span>
      </div>
      
      <div className="h-6 w-full bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden shadow-inner p-1">
        <div
          style={{ width: `${percentage}%` }}
          className={`h-full rounded-full ${colorClasses[color] || colorClasses.blue} shadow-lg transition-all duration-1000 relative`}
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
