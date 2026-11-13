import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  BotMessageSquare,
  Sparkles,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  FileText,
  Building,
  HelpCircle,
  Plus,
  Trash2,
  Globe,
  Clock,
  ShieldCheck,
  Check,
  X
} from 'lucide-react';
import { chatService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const ChatPage = ({ initialQuery = null, language = 'en', setLanguage }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [agentStatus, setAgentStatus] = useState(null);
  const [expandedCitations, setExpandedCitations] = useState({});

  const messagesEndRef = useRef(null);

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load chat sessions on mount
  useEffect(() => {
    const loadSessions = async () => {
      try {
        const data = await chatService.getSessions();
        setSessions(data);
      } catch (err) {
        console.error('Failed to load sessions:', err);
      }
    };
    loadSessions();
  }, []);

  // Handle initial query if passed from dashboard
  useEffect(() => {
    if (initialQuery && initialQuery.trim()) {
      handleSendMessage(initialQuery.trim());
    }
  }, [initialQuery]);

  const handleSendMessage = async (textToSend = null, confirmedAction = null) => {
    const text = (textToSend || inputText).trim();
    if (!text && !confirmedAction) return;

    if (!textToSend) setInputText('');

    // Add user message to UI
    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: text || 'Confirmed Action',
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setAgentStatus('Orchestrator Agent routing query...');

    try {
      const resp = await chatService.sendMessage(text, activeSessionId, language, confirmedAction);
      setActiveSessionId(resp.session_id);

      // Assistant response
      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: resp.answer,
        agent_name: resp.agent_name,
        source: resp.source,
        citations: resp.citations || [],
        action_required: resp.action_required,
        office_referral: resp.office_referral,
        follow_up_suggestions: resp.follow_up_suggestions || [],
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Refresh session list
      const updatedSessions = await chatService.getSessions();
      setSessions(updatedSessions);
    } catch (err) {
      console.error('Chat error:', err);
      const errMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'I could not connect with the campus agent network right now. Please verify your connection or consult the Student Helpdesk.',
        agent_name: 'CampusAI Fallback',
        source: 'error',
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
      setAgentStatus(null);
    }
  };

  const handleConfirmAction = (action) => {
    handleSendMessage(`Confirm ${action.action_title}`, action);
  };

  const startNewConversation = () => {
    setActiveSessionId(null);
    setMessages([]);
  };

  const loadPastSession = async (sessionId) => {
    try {
      setLoading(true);
      const session = await chatService.getSession(sessionId);
      setActiveSessionId(session.session_id);

      // Parse metadata for each message
      const formatted = (session.messages || []).map((m) => {
        let meta = {};
        if (m.metadata_json) {
          try {
            meta = JSON.parse(m.metadata_json);
          } catch (e) {}
        }
        return {
          id: m.id,
          role: m.role,
          content: m.content,
          agent_name: m.agent_name,
          source: m.source,
          citations: meta.citations || [],
          action_required: meta.action_required,
          office_referral: meta.office_referral,
          created_at: m.created_at,
        };
      });
      setMessages(formatted);
    } catch (err) {
      console.error('Failed to load past session:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleCitation = (msgId) => {
    setExpandedCitations((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-slate-50 dark:bg-slate-950 overflow-hidden">
      {/* Session History Sidebar */}
      <div className="w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col shrink-0 hidden md:flex">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800">
          <button
            onClick={startNewConversation}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 active:scale-[0.99] transition"
          >
            <Plus className="w-4 h-4" />
            <span>New Campus Inquiry</span>
          </button>
        </div>

        <div className="flex-1 p-3 overflow-y-auto space-y-1">
          <p className="text-[11px] font-bold text-slate-400 dark:text-slate-500 px-2 py-1 uppercase tracking-wider">
            Past Conversations
          </p>
          {sessions.length === 0 ? (
            <p className="text-xs text-slate-400 p-2 text-center">No past chats yet</p>
          ) : (
            sessions.map((s) => {
              const isSelected = activeSessionId === s.session_id;
              return (
                <button
                  key={s.session_id}
                  onClick={() => loadPastSession(s.session_id)}
                  className={`w-full text-left p-2.5 rounded-xl text-xs font-semibold truncate transition ${
                    isSelected
                      ? 'bg-blue-50 dark:bg-slate-800 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-slate-700 font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60'
                  }`}
                >
                  <p className="truncate">{s.title || 'Inquiry'}</p>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-slate-50/50 dark:bg-slate-950">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 max-w-4xl mx-auto w-full">
          {messages.length === 0 ? (
            <div className="py-12 flex flex-col items-center text-center max-w-md mx-auto space-y-4">
              <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center text-white shadow-xl shadow-blue-500/20">
                <BotMessageSquare className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                  How can CampusAI assist you today?
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Connected to Academic, Fee, Complaint, Scholarship, and Placement agents with real database operations.
                </p>
              </div>

              {/* Starter Prompt Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full pt-4">
                {[
                  { title: "Academic & Attendance", prompt: "What is the mandatory attendance requirement?" },
                  { title: "Fee & ERP Balance", prompt: "How much fee do I owe for semester 6?" },
                  { title: "Lodge Grievance", prompt: "The hostel wifi is down and not working in my room" },
                  { title: "Scholarship & MCM", prompt: "Am I eligible for any scholarships with my CGPA?" },
                ].map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(item.prompt)}
                    className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-left hover:border-blue-500 hover:shadow-md transition group shadow-sm"
                  >
                    <p className="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-blue-600">
                      {item.title}
                    </p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-1">
                      {item.prompt}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => {
              const isUser = msg.role === 'user';
              return (
                <div key={msg.id} className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}>
                  {!isUser && (
                    <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0 mt-0.5 shadow-sm">
                      <BotMessageSquare className="w-4 h-4" />
                    </div>
                  )}

                  <div className={`max-w-[85%] sm:max-w-[78%] space-y-2`}>
                    {/* Message Bubble */}
                    <div
                      className={`p-4 rounded-2xl text-sm leading-relaxed ${
                        isUser
                          ? 'bg-blue-600 text-white rounded-tr-none shadow-md shadow-blue-600/20'
                          : 'bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 border border-slate-200/80 dark:border-slate-800 rounded-tl-none shadow-sm'
                      }`}
                    >
                      {/* Agent Badge (if assistant) */}
                      {!isUser && msg.agent_name && (
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-100 dark:border-slate-800">
                          <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800/60">
                            {msg.agent_name}
                          </span>
                          {msg.source && (
                            <span className="text-[10px] text-slate-400 font-medium">
                              via {msg.source}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Content with Markdown-style bold rendering */}
                      <div className="whitespace-pre-wrap text-sm leading-relaxed">
                        {msg.content}
                      </div>

                      {/* Human-in-the-loop Action Approval Card */}
                      {msg.action_required && msg.action_required.requires_approval && (
                        <div className="mt-3.5 p-3.5 rounded-xl bg-amber-50/80 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-slate-900 dark:text-slate-100">
                          <div className="flex items-center gap-1.5 text-xs font-bold text-amber-800 dark:text-amber-300 mb-1">
                            <AlertTriangle className="w-4 h-4 text-amber-600" />
                            <span>Confirmation Required</span>
                          </div>
                          <p className="text-xs font-semibold">{msg.action_required.action_title}</p>
                          <div className="text-[11px] text-slate-600 dark:text-slate-400 mt-1 space-y-0.5">
                            {Object.entries(msg.action_required.details || {}).map(([k, v]) => (
                              <p key={k}><strong className="capitalize">{k}:</strong> {String(v)}</p>
                            ))}
                          </div>

                          <div className="flex items-center gap-2 mt-3">
                            <button
                              onClick={() => handleConfirmAction(msg.action_required)}
                              className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-sm transition"
                            >
                              <Check className="w-3.5 h-3.5" />
                              <span>Confirm & Authorize</span>
                            </button>
                            <button
                              onClick={() => handleSendMessage("Cancel this action")}
                              className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 text-xs font-medium transition"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Campus Office Referral */}
                      {msg.office_referral && (
                        <div className="mt-3 p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300 flex items-start gap-2">
                          <Building className="w-4 h-4 text-blue-600 dark:text-blue-400 mt-0.5 shrink-0" />
                          <div>
                            <span className="font-bold text-blue-900 dark:text-blue-300">
                              {msg.office_referral.office}
                            </span>
                            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                              {msg.office_referral.contact}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Expandable Citations */}
                    {!isUser && msg.citations && msg.citations.length > 0 && (
                      <div>
                        <button
                          onClick={() => toggleCitation(msg.id)}
                          className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 px-2.5 py-1 rounded-lg hover:bg-emerald-100 transition"
                        >
                          <FileText className="w-3 h-3" />
                          <span>{msg.citations.length} Grounded Document Sources</span>
                          {expandedCitations[msg.id] ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : (
                            <ChevronDown className="w-3 h-3" />
                          )}
                        </button>

                        {expandedCitations[msg.id] && (
                          <div className="mt-2 space-y-2 pl-2 border-l-2 border-emerald-500">
                            {msg.citations.map((c, i) => (
                              <div
                                key={i}
                                className="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[11px]"
                              >
                                <div className="flex items-center justify-between text-slate-500 font-bold mb-1">
                                  <span>{c.document_title} (Page {c.page_number})</span>
                                  {c.relevance_score && (
                                    <span className="text-emerald-600 font-semibold">
                                      Match: {Math.round(c.relevance_score * 100)}%
                                    </span>
                                  )}
                                </div>
                                <p className="text-slate-600 dark:text-slate-300 italic">
                                  "{c.snippet}"
                                </p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Follow-up suggestions */}
                    {!isUser && msg.follow_up_suggestions && msg.follow_up_suggestions.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {msg.follow_up_suggestions.map((sug, i) => (
                          <button
                            key={i}
                            onClick={() => handleSendMessage(sug)}
                            className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-blue-50 hover:text-blue-700 dark:hover:bg-slate-700 transition border border-slate-200 dark:border-slate-700"
                          >
                            {sug}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}

          {/* Agent Activity Indicator */}
          {loading && (
            <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 w-fit shadow-sm animate-pulse">
              <div className="w-5 h-5 rounded-lg bg-blue-600 text-white flex items-center justify-center text-[10px] font-bold">
                <Sparkles className="w-3 h-3 animate-spin" />
              </div>
              <span className="font-semibold">{agentStatus || 'Specialized Agents collaborating...'}</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-t border-slate-200 dark:border-slate-800">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="max-w-4xl mx-auto flex items-center gap-2.5"
          >
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask about attendance, exam dates, fee ledger, complaint tickets, or scholarships..."
              disabled={loading}
              className="flex-1 py-3 px-4 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-500 transition shadow-inner"
            />

            <button
              type="submit"
              disabled={loading || !inputText.trim()}
              className="p-3 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold transition shadow-md shadow-blue-600/30 active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
          <p className="text-center text-[11px] text-slate-400 mt-2">
            CampusAI retrieves responses strictly from verified university documents and authorized records.
          </p>
        </div>
      </div>
    </div>
  );
};
