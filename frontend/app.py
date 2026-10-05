import sys
import os
import time
import threading
import queue

# ── Path setup so we can import the crew from src/ ───────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC  = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import streamlit as st
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"), override=True)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VentureIQ — AI Startup Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1530 40%, #0a1628 100%);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1a3a 0%, #091228 100%) !important;
    border-right: 1px solid rgba(99,179,237,0.15) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    background: linear-gradient(135deg, rgba(37,99,235,0.12) 0%, rgba(99,102,241,0.08) 100%);
    border: 1px solid rgba(99,179,237,0.18);
    border-radius: 20px;
    margin-bottom: 2rem;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem;
    line-height: 1.1;
}
.hero-sub { font-size: 1.05rem; color: #94a3b8; font-weight: 400; margin: 0; }
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(37,99,235,0.25));
    border: 1px solid rgba(99,102,241,0.4);
    color: #a78bfa;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.25rem 0.8rem;
    border-radius: 50px;
    margin-bottom: 1rem;
}
.agent-card {
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 12px;
    padding: 1rem 0.75rem;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
    margin-bottom: 0;
}
.agent-card.active {
    border-color: #6366f1;
    background: rgba(99,102,241,0.15);
    box-shadow: 0 0 20px rgba(99,102,241,0.3);
}
.agent-card.done { border-color: #10b981; background: rgba(16,185,129,0.08); }
.agent-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
.agent-name { font-size: 0.68rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.agent-status { font-size: 0.65rem; color: #64748b; margin-top: 0.2rem; }
.agent-card.active .agent-name { color: #a78bfa; }
.agent-card.active .agent-status { color: #818cf8; }
.agent-card.done .agent-name { color: #34d399; }
.agent-card.done .agent-status { color: #6ee7b7; }
.metric-card {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}
.metric-card.blue  { --accent: #3b82f6; }
.metric-card.purple { --accent: #8b5cf6; }
.metric-card.green { --accent: #10b981; }
.metric-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #64748b; margin-bottom: 0.5rem; }
.metric-value { font-family: 'Space Grotesk', sans-serif; font-size: 1.6rem; font-weight: 700; color: #f1f5f9; }
.metric-sub { font-size: 0.72rem; color: #475569; margin-top: 0.2rem; }
.input-section {
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}
.log-terminal {
    background: #020617;
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    color: #94a3b8;
    max-height: 320px;
    overflow-y: auto;
    line-height: 1.7;
}
.log-terminal .log-success { color: #34d399; }
.log-terminal .log-info    { color: #60a5fa; }
.log-terminal .log-warn    { color: #fbbf24; }
.log-terminal .log-agent   { color: #a78bfa; }
.report-container {
    background: rgba(15,23,42,0.65);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 16px;
    padding: 2rem;
    backdrop-filter: blur(10px);
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(99,179,237,0.25) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-size: 0.92rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}
.stTextInput > label, .stTextArea > label, .stSelectbox > label {
    color: #94a3b8 !important; font-size: 0.82rem !important;
    font-weight: 500 !important; letter-spacing: 0.03em !important;
}
div[data-testid="stMarkdownContainer"] p { color: #94a3b8; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #e2e8f0 !important; }
.stMarkdown h2 { color: #60a5fa !important; }
.stMarkdown strong { color: #f1f5f9 !important; }
.stMarkdown li { color: #94a3b8 !important; }
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-size: 0.9rem !important; padding: 0.55rem 1.8rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.5) !important;
}
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #2563eb, #6366f1, #8b5cf6) !important;
    border-radius: 10px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15,23,42,0.6) !important;
    border-radius: 10px !important; padding: 4px !important; gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #64748b !important;
    border-radius: 8px !important; font-weight: 500 !important;
}
.stTabs [aria-selected="true"] { background: rgba(99,102,241,0.2) !important; color: #a78bfa !important; }
hr { border-color: rgba(99,179,237,0.1) !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
AGENTS = [
    {"key": "market_research_analyst",  "icon": "📊", "label": "Market\nAnalyst"},
    {"key": "competitor_researcher",    "icon": "🔍", "label": "Competitor\nResearch"},
    {"key": "customer_researcher",      "icon": "👥", "label": "Customer\nResearch"},
    {"key": "product_researcher",       "icon": "🛠️", "label": "Product\nResearch"},
    {"key": "business_analyst",         "icon": "💼", "label": "Business\nAnalyst"},
]

AGENT_KEYWORDS = {
    "market_research_analyst": ["Market Research", "market research", "MarketResearch", "market_research_analyst"],
    "competitor_researcher":   ["Competitor", "competitor_researcher", "competitive intelligence"],
    "customer_researcher":     ["Customer Research", "customer_researcher"],
    "product_researcher":      ["Product Research", "product_researcher"],
    "business_analyst":        ["Business Analyst", "business_analyst", "Final Report", "Master Business"],
}

EXAMPLE_IDEAS = [
    "Select an example idea…",
    "Agentic AI tools for market research automation",
    "Mental health app using CBT chatbot for Gen-Z",
    "B2B SaaS for automated financial compliance auditing",
    "AI tutor for personalized K-12 learning",
    "Sustainable supply chain visibility platform for SMEs",
    "Smart home energy management with predictive AI",
]

# ── Session state defaults ────────────────────────────────────────────────────
_defaults = {
    "report":            None,
    "running":           False,
    "log_lines":         [],
    "completed_agents":  set(),
    "active_agent":      None,
    "elapsed":           0,
    "start_time":        None,
    "error":             None,
    "run_count":         0,
    "show_logs":         True,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Helper: render log terminal ───────────────────────────────────────────────
def render_logs(lines):
    rows = []
    for line in lines[-80:]:
        if any(a["key"] in line for a in AGENTS):
            cls = "log-agent"
        elif any(w in line.lower() for w in ["complete", "success", "stored", "done", "✅"]):
            cls = "log-success"
        elif any(w in line.lower() for w in ["error", "fail", "exception", "❌"]):
            cls = "log-warn"
        else:
            cls = "log-info"
        safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        rows.append(f'<span class="{cls}">{safe}</span>')
    body = "<br>".join(rows) if rows else '<span style="color:#475569;">Waiting for agents…</span>'
    return f'<div class="log-terminal">{body}</div>'

# ── Background crew runner ────────────────────────────────────────────────────
def run_crew_bg(idea, result_q, log_q):
    import io
    class LogWriter(io.TextIOBase):
        def write(self, text):
            if text.strip():
                log_q.put(text.strip())
            return len(text)
        def flush(self): pass

    old_stdout = sys.stdout
    sys.stdout = LogWriter()
    try:
        from crew_5_rag.crew import MarketResearchCrew
        output = MarketResearchCrew().crew().kickoff(inputs={"startup_idea": idea})
        result_q.put(("ok", output.raw if hasattr(output, "raw") else str(output)))
    except Exception as e:
        result_q.put(("err", str(e)))
    finally:
        sys.stdout = old_stdout

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚀 VentureIQ")
    st.markdown("*Multi-Agent Startup Intelligence*")
    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")
    for a in AGENTS:
        k     = a["key"]
        done  = k in st.session_state.completed_agents
        live  = k == st.session_state.active_agent
        icon  = "✅" if done else ("⚡" if live else "⏳")
        color = "#34d399" if done else ("#a78bfa" if live else "#475569")
        bg    = "rgba(16,185,129,0.08)" if done else ("rgba(99,102,241,0.1)" if live else "transparent")
        label = a["label"].replace("\n"," ")
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:.6rem;padding:.4rem .6rem;'
            f'border-radius:8px;margin-bottom:4px;background:{bg};">'
            f'<span>{icon}</span>'
            f'<span style="font-size:.8rem;font-weight:{"600" if (done or live) else "400"};color:{color};">{label}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    st.session_state.show_logs = st.checkbox("Show live logs", value=st.session_state.show_logs)
    st.markdown("---")
    st.markdown("### 📋 Session")
    st.markdown(f"**Reports generated:** {st.session_state.run_count}")
    if st.session_state.elapsed:
        m = int(st.session_state.elapsed // 60)
        s = int(st.session_state.elapsed % 60)
        st.markdown(f"**Last run:** {m}m {s}s")
    if st.button("🗑️ Clear Session", use_container_width=True):
        for _k, _v in _defaults.items():
            st.session_state[_k] = _v
        st.rerun()

# ── HERO HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <div class="hero-badge">Multi-Agent AI · RAG-Powered · Investor-Ready</div>
  <div class="hero-title">🚀 VentureIQ</div>
  <p class="hero-sub">
    Five specialized AI agents research market, competitors, customers, product &amp;
    business model — then synthesize a master investor report.
  </p>
</div>
""", unsafe_allow_html=True)

# ── METRICS ROW ───────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="metric-card blue"><div class="metric-label">🤖 AI Agents</div><div class="metric-value">5</div><div class="metric-sub">Specialized research roles</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card purple"><div class="metric-label">🗂️ Report Sections</div><div class="metric-value">8</div><div class="metric-sub">Executive · SWOT · GTM · Risks…</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="metric-card green"><div class="metric-label">🔍 Data Sources</div><div class="metric-value">RAG+Web</div><div class="metric-sub">ChromaDB · Cohere · Serper</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── INPUT SECTION ──────────────────────────────────────────────────────────────
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.markdown("### 💡 Describe Your Startup Idea")
st.markdown('<p style="color:#64748b;font-size:.85rem;margin-bottom:1rem;">Be specific — mention the problem, target users, and value proposition for best results.</p>', unsafe_allow_html=True)

startup_idea = st.text_area(
    "Startup Idea",
    placeholder="e.g. An AI-powered platform that automates competitor intelligence for SaaS startups, giving founders real-time alerts on pricing changes and feature launches…",
    height=100,
    label_visibility="collapsed",
    key="idea_input",
)

example = st.selectbox("💡 Or pick an example idea", EXAMPLE_IDEAS, key="example_pick")
if example and example != EXAMPLE_IDEAS[0]:
    startup_idea = example

btn_col, _ = st.columns([1, 3])
with btn_col:
    run_btn = st.button(
        "🚀 Launch Analysis",
        disabled=st.session_state.running,
        use_container_width=True,
        key="launch_btn",
    )
st.markdown('</div>', unsafe_allow_html=True)

# ── AGENT CARDS ───────────────────────────────────────────────────────────────
agent_cols = st.columns(5)
for i, a in enumerate(AGENTS):
    k    = a["key"]
    done = k in st.session_state.completed_agents
    live = k == st.session_state.active_agent
    css  = "agent-card done" if done else ("agent-card active" if live else "agent-card")
    stat = "✅ Complete" if done else ("⚡ Running…" if live else "⏳ Waiting")
    with agent_cols[i]:
        st.markdown(
            f'<div class="{css}">'
            f'<div class="agent-icon">{a["icon"]}</div>'
            f'<div class="agent-name">{a["label"]}</div>'
            f'<div class="agent-status">{stat}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── PROGRESS BAR ──────────────────────────────────────────────────────────────
pct = len(st.session_state.completed_agents) / len(AGENTS)
progress_bar = st.progress(pct)

# ── LOG + STATUS PLACEHOLDERS ─────────────────────────────────────────────────
log_ph    = st.empty()
status_ph = st.empty()

# ── RUN LOGIC ─────────────────────────────────────────────────────────────────
if run_btn:
    if not startup_idea.strip():
        st.error("⚠️ Please enter a startup idea.")
    else:
        st.session_state.running          = True
        st.session_state.report           = None
        st.session_state.log_lines        = ["[VentureIQ] 🚀 Launching 5-agent analysis…"]
        st.session_state.completed_agents = set()
        st.session_state.active_agent     = AGENTS[0]["key"]
        st.session_state.error            = None
        st.session_state.start_time       = time.time()

        rq = queue.Queue()
        lq = queue.Queue()
        t  = threading.Thread(target=run_crew_bg, args=(startup_idea.strip(), rq, lq), daemon=True)
        t.start()

        with st.spinner(""):
            while t.is_alive() or not rq.empty():
                while not lq.empty():
                    txt = lq.get_nowait()
                    st.session_state.log_lines.append(txt)
                    for idx, ag in enumerate(AGENTS):
                        kws = AGENT_KEYWORDS.get(ag["key"], [])
                        if any(kw in txt for kw in kws):
                            if ag["key"] not in st.session_state.completed_agents:
                                for prev in AGENTS[:idx]:
                                    st.session_state.completed_agents.add(prev["key"])
                                st.session_state.active_agent = ag["key"]

                st.session_state.elapsed = time.time() - st.session_state.start_time
                pct_now = min(len(st.session_state.completed_agents) / len(AGENTS) + 0.04, 0.98)
                progress_bar.progress(pct_now)

                if st.session_state.show_logs:
                    log_ph.markdown(render_logs(st.session_state.log_lines), unsafe_allow_html=True)

                m2 = int(st.session_state.elapsed // 60)
                s2 = int(st.session_state.elapsed % 60)
                status_ph.markdown(
                    f'<p style="color:#64748b;font-size:.8rem;text-align:center;">'
                    f'⏱ Running · {m2}m {s2}s elapsed · {len(st.session_state.completed_agents)}/{len(AGENTS)} agents done</p>',
                    unsafe_allow_html=True,
                )
                time.sleep(0.8)
                if not rq.empty():
                    break

        if not rq.empty():
            kind, payload = rq.get()
            if kind == "ok":
                st.session_state.report           = payload
                st.session_state.completed_agents = {a["key"] for a in AGENTS}
                st.session_state.active_agent     = None
                st.session_state.run_count        += 1
                progress_bar.progress(1.0)
                st.session_state.log_lines.append("✅ [VentureIQ] Analysis complete! Master report generated.")
            else:
                st.session_state.error = payload
                st.session_state.log_lines.append(f"❌ Error: {payload}")
        else:
            st.session_state.error = "Thread finished with no result. Check API keys and environment."

        st.session_state.running = False
        st.rerun()

# ── ERROR DISPLAY ─────────────────────────────────────────────────────────────
if st.session_state.error:
    st.error(f"❌ **Error:** {st.session_state.error}")
    with st.expander("🔍 Troubleshooting"):
        st.markdown("""
- Ensure `.env` contains `GEMINI_API_KEY`, `SERPER_API_KEY`, and `COHERE_API_KEY`
- Run `uv sync` in the project root to install all dependencies
- Try `crewai run` from the project root first to validate the crew
- Ensure `market_research_db/` directory is writable
        """)

# ── LOGS (post-run) ───────────────────────────────────────────────────────────
if st.session_state.show_logs and st.session_state.log_lines and not st.session_state.running:
    with st.expander("📋 Agent Execution Logs", expanded=False):
        st.markdown(render_logs(st.session_state.log_lines), unsafe_allow_html=True)

# ── REPORT ────────────────────────────────────────────────────────────────────
if st.session_state.report:
    st.markdown("---")
    st.markdown("""
    <div style="display:flex;align-items:center;gap:.8rem;margin-bottom:1.5rem;">
      <span style="font-size:1.8rem;">📄</span>
      <div>
        <h2 style="font-family:'Space Grotesk',sans-serif;color:#60a5fa;margin:0;font-size:1.6rem;">Master Business Analysis Report</h2>
        <p style="color:#64748b;font-size:.82rem;margin:0;">AI-generated · Investor-ready · Powered by VentureIQ</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊 Formatted Report", "📝 Raw Markdown"])
    with tab1:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(st.session_state.report)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        st.code(st.session_state.report, language="markdown")

    st.markdown("<br>", unsafe_allow_html=True)
    d1, d2, _ = st.columns([1,1,2])
    with d1:
        st.download_button("⬇️ Download .md", data=st.session_state.report,
                           file_name="ventureiq_report.md", mime="text/markdown",
                           use_container_width=True)
    with d2:
        st.download_button("⬇️ Download .txt", data=st.session_state.report,
                           file_name="ventureiq_report.txt", mime="text/plain",
                           use_container_width=True)

# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if not st.session_state.report and not st.session_state.running and not st.session_state.error:
    st.markdown("""
    <div style="text-align:center;padding:3rem 2rem;background:rgba(15,23,42,0.4);
    border:1px dashed rgba(99,179,237,0.2);border-radius:16px;margin-top:1rem;">
      <div style="font-size:3rem;margin-bottom:1rem;">🔬</div>
      <h3 style="font-family:'Space Grotesk',sans-serif;color:#475569;font-size:1.1rem;margin:0 0 .5rem;">Ready to Analyze</h3>
      <p style="color:#334155;font-size:.85rem;max-width:400px;margin:0 auto;">
        Enter your startup idea above and click <strong style="color:#6366f1;">Launch Analysis</strong>.
        Five AI agents will generate a comprehensive investor-ready report.
      </p>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;margin-top:3rem;border-top:1px solid rgba(99,179,237,0.08);">
  <p style="color:#1e293b;font-size:.75rem;margin:0;">
    VentureIQ · Multi-Agent Startup Intelligence · CrewAI · ChromaDB · Cohere · Serper
  </p>
</div>
""", unsafe_allow_html=True)
