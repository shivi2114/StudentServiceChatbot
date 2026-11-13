import streamlit as st

try:
    from chatbot import get_detailed_response, SERVICE_DIRECTORY
except ImportError:
    from chatbot import get_response, SERVICE_DIRECTORY

    def get_detailed_response(question, history=None):
        return {
            "answer": get_response(question, history=history),
            "source": "verified_kb",
            "office": None,
            "contact": None
        }

from config import has_groq_api_key

# ==============================================================================
# Page Configuration
# ==============================================================================

st.set_page_config(
    page_title="Student Support • Campus Services Chatbot",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# Custom CSS: Calm, Modern, Accessible Collegiate Design
# ==============================================================================

st.markdown(
    """
    <style>
    /* Reset & Base Typography */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #0f172a;
        background-color: #fafbfc;
    }

    /* Container constraint with proper top and bottom clearance */
    .block-container {
        max-width: 820px !important;
        padding-top: 4.5rem !important;
        padding-bottom: 9.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Streamlit top header adjustment */
    header[data-testid="stHeader"] {
        background-color: rgba(250, 251, 252, 0.85) !important;
        backdrop-filter: blur(8px);
    }

    /* Streamlit bottom chat input bar background */
    div[data-testid="stBottom"] {
        background-color: #fafbfc !important;
        padding-bottom: 1rem !important;
    }

    /* Header styling */
    .brand-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        background-color: #eff6ff;
        color: #1e40af;
        border: 1px solid #dbeafe;
        border-radius: 4px;
        padding: 0.15rem 0.45rem;
        margin-bottom: 0.35rem;
    }
    .brand-heading {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        line-height: 1.2;
    }
    .brand-caption {
        font-size: 0.86rem;
        color: #64748b;
        margin: 0.2rem 0 0 0;
    }

    /* Welcome / Orientation Notice */
    .welcome-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.15rem 1.25rem;
        margin-top: 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .welcome-title {
        font-size: 1rem;
        font-weight: 600;
        color: #0f172a;
        margin: 0 0 0.25rem 0;
    }
    .welcome-text {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.5;
        margin: 0;
    }

    /* Example Questions Section */
    .examples-header {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin: 1rem 0 0.5rem 0;
    }

    /* Compact, Touch-Friendly Button Styling */
    div[data-testid="stButton"] > button,
    div[data-testid="stPopover"] > button {
        border-radius: 6px;
        border: 1px solid #cbd5e1;
        background-color: #ffffff;
        color: #1e293b;
        font-size: 0.85rem;
        font-weight: 500;
        text-align: left;
        padding: 0.45rem 0.75rem;
        transition: all 0.15s ease-in-out;
        width: 100%;
        margin-bottom: 0.25rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    div[data-testid="stButton"] > button:hover,
    div[data-testid="stPopover"] > button:hover {
        border-color: #2563eb;
        background-color: #eff6ff;
        color: #1d4ed8;
    }
    div[data-testid="stButton"] > button:focus-visible,
    div[data-testid="stPopover"] > button:focus-visible {
        outline: 2px solid #2563eb;
        outline-offset: 2px;
    }

    /* Chat Messages */
    div[data-testid="stChatMessage"] {
        padding: 0.5rem 0;
        background-color: transparent !important;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #f1f5f9 !important;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.75rem;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0;
        border-left: 3px solid #1e40af;
        border-radius: 8px;
        padding: 0.95rem 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }

    /* Verified Source Pill */
    .verified-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        color: #166534;
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 4px;
        padding: 0.15rem 0.45rem;
        margin-bottom: 0.5rem;
    }

    /* Designated Office Card inside assistant response */
    .office-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.65rem 0.85rem;
        margin-top: 0.75rem;
        font-size: 0.84rem;
        color: #334155;
    }
    .office-card-header {
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Referral Card for unanswered inquiries */
    .referral-card {
        background-color: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 6px;
        padding: 0.7rem 0.9rem;
        margin-top: 0.75rem;
        font-size: 0.84rem;
        color: #92400e;
    }

    /* Support Popover Container */
    .directory-item {
        padding: 0.45rem 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.85rem;
    }
    .directory-name {
        font-weight: 600;
        color: #0f172a;
    }
    .directory-details {
        color: #64748b;
        font-size: 0.8rem;
    }

    /* Subtle Footer */
    .site-footer {
        text-align: center;
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #e2e8f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# State Initialization
# ==============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# ==============================================================================
# Core Interaction Handlers
# ==============================================================================

def process_query(user_text: str):
    """Run user query through chatbot pipeline and update conversation state."""
    cleaned = user_text.strip()
    if not cleaned:
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": cleaned})

    # Prepare conversational history for multi-turn reasoning
    history_turns = []
    for msg in st.session_state.messages[:-1]:
        history_turns.append({"role": msg["role"], "content": msg["content"]})

    # Query chatbot
    detail = get_detailed_response(cleaned, history=history_turns)

    # Add structured assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": detail["answer"],
        "source": detail.get("source"),
        "office": detail.get("office"),
        "contact": detail.get("contact")
    })


def select_example(question_text: str):
    """Trigger selection of an example question."""
    st.session_state.pending_query = question_text


def clear_conversation():
    """Reset chat state."""
    st.session_state.messages = []
    st.session_state.pending_query = None

# ==============================================================================
# Header Bar: Identity & Aligned Quick Actions
# ==============================================================================

col_brand, col_reset, col_offices = st.columns([3.8, 1.1, 1.1], vertical_alignment="bottom")

with col_brand:
    st.markdown(
        """
        <div>
            <span class="brand-badge">Student Support</span>
            <h1 class="brand-heading">Campus Services Chatbot</h1>
            <p class="brand-caption">Direct answers for admissions, fees, exams, and department services</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_reset:
    if st.button("🔄 Reset", help="Start fresh conversation", use_container_width=True):
        clear_conversation()
        st.rerun()

with col_offices:
    with st.popover("🏢 Offices", help="Campus Office Directory", use_container_width=True):
        st.markdown("### 🏢 Campus Office Directory")
        st.caption("Official in-person contact desks")

        directory_entries = [
            ("College Reception", "Main Administration Block • General Enquiries"),
            ("Accounts Office", "Admin Block (Windows 1-4) • Fee Payments & Refunds"),
            ("Central Library", "Circulation Desk • Mon-Fri (9:00 AM - 5:00 PM)"),
            ("Examination Cell", "University Examination Desk • Schedules & Results"),
            ("IT Support Desk", "Network Cell • ERP Portal & Wi-Fi Access"),
            ("Hostel Office", "Hostel Administration • Room Allotments & Mess"),
            ("Grievance Redressal Cell", "Confidential Student Welfare & Proctorial Desk"),
            ("Training & Placement Cell", "T&P Desk • Campus Drives & Internships"),
        ]

        for name, detail in directory_entries:
            st.markdown(
                f"""
                <div class="directory-item">
                    <div class="directory-name">{name}</div>
                    <div class="directory-details">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ==============================================================================
# Handle Pending Query Triggered from Quick Starts
# ==============================================================================

if st.session_state.pending_query:
    active_prompt = st.session_state.pending_query
    st.session_state.pending_query = None
    with st.spinner("Checking campus service records..."):
        process_query(active_prompt)
    st.rerun()

# ==============================================================================
# Empty State: Orientation & Perfectly Sized Example Questions
# ==============================================================================

if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-box">
            <div class="welcome-title">How can we assist you today?</div>
            <div class="welcome-text">
                Ask practical questions about fees, examinations, course timetables, hostel rules,
                and certificates. Answers are derived strictly from verified institutional service guidelines.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="examples-header">Common Inquiries</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("💳 How do I pay fees through the ERP portal?", key="ex_fees", use_container_width=True):
            select_example("How do I pay fees through the ERP portal?")
            st.rerun()
        if st.button("📖 What are the Central Library timings?", key="ex_library", use_container_width=True):
            select_example("What are the Central Library timings?")
            st.rerun()

    with c2:
        if st.button("📑 What is the minimum attendance requirement?", key="ex_att", use_container_width=True):
            select_example("What is the minimum attendance requirement?")
            st.rerun()
        if st.button("🏢 How does hostel room allotment work?", key="ex_hostel", use_container_width=True):
            select_example("How does hostel room allotment work?")
            st.rerun()

    # Expandable secondary inquiries so screen stays compact and unclipped
    with st.expander("More inquiries (Bonafide certificates, Exam schedules)"):
        e1, e2 = st.columns(2)
        with e1:
            if st.button("🎓 How do I apply for a Bonafide Certificate?", key="ex_bonafide", use_container_width=True):
                select_example("How do I apply for a Bonafide Certificate?")
                st.rerun()
        with e2:
            if st.button("🗓️ When is the examination schedule released?", key="ex_exam", use_container_width=True):
                select_example("When is the examination schedule released?")
                st.rerun()

# ==============================================================================
# Active Conversation Display
# ==============================================================================

for msg in st.session_state.messages:
    role = msg["role"]
    avatar = "👤" if role == "user" else "🎓"

    with st.chat_message(role, avatar=avatar):
        # If assistant, show verified badge when matched with canonical guidelines
        if role == "assistant" and msg.get("source") == "verified_kb":
            st.markdown(
                '<div class="verified-pill">✓ Official Campus Record</div>',
                unsafe_allow_html=True,
            )

        # Message body
        st.markdown(msg["content"])

        # Physical Office Contact Card (if available)
        if role == "assistant" and msg.get("office"):
            st.markdown(
                f"""
                <div class="office-card">
                    <div class="office-card-header">
                        <span>📍</span>
                        <span>Designated Campus Office</span>
                    </div>
                    <div><strong>{msg['office']}</strong> • {msg.get('contact', 'Contact Reception')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Unanswered / Referral card (if fallback or error)
        if role == "assistant" and msg.get("source") in ("fallback", "error"):
            st.markdown(
                """
                <div class="referral-card">
                    <strong>Need official in-person verification?</strong> Please visit the <strong>College Reception</strong> (Main Administration Block) or consult your department mentor.
                </div>
                """,
                unsafe_allow_html=True,
            )

# ==============================================================================
# Message Composer
# ==============================================================================

user_text = st.chat_input("Ask a question about fees, admissions, exams, hostel, library, or support...")

if user_text:
    with st.spinner("Checking campus service records..."):
        process_query(user_text)
    st.rerun()

# ==============================================================================
# Footer
# ==============================================================================

st.markdown(
    """
    <div class="site-footer">
        Student Support Service • 48 Campus Topics Verified • Direct Inquiries: College Reception Desk
    </div>
    """,
    unsafe_allow_html=True,
)
