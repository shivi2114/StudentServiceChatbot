import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token from localStorage if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('campusai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url?.includes('/auth/login');
    if (error.response && error.response.status === 401 && !isLoginRequest) {
      localStorage.removeItem('campusai_token');
      localStorage.removeItem('campusai_user');
      localStorage.removeItem('campusai_profile');
      window.dispatchEvent(new Event('campusai:auth-expired'));
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    return res.data;
  },
  getMe: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  },
};

export const studentService = {
  getDashboard: async () => {
    const res = await api.get('/students/dashboard');
    return res.data;
  },
  getAcademics: async () => {
    const res = await api.get('/students/academics');
    return res.data;
  },
  getFees: async () => {
    const res = await api.get('/students/fees');
    return res.data;
  },
  getNotifications: async () => {
    const res = await api.get('/students/notifications');
    return res.data;
  },
};

export const chatService = {
  sendMessage: async (message, sessionId = null, language = 'en', confirmedAction = null) => {
    const res = await api.post('/chat', {
      message,
      session_id: sessionId,
      language,
      confirmed_action: confirmedAction,
    });
    return res.data;
  },
  getSessions: async () => {
    const res = await api.get('/chat/sessions');
    return res.data;
  },
  getSession: async (sessionId) => {
    const res = await api.get(`/chat/sessions/${sessionId}`);
    return res.data;
  },
  deleteSession: async (sessionId) => {
    const res = await api.delete(`/chat/sessions/${sessionId}`);
    return res.data;
  },
};

export const complaintService = {
  getComplaints: async () => {
    const res = await api.get('/complaints');
    return res.data;
  },
  getComplaint: async (ticketId) => {
    const res = await api.get(`/complaints/${ticketId}`);
    return res.data;
  },
  createComplaint: async (payload) => {
    const res = await api.post('/complaints', payload);
    return res.data;
  },
  escalateComplaint: async (ticketId, reason) => {
    const res = await api.post(`/complaints/${ticketId}/escalate`, { reason });
    return res.data;
  },
  updateComplaintStatus: async (ticketId, payload) => {
    const res = await api.patch(`/complaints/${ticketId}`, payload);
    return res.data;
  },
};

export const announcementService = {
  getAnnouncements: async () => {
    const res = await api.get('/announcements');
    return res.data;
  },
};

export const adminService = {
  getAnalytics: async () => {
    const res = await api.get('/admin/analytics');
    return res.data;
  },
  getDocuments: async () => {
    const res = await api.get('/admin/documents');
    return res.data;
  },
  uploadDocument: async (formData) => {
    const res = await api.post('/admin/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
  getQueryLogs: async () => {
    const res = await api.get('/admin/queries');
    return res.data;
  },
};

export default api;
