import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Smartphone, 
  Settings, 
  BarChart3,
  Activity
} from 'lucide-react';

function Sidebar() {
  const navItems = [
    { to: '/dashboard', icon: Home, label: 'Dashboard' },
    { to: '/platforms', icon: Smartphone, label: 'Platforms' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    { to: '/activity', icon: Activity, label: 'Activity' },
    { to: '/settings', icon: Settings, label: 'Settings' }
  ];

  return (
    <div className="w-64 bg-white shadow-sm border-r border-gray-200 h-screen">
      <div className="p-6">
        <div className="flex items-center mb-8">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
            <Smartphone className="h-6 w-6 text-white" />
          </div>
          <div className="ml-3">
            <h2 className="text-lg font-semibold text-gray-900">SMA Suite</h2>
            <p className="text-xs text-gray-600">v2.0.0</p>
          </div>
        </div>
        
        <nav className="space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`
              }
            >
              <item.icon className="h-5 w-5 mr-3" />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}

export default Sidebar;