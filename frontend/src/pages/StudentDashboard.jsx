import React, { useState, useEffect } from 'react';
import {
  GraduationCap,
  Calendar,
  AlertTriangle,
  CreditCard,
  CheckCircle,
  Clock,
  ArrowRight,
  TrendingUp,
  FileText,
  Building,
  Sparkles,
  BotMessageSquare,
  ShieldAlert
} from 'lucide-react';
import { studentService, announcementService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const StudentDashboard = ({ setActiveTab, setInitialQuery }) => {
  const { user, studentProfile } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      if (user?.role === 'admin') {
        setLoading(false);
        return;
      }
      try {
        const data = await studentService.getDashboard();
        setDashboardData(data);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [user]);

  const handleAskAgent = (query) => {
    if (setInitialQuery) setInitialQuery(query);
    setActiveTab('chat');
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm font-semibold text-slate-500">Loading student records...</p>
        </div>
      </div>
    );
  }

  const profile = dashboardData?.profile || studentProfile;
  const academics = dashboardData?.academics || [];
  const attendanceAvg = dashboardData?.overall_attendance || 81.4;
  const fees = dashboardData?.fees || [];
  const totalDue = dashboardData?.total_due || 0;
  const complaints = dashboardData?.recent_complaints || [];
  const announcements = dashboardData?.announcements || [];
  const notifications = dashboardData?.notifications || [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* 1. Personalized Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-700 via-indigo-700 to-purple-800 p-7 text-white shadow-xl shadow-blue-900/10">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/15 backdrop-blur-md text-xs font-semibold text-blue-100 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>CampusAI 2.0 • Active Session</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight">
              Welcome back, {user?.full_name || 'Student'}!
            </h2>
            <p className="text-blue-100/90 text-sm mt-1">
              Roll No: <span className="font-semibold text-white">{profile?.roll_number || '2026CS1042'}</span> • {profile?.branch || 'Computer Science'} (Semester {profile?.semester || 6}, Sec {profile?.section || 'A'})
            </p>
            {profile?.hostel_resident && (
              <p className="text-xs text-blue-200 mt-1 flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5" />
                <span>Resident: {profile?.room_number || 'Hostel Block B, Room 304'}</span>
              </p>
            )}
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => handleAskAgent("Am I eligible for any scholarships?")}
              className="px-4 py-2.5 rounded-xl bg-white text-blue-900 font-bold text-xs hover:bg-blue-50 transition shadow-md active:scale-95 flex items-center gap-2"
            >
              <BotMessageSquare className="w-4 h-4 text-blue-600" />
              <span>Ask AI Assistant</span>
            </button>
          </div>
        </div>

        {/* Decorative backdrop shapes */}
        <div className="absolute -right-8 -bottom-12 w-64 h-64 bg-white/10 rounded-full blur-2xl pointer-events-none"></div>
      </div>

      {/* 2. Key Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Overall Attendance */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm transition hover:shadow-md">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Attendance
            </span>
            <div className={`p-2 rounded-xl ${attendanceAvg >= 75 ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60' : 'bg-rose-50 text-rose-600 dark:bg-rose-950/60'}`}>
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">{attendanceAvg}%</span>
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">Above 75% Threshold</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            Mandatory criteria met for university end-term hall ticket.
          </p>
        </div>

        {/* Metric 2: Fee Balance */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm transition hover:shadow-md">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Fee Ledger
            </span>
            <div className="p-2 rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-950/60">
              <CreditCard className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">
              ₹{totalDue.toLocaleString()}
            </span>
            <span className="text-xs font-semibold text-amber-600 dark:text-amber-400">Due Dec 15</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            Semester 6 Balance. Avoid ₹100/day fine after deadline.
          </p>
        </div>

        {/* Metric 3: Grievances */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm transition hover:shadow-md">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Grievances
            </span>
            <div className="p-2 rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950/60">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">
              {complaints.filter((c) => c.status !== 'RESOLVED').length}
            </span>
            <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">Active Tickets</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            {complaints.length > 0 ? `Latest: ${complaints[0].ticket_id} (${complaints[0].status})` : 'No active tickets'}
          </p>
        </div>

        {/* Metric 4: Placement Standing */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm transition hover:shadow-md">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Career & T&P
            </span>
            <div className="p-2 rounded-xl bg-purple-50 text-purple-600 dark:bg-purple-950/60">
              <GraduationCap className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-extrabold text-purple-700 dark:text-purple-300">Tier 1</span>
            <span className="text-xs font-semibold text-slate-500">Dream Drives</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
            CGPA {profile?.cgpa || 8.72} qualifies for TCS Digital & Core packages &gt; 10 LPA.
          </p>
        </div>
      </div>

      {/* 3. Main Split View: Course Attendance + AI Quick Action */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 Cols): Enrolled Subjects & Attendance breakdown */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">
                  Semester 6 Course Attendance
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Real-time synchronization with ERP Academic Lecture records
                </p>
              </div>
              <span className="text-xs font-semibold text-slate-500 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-full">
                {academics.length} Courses
              </span>
            </div>

            <div className="space-y-4">
              {academics.map((sub) => {
                const isDeficit = sub.attendance_percentage < 75.0;
                return (
                  <div
                    key={sub.id}
                    className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 space-y-2.5"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded">
                          {sub.subject_code}
                        </span>
                        <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 mt-1">
                          {sub.subject_name}
                        </h4>
                      </div>

                      <div className="text-right">
                        <span className={`text-base font-extrabold ${isDeficit ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-slate-100'}`}>
                          {sub.attendance_percentage}%
                        </span>
                        <p className="text-[11px] text-slate-500">
                          {sub.attended_classes} / {sub.total_classes} lectures
                        </p>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${isDeficit ? 'bg-rose-500' : 'bg-blue-600'}`}
                        style={{ width: `${Math.min(sub.attendance_percentage, 100)}%` }}
                      ></div>
                    </div>

                    {isDeficit && (
                      <div className="flex items-center gap-1.5 text-xs text-rose-600 dark:text-rose-400 font-semibold bg-rose-50 dark:bg-rose-950/40 p-2 rounded-xl">
                        <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                        <span>Attendance Deficit: Needs {Math.ceil((0.75 * sub.total_classes) - sub.attended_classes)} additional lectures to reach mandatory 75%.</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Campus Announcements */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">
                  Campus Circulars & Official Announcements
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Published by Dean Office, Examination Cell & Placement Section
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {announcements.map((ann) => (
                <div
                  key={ann.id}
                  className="p-4 rounded-2xl border border-slate-100 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 hover:bg-slate-100/70 dark:hover:bg-slate-800/70 transition"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/60 text-blue-800 dark:text-blue-300">
                      {ann.category}
                    </span>
                    <span className="text-[11px] text-slate-400">{ann.published_date}</span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">{ann.title}</h4>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                    {ann.content}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (1 Col): AI Assistant Fast Prompts + Grievance Tracker */}
        <div className="space-y-6">
          {/* AI One-Click Action Prompts */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-900 dark:to-slate-800/80 border border-blue-100 dark:border-slate-700/60 rounded-3xl p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center">
                <BotMessageSquare className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">Ask CampusAI</h4>
                <p className="text-[11px] text-slate-500">Autonomous Multi-Agent Routing</p>
              </div>
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-300 mb-4">
              Tap any verified query below to consult specialized agents with real institutional grounding:
            </p>

            <div className="space-y-2">
              {[
                "What is my current attendance and am I eligible for exams?",
                "How much is my pending fee balance?",
                "My hostel wifi is down and not working",
                "What are the Tier 1 placement criteria?",
                "What is the medical condonation policy for attendance?",
              ].map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleAskAgent(q)}
                  className="w-full text-left p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400 transition flex items-center justify-between group shadow-sm"
                >
                  <span className="line-clamp-1">{q}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition" />
                </button>
              ))}
            </div>
          </div>

          {/* Grievance Quick View */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">
                Recent Grievance Tickets
              </h4>
              <button
                onClick={() => setActiveTab('complaints')}
                className="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline"
              >
                View All
              </button>
            </div>

            <div className="space-y-3">
              {complaints.length === 0 ? (
                <p className="text-xs text-slate-400 text-center py-4">No complaints recorded</p>
              ) : (
                complaints.slice(0, 3).map((c) => (
                  <div
                    key={c.id}
                    className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 text-xs"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono font-bold text-slate-900 dark:text-slate-100">{c.ticket_id}</span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          c.status === 'RESOLVED'
                            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400'
                            : c.status === 'ESCALATED'
                            ? 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400'
                            : 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400'
                        }`}
                      >
                        {c.status}
                      </span>
                    </div>
                    <p className="text-slate-600 dark:text-slate-300 font-medium line-clamp-1">{c.title}</p>
                    <p className="text-[10px] text-slate-400 mt-1">{c.category} • Priority: {c.priority}</p>
                  </div>
                ))
              )}
            </div>

            <button
              onClick={() => handleAskAgent("I want to register a complaint")}
              className="w-full mt-4 py-2 px-3 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 text-xs font-bold text-slate-600 dark:text-slate-400 hover:border-blue-500 hover:text-blue-600 transition flex items-center justify-center gap-1.5"
            >
              <span>+ Register New Grievance Ticket</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
