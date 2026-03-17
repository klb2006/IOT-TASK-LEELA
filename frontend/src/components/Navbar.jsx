import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, BarChart3, Moon, Sun } from 'lucide-react';

const Navbar = ({ darkMode, toggleDarkMode }) => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto glass rounded-2xl px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/30">
            <LayoutDashboard className="text-white w-6 h-6" />
          </div>
          <span className="text-xl font-outfit font-bold tracking-tight bg-gradient-to-r from-primary-600 to-blue-500 bg-clip-text text-transparent">
            Smart Nodes KIET
          </span>
        </div>

        <div className="flex items-center gap-6">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-300 font-medium ${
                isActive
                  ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`
            }
          >
            <LayoutDashboard size={20} />
            <span className="hidden sm:inline">Dashboard</span>
          </NavLink>
          
          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              `flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-300 font-medium ${
                isActive
                  ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`
            }
          >
            <BarChart3 size={20} />
            <span className="hidden sm:inline">Analytics</span>
          </NavLink>

          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-xl glass hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-300"
            aria-label="Toggle dark mode"
          >
            {darkMode ? <Sun size={20} className="text-yellow-500" /> : <Moon size={20} className="text-slate-700" />}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
