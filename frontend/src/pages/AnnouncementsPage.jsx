import React, { useState, useEffect } from 'react';
import { Bell, Calendar, Sparkles, Filter } from 'lucide-react';
import { announcementService } from '../services/api';

export const AnnouncementsPage = () => {
  const [announcements, setAnnouncements] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnn = async () => {
      try {
        const data = await announcementService.getAnnouncements();
        setAnnouncements(data);
      } catch (err) {
        console.error('Failed to load circulars:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnn();
  }, []);

  const categories = ['ALL', 'Exams', 'Placements', 'Scholarship', 'General'];
  const filtered = filter === 'ALL' ? announcements : announcements.filter((a) => a.category.toLowerCase() === filter.toLowerCase());

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100">
            Official Campus Notices & Circulars
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Verified university releases on examinations, placement drives, and government scholarship updates.
          </p>
        </div>

        {/* Filter Chips */}
        <div className="flex flex-wrap gap-1.5 self-start">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setFilter(c)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                filter === c
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                  : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((ann) => (
          <div
            key={ann.id}
            className={`p-6 rounded-3xl bg-white dark:bg-slate-900 border transition hover:shadow-md space-y-3 ${
              ann.is_urgent
                ? 'border-rose-200 dark:border-rose-900/60 shadow-sm shadow-rose-500/5'
                : 'border-slate-200 dark:border-slate-800 shadow-sm'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className={`text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full ${
                ann.is_urgent
                  ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                  : 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
              }`}>
                {ann.category} {ann.is_urgent && '• URGENT'}
              </span>
              <span className="text-xs text-slate-400 flex items-center gap-1 font-medium">
                <Calendar className="w-3.5 h-3.5" />
                {ann.published_date}
              </span>
            </div>

            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 leading-snug">
              {ann.title}
            </h3>

            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
              {ann.content}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
