import React, { useState, useEffect } from 'react';
import {
  Shield,
  Upload,
  FileText,
  AlertCircle,
  Users,
  CheckCircle,
  Clock,
  TrendingUp,
  Search,
  RefreshCw,
  Plus,
  BotMessageSquare,
  Sparkles
} from 'lucide-react';
import { adminService, complaintService } from '../services/api';

export const AdminDashboard = () => {
  const [activeAdminTab, setActiveAdminTab] = useState('analytics');
  const [analytics, setAnalytics] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [complaints, setComplaints] = useState([]);
  const [queryLogs, setQueryLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Upload state
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState('Regulations');
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [stats, docs, cmps, logs] = await Promise.all([
        adminService.getAnalytics(),
        adminService.getDocuments(),
        complaintService.getComplaints(),
        adminService.getQueryLogs(),
      ]);
      setAnalytics(stats);
      setDocuments(docs);
      setComplaints(cmps);
      setQueryLogs(logs);
    } catch (err) {
      console.error('Failed to load admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDocumentUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile || !uploadTitle) return;

    setUploading(true);
    setUploadMsg('');
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('title', uploadTitle);
    formData.append('category', uploadCategory);

    try {
      const res = await adminService.uploadDocument(formData);
      setUploadMsg(`✅ Document uploaded: ${res.chunks_indexed} semantic chunks indexed into ChromaDB!`);
      setUploadTitle('');
      setUploadFile(null);
      loadData();
    } catch (err) {
      setUploadMsg(`❌ Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleUpdateStatus = async (ticketId, newStatus) => {
    try {
      await complaintService.updateComplaintStatus(ticketId, { status: newStatus });
      loadData();
    } catch (err) {
      alert('Failed to update ticket status');
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm font-semibold text-slate-500">Loading university administration metrics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-100 dark:bg-purple-950/60 text-xs font-bold text-purple-800 dark:text-purple-300 mb-1">
            <Shield className="w-3.5 h-3.5" />
            <span>Administrator Control Console</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100">
            University Management & Multi-Agent Operations
          </h2>
        </div>

        <button
          onClick={loadData}
          className="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5 transition self-start"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Records</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200 dark:border-slate-800">
        {[
          { id: 'analytics', label: 'Overview & Performance' },
          { id: 'documents', label: 'Document & RAG Knowledge Base' },
          { id: 'complaints', label: 'Grievance Management' },
          { id: 'queries', label: 'Agent Query Logs' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveAdminTab(tab.id)}
            className={`pb-3 px-3 text-sm font-bold transition border-b-2 ${
              activeAdminTab === tab.id
                ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Analytics */}
      {activeAdminTab === 'analytics' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Enrolled Students</span>
              <p className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 mt-2">{analytics?.total_students}</p>
              <p className="text-[11px] text-emerald-600 font-semibold mt-1">Verified ERP Profiles</p>
            </div>

            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Document Chunks in RAG</span>
              <p className="text-3xl font-extrabold text-blue-600 dark:text-blue-400 mt-2">{analytics?.chunks_indexed}</p>
              <p className="text-[11px] text-slate-500 mt-1">Across {analytics?.documents_indexed} Official PDFs</p>
            </div>

            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Student Inquiries Handled</span>
              <p className="text-3xl font-extrabold text-purple-600 dark:text-purple-400 mt-2">{analytics?.total_queries}</p>
              <p className="text-[11px] text-purple-500 font-semibold mt-1">LangGraph Multi-Agent Routings</p>
            </div>

            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Grievances Triage</span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-3xl font-extrabold text-amber-600">{analytics?.pending_complaints}</span>
                <span className="text-xs text-slate-500">pending ({analytics?.escalated_complaints} escalated)</span>
              </div>
              <p className="text-[11px] text-emerald-600 font-semibold mt-1">{analytics?.resolved_complaints} Resolved</p>
            </div>
          </div>

          {/* Agent Distribution Breakdown */}
          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <h3 className="font-bold text-base text-slate-900 dark:text-slate-100 mb-1">
              LangGraph Agent Delegation Distribution
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              Breakdown of autonomous task routing across specialized campus agents
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {Object.entries(analytics?.agent_distribution || {}).map(([agent, count]) => (
                <div key={agent} className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 text-center">
                  <p className="text-xs font-bold text-slate-700 dark:text-slate-300 truncate">{agent}</p>
                  <p className="text-xl font-extrabold text-blue-600 dark:text-blue-400 mt-1">{count}</p>
                  <p className="text-[10px] text-slate-400">delegations</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Document Management & Upload */}
      {activeAdminTab === 'documents' && (
        <div className="space-y-6">
          {/* Upload Card */}
          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <h3 className="font-bold text-base text-slate-900 dark:text-slate-100 mb-1">
              Upload Official College Notices & Handbooks
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              Files are automatically chunked, embedded, and indexed into the ChromaDB vector store.
            </p>

            {uploadMsg && (
              <div className="mb-4 p-3 rounded-xl bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 text-xs font-medium text-blue-800 dark:text-blue-300">
                {uploadMsg}
              </div>
            )}

            <form onSubmit={handleDocumentUpload} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">Document Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Hostel Guidelines 2026"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  className="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">Category</label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none"
                >
                  <option>Regulations</option>
                  <option>Fees</option>
                  <option>Placements</option>
                  <option>Hostel</option>
                  <option>Scholarships</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">Choose File (.pdf, .txt, .md)</label>
                <input
                  type="file"
                  required
                  accept=".pdf,.txt,.md"
                  onChange={(e) => setUploadFile(e.target.files[0])}
                  className="w-full py-1.5 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs file:mr-2 file:py-1 file:px-2 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white"
                />
              </div>

              <div className="sm:col-span-3 pt-2">
                <button
                  type="submit"
                  disabled={uploading}
                  className="py-2.5 px-5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-blue-600/25 transition disabled:opacity-50"
                >
                  <Upload className="w-4 h-4" />
                  <span>{uploading ? 'Extracting & Indexing...' : 'Index into ChromaDB RAG'}</span>
                </button>
              </div>
            </form>
          </div>

          {/* Document List */}
          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100 mb-3">
              Currently Indexed Knowledge Documents
            </h4>

            <div className="space-y-2">
              {documents.map((doc, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="font-bold text-slate-900 dark:text-slate-100">{doc.title}</p>
                      <p className="text-[11px] text-slate-500">{doc.filename} • {doc.size_kb} KB</p>
                    </div>
                  </div>

                  <span className="font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
                    {doc.chunk_count} Chunks Indexed
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Complaint Triage */}
      {activeAdminTab === 'complaints' && (
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">
            Student Grievance Triage Registry
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800 text-slate-500 font-bold uppercase tracking-wider">
                <tr>
                  <th className="p-3">Ticket ID</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Title & Summary</th>
                  <th className="p-3">Priority</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {complaints.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                    <td className="p-3 font-mono font-bold text-blue-600">{c.ticket_id}</td>
                    <td className="p-3 font-medium">{c.category}</td>
                    <td className="p-3">
                      <p className="font-bold text-slate-900 dark:text-slate-100">{c.title}</p>
                      <p className="text-[11px] text-slate-500 line-clamp-1">{c.description}</p>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded font-bold uppercase text-[10px] ${
                        c.priority === 'CRITICAL' || c.priority === 'HIGH' ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-700'
                      }`}>
                        {c.priority}
                      </span>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                        c.status === 'RESOLVED' ? 'bg-emerald-100 text-emerald-800' : c.status === 'ESCALATED' ? 'bg-purple-100 text-purple-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-3 text-right space-x-1">
                      {c.status !== 'RESOLVED' && (
                        <button
                          onClick={() => handleUpdateStatus(c.ticket_id, 'RESOLVED')}
                          className="px-2.5 py-1 rounded bg-emerald-600 text-white font-bold text-[10px] hover:bg-emerald-700 transition"
                        >
                          Resolve
                        </button>
                      )}
                      {c.status === 'PENDING' && (
                        <button
                          onClick={() => handleUpdateStatus(c.ticket_id, 'IN_REVIEW')}
                          className="px-2.5 py-1 rounded bg-blue-600 text-white font-bold text-[10px] hover:bg-blue-700 transition"
                        >
                          Mark Review
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Query Logs */}
      {activeAdminTab === 'queries' && (
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">
            Live Agent Execution & Student Query Logs
          </h3>

          <div className="space-y-2">
            {queryLogs.map((log, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 text-xs flex items-center justify-between"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded">
                      {log.agent_name}
                    </span>
                    <span className="text-[10px] text-slate-400">via {log.source}</span>
                    <span className="text-[10px] text-slate-400">• {log.timestamp}</span>
                  </div>
                  <p className="text-slate-700 dark:text-slate-300">{log.content_preview}...</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
