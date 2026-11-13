import React, { useState, useEffect } from 'react';
import { AlertCircle, Plus, Search, ShieldAlert, CheckCircle, Clock, ArrowRight } from 'lucide-react';
import { complaintService } from '../services/api';

export const ComplaintsPage = ({ setActiveTab, setInitialQuery }) => {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTicket, setSearchTicket] = useState('');
  const [searchedRecord, setSearchedRecord] = useState(null);
  const [searchError, setSearchError] = useState('');

  // New complaint form state
  const [showModal, setShowModal] = useState(false);
  const [category, setCategory] = useState('Hostel');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('MEDIUM');
  const [submitting, setSubmitting] = useState(false);

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const data = await complaintService.getComplaints();
      setComplaints(data);
    } catch (err) {
      console.error('Failed to load complaints:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTicket.trim()) return;
    setSearchError('');
    setSearchedRecord(null);
    try {
      const res = await complaintService.getComplaint(searchTicket.trim());
      setSearchedRecord(res);
    } catch (err) {
      setSearchError(`Ticket '${searchTicket}' not found in registry.`);
    }
  };

  const handleCreateComplaint = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await complaintService.createComplaint({ category, title, description, priority });
      setShowModal(false);
      setTitle('');
      setDescription('');
      fetchComplaints();
    } catch (err) {
      alert('Failed to submit complaint: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const handleEscalate = async (ticketId) => {
    const reason = prompt('Please provide the reason for escalating this ticket:');
    if (!reason) return;
    try {
      await complaintService.escalateComplaint(ticketId, reason);
      alert(`Ticket ${ticketId} escalated successfully!`);
      fetchComplaints();
    } catch (err) {
      alert('Escalation failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100">
            Student Grievance Redressal & Support
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Registered complaints are tracked under official university grievance bylaws with Dean oversight.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-md shadow-blue-600/25 transition self-start"
        >
          <Plus className="w-4 h-4" />
          <span>File New Grievance</span>
        </button>
      </div>

      {/* Ticket Lookup Card */}
      <div className="p-5 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
        <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100 mb-2">Track Specific Ticket ID</h4>
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="e.g. CMP-2026-1001"
            value={searchTicket}
            onChange={(e) => setSearchTicket(e.target.value)}
            className="flex-1 py-2 px-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 text-xs font-bold hover:opacity-90 transition flex items-center gap-1.5"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Search</span>
          </button>
        </form>

        {searchError && (
          <p className="text-xs font-semibold text-rose-500 mt-2">{searchError}</p>
        )}

        {searchedRecord && (
          <div className="mt-3 p-3.5 rounded-2xl bg-blue-50/70 dark:bg-slate-800/80 border border-blue-200 dark:border-slate-700 text-xs">
            <div className="flex items-center justify-between mb-1">
              <span className="font-bold text-blue-900 dark:text-blue-300 font-mono text-sm">
                {searchedRecord.ticket_id}
              </span>
              <span className="font-bold uppercase text-[10px] px-2 py-0.5 rounded bg-blue-600 text-white">
                {searchedRecord.status}
              </span>
            </div>
            <p className="font-bold text-slate-800 dark:text-slate-200">{searchedRecord.title}</p>
            <p className="text-slate-600 dark:text-slate-400 mt-1">{searchedRecord.description}</p>
            {searchedRecord.status !== 'RESOLVED' && (
              <button
                onClick={() => handleEscalate(searchedRecord.ticket_id)}
                className="mt-2 text-[11px] font-bold text-rose-600 hover:underline"
              >
                🚨 Escalate this ticket to Dean & Proctorial Board
              </button>
            )}
          </div>
        )}
      </div>

      {/* Complaints List */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-3">
        <h3 className="font-bold text-base text-slate-900 dark:text-slate-100 mb-2">My Registered Tickets</h3>

        {complaints.length === 0 ? (
          <p className="text-xs text-slate-400 text-center py-8">No complaints registered on your profile</p>
        ) : (
          complaints.map((c) => (
            <div
              key={c.id}
              className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
            >
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{c.ticket_id}</span>
                  <span className="font-semibold text-slate-500">• {c.category}</span>
                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                    c.priority === 'CRITICAL' || c.priority === 'HIGH' ? 'bg-rose-100 text-rose-700' : 'bg-slate-200 text-slate-700'
                  }`}>
                    {c.priority}
                  </span>
                </div>
                <h4 className="font-bold text-slate-900 dark:text-slate-100">{c.title}</h4>
                <p className="text-slate-500 mt-0.5">{c.description}</p>
                {c.escalation_reason && (
                  <p className="text-[11px] text-purple-600 dark:text-purple-400 mt-1 font-medium">
                    Note: {c.escalation_reason}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span
                  className={`text-[11px] font-bold px-3 py-1 rounded-full ${
                    c.status === 'RESOLVED'
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                      : c.status === 'ESCALATED'
                      ? 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300'
                      : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                  }`}
                >
                  {c.status}
                </span>

                {c.status !== 'RESOLVED' && c.status !== 'ESCALATED' && (
                  <button
                    onClick={() => handleEscalate(c.ticket_id)}
                    className="px-2.5 py-1 rounded-lg border border-rose-300 text-rose-600 hover:bg-rose-50 text-[11px] font-bold transition"
                  >
                    Escalate
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal for Filing Complaint */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-lg shadow-2xl">
            <h3 className="font-extrabold text-lg text-slate-900 dark:text-slate-100 mb-1">
              File Official Student Complaint
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Your grievance will be recorded in the PostgreSQL database and assigned to the relevant department head.
            </p>

            <form onSubmit={handleCreateComplaint} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none"
                >
                  <option>Hostel</option>
                  <option>Wi-Fi</option>
                  <option>Hostel Mess</option>
                  <option>Academic</option>
                  <option>Accounts</option>
                  <option>General</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Wi-Fi dropping in Hostel Block B"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Description</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Provide exact details, room number, or affected course..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                ></textarea>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none"
                >
                  <option>LOW</option>
                  <option>MEDIUM</option>
                  <option>HIGH</option>
                  <option>CRITICAL</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md transition disabled:opacity-50"
                >
                  {submitting ? 'Filing...' : 'Submit Grievance'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
