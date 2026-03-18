import React from 'react';

const SensorCard = ({ title, value, unit, icon: Icon, color = 'blue', description, loading = false }) => {
  const colorClasses = {
    blue: 'bg-blue-500/10 text-blue-600',
    orange: 'bg-orange-500/10 text-orange-600',
    green: 'bg-green-500/10 text-green-600',
    purple: 'bg-purple-500/10 text-purple-600',
    cyan: 'bg-cyan-500/10 text-cyan-600',
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm hover:shadow-md hover:border-blue-300 transition-all duration-300">
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClasses[color] || colorClasses.blue} mb-4`}>
        {loading ? (
          <div className="w-6 h-6 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
        ) : (
          Icon && <Icon size={24} />
        )}
      </div>
      
      <div>
        <h3 className="text-slate-500 dark:text-slate-400 font-medium text-sm uppercase tracking-wider mb-1">
          {title}
        </h3>
        <div className="flex items-baseline gap-2">
          {loading ? (
            <div className="h-10 w-32 bg-slate-300 dark:bg-slate-600 rounded animate-pulse" />
          ) : (
            <>
              <span className="text-4xl font-bold text-slate-900 dark:text-white">
                {value}
              </span>
              <span className="text-lg font-medium text-slate-400 dark:text-slate-500">
                {unit}
              </span>
            </>
          )}
        </div>
        {description && !loading && (
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-2">{description}</p>
        )}
      </div>
    </div>
  );
};

export default SensorCard;
