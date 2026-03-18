import React from 'react';
import { motion } from 'framer-motion';

const WaterLevelIndicator = ({ waterLiters, waterPercentage, loading = false }) => {
  // waterPercentage is 0 to 100 (for fill height)
  // waterLiters is the actual liters value
  const fillHeight = loading ? 50 : (100 - waterPercentage);
  const displayLiters = loading ? 'Loading...' : waterLiters.toFixed(1);
  const displayPercentage = loading ? '--' : waterPercentage.toFixed(1);

  return (
    <div className="premium-card flex flex-col items-center gap-6 h-full">
      <h3 className="text-slate-500 dark:text-slate-400 font-medium text-sm uppercase tracking-wider">
        Water Volume
      </h3>
      
      <div className="relative w-32 h-64 bg-slate-100 dark:bg-slate-800 rounded-[2rem] border-4 border-slate-200 dark:border-slate-700 overflow-hidden shadow-inner">
        {/* Animated Water Background */}
        <motion.div
          initial={{ top: '100%' }}
          animate={{ top: `${fillHeight}%` }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          className="absolute left-0 right-0 bottom-0 bg-blue-500/80 backdrop-blur-sm"
        >
          {/* Wave animation effect */}
          <div className="absolute top-0 left-0 w-full h-4 -mt-3 overflow-hidden">
            <motion.div
              animate={{ x: [0, -40] }}
              transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
              className="flex whitespace-nowrap"
            >
              {[1, 2, 3, 4].map((i) => (
                <svg key={i} className="w-16 h-4 text-blue-500/80 fill-current" viewBox="0 0 100 20">
                  <path d="M0 10 Q25 0 50 10 T100 10 V20 H0 Z" />
                </svg>
              ))}
            </motion.div>
          </div>
          
          <div className="absolute inset-0 bg-gradient-to-b from-blue-400/30 to-transparent" />
        </motion.div>

        {/* Level Markings */}
        <div className="absolute inset-0 flex flex-col justify-between py-6 px-1 pointer-events-none opacity-20">
          {[100, 75, 50, 25, 0].map((mark) => (
            <div key={mark} className="flex items-center gap-2">
              <div className="w-4 h-0.5 bg-slate-500" />
              <span className="text-[10px] font-bold">{mark}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Display both Liters and Percentage */}
      <div className="text-center w-full">
        <div className="text-3xl font-outfit font-bold text-slate-900 dark:text-white">
          {displayLiters} <span className="text-lg text-slate-500">L</span>
        </div>
        <div className="text-lg font-semibold text-blue-600 dark:text-blue-400 mt-1">
          {displayPercentage}%
        </div>
      </div>
    </div>
  );
};

export default WaterLevelIndicator;
