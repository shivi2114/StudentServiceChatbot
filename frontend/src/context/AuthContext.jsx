import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('campusai_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [studentProfile, setStudentProfile] = useState(() => {
    const saved = localStorage.getItem('campusai_profile');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('campusai_token'));
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('campusai_theme') === 'dark';
  });

  // Apply dark mode class to html element
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('campusai_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('campusai_theme', 'light');
    }
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode((prev) => !prev);

  // Validate session on load
  useEffect(() => {
    const handleAuthExpired = () => {
      logout();
    };
    window.addEventListener('campusai:auth-expired', handleAuthExpired);

    const verifyToken = async () => {
      const storedToken = localStorage.getItem('campusai_token');
      if (!storedToken) {
        setLoading(false);
        return;
      }
      try {
        const data = await authService.getMe();
        setUser(data.user);
        setStudentProfile(data.student_profile);
        localStorage.setItem('campusai_user', JSON.stringify(data.user));
        if (data.student_profile) {
          localStorage.setItem('campusai_profile', JSON.stringify(data.student_profile));
        }
      } catch (err) {
        console.error('Session validation error:', err);
        logout();
      } finally {
        setLoading(false);
      }
    };
    verifyToken();

    return () => {
      window.removeEventListener('campusai:auth-expired', handleAuthExpired);
    };
  }, []);

  const login = async (email, password) => {
    const res = await authService.login(email, password);
    setToken(res.access_token);
    localStorage.setItem('campusai_token', res.access_token);

    const meData = await authService.getMe();
    setUser(meData.user);
    setStudentProfile(meData.student_profile);

    localStorage.setItem('campusai_user', JSON.stringify(meData.user));
    if (meData.student_profile) {
      localStorage.setItem('campusai_profile', JSON.stringify(meData.student_profile));
    }
    return meData.user;
  };

  const logout = () => {
    setUser(null);
    setStudentProfile(null);
    setToken(null);
    localStorage.removeItem('campusai_token');
    localStorage.removeItem('campusai_user');
    localStorage.removeItem('campusai_profile');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        studentProfile,
        token,
        role: user?.role || 'student',
        isAuthenticated: !!token && !!user,
        loading,
        darkMode,
        toggleDarkMode,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
