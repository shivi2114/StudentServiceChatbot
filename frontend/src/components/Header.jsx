import React, { useState } from 'react';
import { Bell, Sparkles, CheckCircle2, ShieldAlert } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Header = ({ activeTab, notifications = [] }) => {
  const { user, studentProfile } = useAuth();
  const [showNotifications, setShowNotifications] = useState(false);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const titles = {
    dashboard: 'Student Overview & Academic Hub',
    chat: 'CampusAI Multi-Agent Assistance Console',
    complaints: 'Grievance Redressal & Support Tickets',
    announcements: 'Campus Circulars & Official Notices',
    admin: 'University Administration Portal',
  };

  return (
    <header className="h-16 px-6 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-between sticky top-0 z-30 transition-colors">
      <div>
        <h1 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          {titles[activeTab] || 'CampusAI'}
          {activeTab === 'chat' && (
            <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              7 Agents Orchestrated
            </span>
          )}
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Official Academic Year 2026-2027 • Institutional AI Support
        </p>
      </div>

      <div className="flex items-center gap-3">
        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 relative transition border border-transparent hover:border-slate-200 dark:hover:border-slate-700"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white dark:ring-slate-900"></span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl z-50 p-3 overflow-hidden">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 dark:border-slate-800">
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                  Campus Alerts & Reminders
                </span>
                <span className="text-[10px] font-semibold text-blue-600 dark:text-blue-400">
                  {notifications.length} active
                </span>
              </div>

              <div className="space-y-2 max-h-64 overflow-y-auto">
                {notifications.length === 0 ? (
                  <p className="text-xs text-slate-400 text-center py-4">No active notifications</p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50 text-xs"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-slate-800 dark:text-slate-200">
                          {n.title}
                        </span>
                        <span className="text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase px-1.5 py-0.2 rounded bg-blue-50 dark:bg-blue-950/60">
                          {n.reminder_type}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2">
                        {n.description}
                      </p>
                      {n.due_date && (
                        <p className="text-[10px] font-medium text-amber-600 dark:text-amber-400 mt-1">
                          Due: {n.due_date}
                        </p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
