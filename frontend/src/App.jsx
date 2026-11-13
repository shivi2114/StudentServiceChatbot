import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { LoginPage } from './pages/LoginPage';
import { StudentDashboard } from './pages/StudentDashboard';
import { ChatPage } from './pages/ChatPage';
import { ComplaintsPage } from './pages/ComplaintsPage';
import { AnnouncementsPage } from './pages/AnnouncementsPage';
import { AdminDashboard } from './pages/AdminDashboard';

const MainApp = () => {
  const { isAuthenticated, loading, role } = useAuth();
  const [activeTab, setActiveTab] = useState(() => (role === 'admin' ? 'admin' : 'dashboard'));
  const [language, setLanguage] = useState('en');
  const [initialQuery, setInitialQuery] = useState(null);

  React.useEffect(() => {
    if (role === 'admin' && activeTab === 'dashboard') {
      setActiveTab('admin');
    } else if (role === 'student' && activeTab === 'admin') {
      setActiveTab('dashboard');
    }
  }, [role]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm font-semibold text-slate-500">Initializing CampusAI Platform...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden font-['Plus_Jakarta_Sans',sans-serif]">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header
          activeTab={activeTab}
        />

        <main className="flex-1 overflow-y-auto">
          {activeTab === 'dashboard' && (
            <StudentDashboard
              setActiveTab={setActiveTab}
              setInitialQuery={setInitialQuery}
            />
          )}

          {activeTab === 'chat' && (
            <ChatPage
              initialQuery={initialQuery}
              language={language}
              setLanguage={setLanguage}
            />
          )}

          {activeTab === 'complaints' && (
            <ComplaintsPage
              setActiveTab={setActiveTab}
              setInitialQuery={setInitialQuery}
            />
          )}

          {activeTab === 'announcements' && <AnnouncementsPage />}

          {activeTab === 'admin' && <AdminDashboard />}
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
