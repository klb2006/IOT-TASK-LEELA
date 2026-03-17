import React from 'react';
import { motion } from 'framer-motion';

const ProgressBar = ({ percentage, color = "blue", title, loading = false }) => {
  return (
    <div className="premium-card w-full flex flex-col gap-4">
      <div className="flex justify-between items-end">
        <h3 className="text-slate-500 dark:text-slate-400 font-medium text-sm uppercase tracking-wider">
          {title}
        </h3>
        <span className="text-2xl font-outfit font-bold text-slate-900 dark:text-white">
          {percentage}%
        </span>
      </div>
      
      <div className="h-6 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden shadow-inner p-1">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`h-full rounded-full bg-gradient-to-r from-${color}-500 to-${color}-400 shadow-lg shadow-${color}-500/20 relative`}
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        </motion.div>
      </div>
    </div>
  );
};

export default ProgressBar;
