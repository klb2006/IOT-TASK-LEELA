import React from 'react';
import { motion } from 'framer-motion';

const SensorCard = ({ title, value, unit, icon: Icon, color, description, loading = false }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="premium-card relative overflow-hidden group"
    >
      <div className={`absolute top-0 right-0 w-32 h-32 -mr-8 -mt-8 rounded-full opacity-10 blur-2xl group-hover:opacity-20 transition-opacity bg-${color}-500`} />
      
      <div className="flex flex-col gap-4">
        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center bg-${color}-500/10 text-${color}-600 dark:text-${color}-400 mb-2`}>
          {loading ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
              className="w-8 h-8 border-2 border-slate-300 border-t-slate-600 rounded-full"
            />
          ) : (
            <Icon size={32} />
          )}
        </div>
        
        <div>
          <h3 className="text-slate-500 dark:text-slate-400 font-medium text-sm lg:text-base uppercase tracking-wider mb-1">
            {title}
          </h3>
          <div className="flex items-baseline gap-2">
            {loading ? (
              <motion.div
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className="h-10 w-32 bg-slate-300 dark:bg-slate-600 rounded"
              />
            ) : (
              <>
                <span className="text-4xl lg:text-5xl font-outfit font-bold text-slate-900 dark:text-white">
                  {value}
                </span>
                <span className="text-xl lg:text-2xl font-medium text-slate-400 dark:text-slate-500">
                  {unit}
                </span>
              </>
            )}
          </div>
        </div>
        
        {description && (
          <p className="text-slate-400 dark:text-slate-600 text-xs lg:text-sm mt-2 border-t border-slate-100 dark:border-slate-800 pt-3 italic">
            {description}
          </p>
        )}
      </div>
    </motion.div>
  );
};

export default SensorCard;
