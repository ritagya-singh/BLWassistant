"""
BLW Employee Assistant — Streamlit App
Real India map background (36 state SVG paths) + WAP-7 electric loco + cream/green chatbot
"""
import re
import streamlit as st
from datetime import datetime
from data import lookup_employee
from india_map import get_india_svg
# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="BLW Employee Assistant",
    page_icon="🚂",
    layout="centered",
    initial_sidebar_state="collapsed",
)
# ── Session state ──────────────────────────────────────────────
for key, default in [
    ("messages",   []),
    ("phase",      "awaiting_name"),
    ("user_name",  None),
    ("attempts",   0),
    ("last_emp",   None),
    ("chips",      []),
]:
    if key not in st.session_state:
        st.session_state[key] = default
# ── Helpers ────────────────────────────────────────────────────
def fmt(n: int) -> str:
    return "₹{:,}".format(n)
def greeting() -> str:
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"
def payslip_html(emp: dict) -> str:
    gross = emp["basic"] + emp["da"] + emp["hra"] + emp["ta"]
    ded   = emp["pf"] + emp["income_tax"] + emp["esi"] + emp["other"]
    net   = gross - ded
    month = datetime.now().strftime("%B %Y")
    ded_rows = "<tr><td>Provident Fund (12% of Basic)</td><td class='ded'>−" + fmt(emp['pf']) + "</td></tr>"
    if emp["income_tax"] > 0:
        ded_rows += "<tr><td>Income Tax (TDS)</td><td class='ded'>−" + fmt(emp['income_tax']) + "</td></tr>"
    if emp["esi"] > 0:
        ded_rows += "<tr><td>ESI Deduction</td><td class='ded'>−" + fmt(emp['esi']) + "</td></tr>"
    if emp["other"] > 0:
        ded_rows += "<tr><td>Other Deductions</td><td class='ded'>−" + fmt(emp['other']) + "</td></tr>"
    return (
        '<div class="payslip">'
        '<div class="ps-top">'
        '<div>'
        '<div class="ps-name">' + emp['name'] + '</div>'
        '<div class="ps-sub">' + emp['designation'] + ' &nbsp;·&nbsp; ' + emp['department'] + ' &nbsp;·&nbsp; ' + emp['grade'] + '</div>'
        '</div>'
        '<div class="ps-badge">📅 ' + month + '</div>'
        '</div>'
        '<div class="ps-body">'
        '<div class="ps-sect-lbl">EARNINGS</div>'
        '<table class="pst">'
        '<tr><td>Basic Pay</td><td class="earn">' + fmt(emp['basic']) + '</td></tr>'
        '<tr><td>Dearness Allowance (DA)</td><td class="earn">' + fmt(emp['da']) + '</td></tr>'
        '<tr><td>House Rent Allowance (HRA)</td><td class="earn">' + fmt(emp['hra']) + '</td></tr>'
        '<tr><td>Transport Allowance (TA)</td><td class="earn">' + fmt(emp['ta']) + '</td></tr>'
        '<tr class="tot-row"><td><strong>Gross Salary</strong></td><td class="earn"><strong>' + fmt(gross) + '</strong></td></tr>'
        '</table>'
        '<div class="ps-sect-lbl" style="margin-top:14px;">DEDUCTIONS</div>'
        '<table class="pst">'
        + ded_rows +
        '<tr class="tot-row"><td><strong>Total Deductions</strong></td><td class="ded"><strong>−' + fmt(ded) + '</strong></td></tr>'
        '</table>'
        '<div class="net-box">'
        '<span class="net-lbl">💳 &nbsp;Net Salary Credited</span>'
        '<span class="net-amt">' + fmt(net) + '</span>'
        '</div>'
        '</div>'
        '<div class="ps-foot">'
        '🏦 &nbsp;A/C: <strong>' + emp['account_no'] + '</strong> &nbsp;·&nbsp; ' + emp['bank'] +
        ' &nbsp;&nbsp;|&nbsp;&nbsp; Employer PF Contribution: <strong>' + fmt(emp['pf_employer']) + '</strong>'
        '</div>'
        '</div>'
    )
# ── Response generator ─────────────────────────────────────────
def generate_response(user_input: str):
    """Returns (content: str, is_html: bool, chips: list[str])"""
    raw   = user_input.strip()
    phase = st.session_state.phase
    if phase == "awaiting_name":
        st.session_state.user_name = raw
        st.session_state.phase = "awaiting_service"
        return (
            greeting() + ", **" + raw + "**! 👋\n\n"
            "To fetch your salary slip, please enter your **Service Number** and **full name** in this format:\n\n"
            "`Service Number, Full Name`\n\n"
            "*Example: BLW001, Rajesh Kumar Singh*",
            False,
            ["BLW001, Rajesh Kumar Singh", "BLW002, Priya Sharma", "Help"],
        )
    if phase == "awaiting_service":
        if raw.lower() == "help":
            return (
                "**📋 Help**\n\n"
                "Enter your **Service Number** and **Name** separated by a comma.\n\n"
                "`BLW001, Your Full Name`\n\n"
                "Your Service Number is printed on your BLW Identity Card.",
                False,
                ["BLW001, Rajesh Kumar Singh", "BLW003, Mohan Lal Verma"],
            )
        ci = raw.find(",")
        if ci != -1:
            svc, name = raw[:ci].strip(), raw[ci + 1:].strip()
        else:
            m = re.match(r"^([A-Za-z]{2,4}\d{3,6})\s+(.+)$", raw, re.I)
            if m:
                svc, name = m.group(1).strip(), m.group(2).strip()
            else:
                return (
                    "Please provide both your **Service Number** and **Name**.\n\n"
                    "Format: `BLW001, Your Name`",
                    False,
                    ["BLW001, Rajesh Kumar Singh", "Help"],
                )
        result = lookup_employee(svc, name)
        if result["error"] == "not_found":
            st.session_state.attempts += 1
            if st.session_state.attempts >= 3:
                st.session_state.phase = "done"
                return ("🔒 Too many failed attempts. Contact HR: **0542-2501234**.", False, [])
            return (
                "❌ Service number **" + svc.upper() + "** not found.\n\n"
                "Please verify and try again. *(Attempt " + str(st.session_state.attempts) + "/3)*",
                False, ["Help"],
            )
        if result["error"] == "name_mismatch":
            st.session_state.attempts += 1
            if st.session_state.attempts >= 3:
                st.session_state.phase = "done"
                return ("🔒 Too many failed attempts. Contact HR: **0542-2501234**.", False, [])
            return (
                "⚠️ Name doesn't match our records for this service number.\n\n"
                "Please use your full name as per BLW records. *(Attempt " + str(st.session_state.attempts) + "/3)*",
                False, [],
            )
        emp = result["employee"]
        st.session_state.last_emp = emp
        st.session_state.phase    = "done"
        return (payslip_html(emp), True, ["View Salary Again", "PF Info", "Contact HR", "Start Over"])
    if phase == "done":
        l = raw.lower()
        if any(k in l for k in ["salary", "again", "slip", "payslip"]):
            emp = st.session_state.last_emp
            if emp:
                return (payslip_html(emp), True, ["PF Info", "Contact HR", "Start Over"])
        if any(k in l for k in ["pf", "provident", "fund"]):
            return (
                "**🏦 Provident Fund (PF) Information**\n\n"
                "| Detail | Value |\n|---|---|\n"
                "| Employee Contribution | 12% of Basic Pay |\n"
                "| Employer Contribution | 12% of Basic Pay |\n"
                "| Credited to | EPFO Account |\n\n"
                "📞 PF Helpline: **1800-118-005** *(toll free)*\n"
                "🌐 epfindia.gov.in",
                False,
                ["View Salary Again", "Contact HR", "Start Over"],
            )
        if any(k in l for k in ["hr", "contact", "human resource", "personnel"]):
            return (
                "**📞 BLW HR / Personnel Department**\n\n"
                "📞 **0542-2501234**\n\n"
                "📧 hr@blw.indianrailways.gov.in\n\n"
                "🏢 Personnel Branch, BLW Campus, Varanasi – 221005\n\n"
                "⏰ Mon – Sat &nbsp;|&nbsp; 9:00 AM – 5:30 PM",
                False,
                ["View Salary Again", "PF Info", "Start Over"],
            )
        if any(k in l for k in ["start over", "restart", "new", "reset"]):
            st.session_state.phase     = "awaiting_name"
            st.session_state.user_name = None
            st.session_state.attempts  = 0
            st.session_state.last_emp  = None
            return (
                greeting() + " again! 🙏 Please tell me your **name** to begin.",
                False,
                ["Rajesh Kumar", "Priya Sharma", "Amit Pandey"],
            )
        return (
            "I can help you with your **salary slip**, **provident fund details**, or **HR contact information**.",
            False,
            ["View Salary Again", "PF Info", "Contact HR", "Start Over"],
        )
    return ("I didn't understand that. Please try again.", False, [])
# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body { height: 100%; }
.stApp {
    font-family: 'Inter', sans-serif !important;
    background: #f4efe4 !important;
}
#MainMenu, footer, .stDeployButton { display: none !important; }
header[data-testid="stHeader"] {
    background: rgba(244,239,228,0.97) !important;
}
/* Main container — above fixed background */
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 720px !important;
    position: relative;
    z-index: 10;
    isolation: isolate;
}
section[data-testid="stMain"] {
    position: relative;
    z-index: 10;
}
/* ── Background scene ── */
.bg-scene {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
/* India map — faded, centred */
.india-wrap {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: min(62vw, 440px);
    opacity: 0.13;
}
/* Electric loco */
.loco-wrap {
    position: absolute;
    top: 51%;
    transform: translateY(-50%);
    animation: trainRide 55s linear infinite;
    opacity: 0.20;
}
@keyframes trainRide {
    0%   { left: -340px; }
    100% { left: 110vw;  }
}
/* ── Header ── */
.blw-header {
    text-align: center;
    padding: 18px 0 10px;
    position: relative;
    z-index: 2;
}
.blw-logo-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 4px;
}
.blw-title {
    font-size: 23px;
    font-weight: 700;
    color: #1b4332;
    letter-spacing: -0.3px;
}
.blw-title span { font-weight: 400; color: #52796f; font-size: 18px; }
.blw-tagline { font-size: 12px; color: #74a57f; letter-spacing: 0.4px; margin-top: 3px; }
.blw-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #b7e4c7, transparent);
    margin: 14px auto 18px;
    width: 80%;
}
/* ── Chat messages ── */
[data-testid="stChatMessageContent"] {
    background: #ffffff !important;
    border: 1px solid #d0e8d4 !important;
    border-radius: 14px !important;
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
    color: #1c3829 !important;
    box-shadow: 0 1px 6px rgba(45,106,79,0.07) !important;
    line-height: 1.65 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] {
    background: #2d6a4f !important;
    color: #f0fdf4 !important;
    border-color: #2d6a4f !important;
}
[data-testid="stChatMessageAvatarAssistant"] { background: #d8f3dc !important; }
[data-testid="stChatMessageAvatarUser"]      { background: #2d6a4f !important; }
[data-testid="stChatMessageContent"] p { margin-bottom: 6px !important; }
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0 !important; }
[data-testid="stChatMessageContent"] code {
    background: #f0fdf4 !important;
    color: #1b4332 !important;
    border-radius: 4px !important;
    padding: 1px 6px !important;
    font-size: 12.5px !important;
}
/* ── Chat input ── */
[data-testid="stChatInput"] {
    border-radius: 28px !important;
    border: 1.5px solid #b7e4c7 !important;
    background: #ffffff !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #2d6a4f !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,0.12) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    color: #1c3829 !important;
    background: transparent !important;
    border: none !important;
}
[data-testid="stChatInput"] button {
    background: #2d6a4f !important;
    border-radius: 50% !important;
}
/* ── Payslip card ── */
.payslip {
    border: 1px solid #c8e6d0;
    border-radius: 14px;
    overflow: hidden;
    font-family: 'Inter', sans-serif;
    font-size: 13.5px;
    box-shadow: 0 3px 16px rgba(45,106,79,0.10);
    margin: 6px 0;
}
.ps-top {
    background: linear-gradient(135deg, #2d6a4f 0%, #40916c 100%);
    color: #fff;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
}
.ps-name { font-size: 16px; font-weight: 700; }
.ps-sub  { font-size: 11.5px; opacity: 0.72; margin-top: 4px; }
.ps-badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    flex-shrink: 0;
}
.ps-body { padding: 16px 20px; background: #fff; }
.ps-sect-lbl {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.1px;
    color: #74a57f;
    text-transform: uppercase;
    padding-bottom: 6px;
    border-bottom: 1px solid #e8f5ec;
    margin-bottom: 4px;
}
.pst { width: 100%; border-collapse: collapse; }
.pst td { padding: 7px 6px; color: #374151; }
.pst tr:hover td { background: #f7fdf9; border-radius: 6px; }
.pst .earn { text-align: right; font-weight: 600; color: #1a56a0; }
.pst .ded  { text-align: right; font-weight: 600; color: #dc2626; }
.pst .tot-row { border-top: 1px solid #e8f5ec; }
.pst .tot-row td { padding-top: 9px; font-size: 14px; }
.net-box {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #f0fdf4, #e8f8ee);
    border: 1.5px solid #86efac;
    border-radius: 10px;
    padding: 13px 16px;
    margin-top: 14px;
}
.net-lbl { font-size: 13.5px; font-weight: 600; color: #166534; }
.net-amt { font-size: 20px; font-weight: 800; color: #15803d; letter-spacing: -0.5px; }
.ps-foot {
    background: #f9fdf9;
    border-top: 1px solid #e0f0e4;
    padding: 10px 20px;
    font-size: 11.5px;
    color: #6b7280;
}
/* ── Suggestion chips ── */
.stButton > button {
    background: #ffffff !important;
    border: 1.5px solid #b7e4c7 !important;
    border-radius: 22px !important;
    color: #2d6a4f !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 5px 16px !important;
    transition: all 0.15s !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #2d6a4f !important;
    color: #ffffff !important;
    border-color: #2d6a4f !important;
    transform: translateY(-1px);
    box-shadow: 0 3px 10px rgba(45,106,79,0.2) !important;
}
/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #b7e4c7; border-radius: 10px; }
/* ── Tables inside chat ── */
[data-testid="stChatMessageContent"] table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 4px;
}
[data-testid="stChatMessageContent"] th,
[data-testid="stChatMessageContent"] td {
    padding: 7px 10px;
    border-bottom: 1px solid #e8f5ec;
    text-align: left;
}
[data-testid="stChatMessageContent"] th {
    background: #f0fdf4;
    font-weight: 600;
    color: #1b4332;
}
</style>
""", unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════
# Animated background — real India map (loaded from file/network)
# + WAP-7 electric locomotive
# Note: We build the HTML as a plain string (no f-string) so that
# curly braces inside the SVG path data don't confuse Python.
# ══════════════════════════════════════════════════════════════
_india_svg = get_india_svg()   # loads cached india_map_svg.txt
_loco_svg = """
<svg width="320" height="95" viewBox="0 0 320 95" xmlns="http://www.w3.org/2000/svg">
  <!-- Overhead catenary wire -->
  <line x1="-60" y1="6" x2="380" y2="6"
        stroke="#2d6a4f" stroke-width="1.4" opacity="0.55" stroke-dasharray="18,6"/>
  <line x1="80"  y1="6" x2="80"  y2="10" stroke="#2d6a4f" stroke-width="1" opacity="0.4"/>
  <line x1="160" y1="6" x2="160" y2="10" stroke="#2d6a4f" stroke-width="1" opacity="0.4"/>
  <line x1="240" y1="6" x2="240" y2="10" stroke="#2d6a4f" stroke-width="1" opacity="0.4"/>
  <line x1="-60" y1="9" x2="380" y2="9"
        stroke="#2d6a4f" stroke-width="2.2" opacity="0.40"/>
  <!-- Pantograph (diamond bow collector) -->
  <rect x="102" y="24" width="6" height="6" rx="1" fill="#2d6a4f"/>
  <rect x="150" y="24" width="6" height="6" rx="1" fill="#2d6a4f"/>
  <line x1="105" y1="24" x2="129" y2="14" stroke="#2d6a4f" stroke-width="2"/>
  <line x1="153" y1="24" x2="129" y2="14" stroke="#2d6a4f" stroke-width="2"/>
  <line x1="120" y1="9"  x2="138" y2="9"  stroke="#2d6a4f" stroke-width="3"/>
  <line x1="120" y1="9"  x2="115" y2="14" stroke="#2d6a4f" stroke-width="1.8"/>
  <line x1="138" y1="9"  x2="143" y2="14" stroke="#2d6a4f" stroke-width="1.8"/>
  <line x1="115" y1="14" x2="143" y2="14" stroke="#2d6a4f" stroke-width="1.5"/>
  <line x1="115" y1="14" x2="105" y2="24" stroke="#2d6a4f" stroke-width="2"/>
  <line x1="143" y1="14" x2="153" y2="24" stroke="#2d6a4f" stroke-width="2"/>
  <!-- Roof -->
  <rect x="18" y="24" width="280" height="6" rx="2" fill="#245a40"/>
  <!-- Main body (WAP-7 style long rectangular loco) -->
  <rect x="18" y="28" width="280" height="44" rx="4" fill="#2d6a4f"/>
  <!-- Left cab -->
  <path d="M 18,28 L 18,72 L 68,72 L 68,28 Z" fill="#1e5040"/>
  <rect x="22" y="32" width="40" height="24" rx="3" fill="#f4efe4" opacity="0.82"/>
  <rect x="22" y="58" width="16" height="12" rx="2" fill="#f4efe4" opacity="0.60"/>
  <circle cx="20" cy="44" r="5" fill="#f4efe4" opacity="0.75"/>
  <circle cx="20" cy="57" r="3" fill="#f4efe4" opacity="0.55"/>
  <rect x="12" y="65" width="10" height="7" rx="1" fill="#1b3a28"/>
  <rect x="8"  y="67" width="14" height="5" rx="1" fill="#2d6a4f"/>
  <!-- Right cab -->
  <path d="M 250,28 L 250,72 L 298,72 L 298,28 Z" fill="#1e5040"/>
  <rect x="254" y="32" width="40" height="24" rx="3" fill="#f4efe4" opacity="0.82"/>
  <rect x="278" y="58" width="16" height="12" rx="2" fill="#f4efe4" opacity="0.60"/>
  <circle cx="297" cy="44" r="5" fill="#f4efe4" opacity="0.75"/>
  <circle cx="297" cy="57" r="3" fill="#f4efe4" opacity="0.55"/>
  <rect x="294" y="65" width="10" height="7" rx="1" fill="#1b3a28"/>
  <rect x="294" y="67" width="14" height="5" rx="1" fill="#2d6a4f"/>
  <!-- Equipment housings + louvres -->
  <rect x="74"  y="30" width="22" height="38" rx="2" fill="#1b4a38"/>
  <rect x="100" y="30" width="14" height="38" rx="2" fill="#1b4a38"/>
  <line x1="76" y1="36" x2="94" y2="36" stroke="#2d6a4f" stroke-width="1.2"/>
  <line x1="76" y1="42" x2="94" y2="42" stroke="#2d6a4f" stroke-width="1.2"/>
  <line x1="76" y1="48" x2="94" y2="48" stroke="#2d6a4f" stroke-width="1.2"/>
  <line x1="76" y1="54" x2="94" y2="54" stroke="#2d6a4f" stroke-width="1.2"/>
  <line x1="76" y1="60" x2="94" y2="60" stroke="#2d6a4f" stroke-width="1.2"/>
  <rect x="192" y="30" width="14" height="38" rx="2" fill="#1b4a38"/>
  <rect x="210" y="30" width="22" height="38" rx="2" fill="#1b4a38"/>
  <line x1="212" y1="36" x2="230" y2="36" stroke="#2d6a4f" stroke-width="1.2"/>
  <line x1="212" y1="42" x2="230" y2="42" stroke="#2d6a4f" stroke-width="1.2"/>
  <line x1="212" y1="48" x2="230" y2="48" stroke="#2d6a4f" stroke-width="1.2"/>
  <line x1="212" y1="54" x2="230" y2="54" stroke="#2d6a4f" stroke-width="1.2"/>
  <line x1="212" y1="60" x2="230" y2="60" stroke="#2d6a4f" stroke-width="1.2"/>
  <!-- Centre ventilation grilles -->
  <rect x="120" y="32" width="75" height="10" rx="2" fill="#1b4a38"/>
  <rect x="120" y="46" width="75" height="10" rx="2" fill="#1b4a38"/>
  <rect x="120" y="58" width="75" height="10" rx="2" fill="#1b4a38"/>
  <!-- Underframe -->
  <rect x="14" y="70" width="288" height="5" rx="2" fill="#142d1f"/>
  <!-- Left bogie — 3 axles -->
  <rect x="22" y="74" width="80" height="7" rx="3" fill="#1b3a28"/>
  <circle cx="36" cy="83" r="9" fill="none" stroke="#2d6a4f" stroke-width="2.2"/>
  <circle cx="36" cy="83" r="3" fill="#2d6a4f"/>
  <line x1="36" y1="74" x2="36" y2="92" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 36 83" to="360 36 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <line x1="27" y1="83" x2="45" y2="83" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 36 83" to="360 36 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <circle cx="62" cy="83" r="9" fill="none" stroke="#2d6a4f" stroke-width="2.2"/>
  <circle cx="62" cy="83" r="3" fill="#2d6a4f"/>
  <line x1="62" y1="74" x2="62" y2="92" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 62 83" to="360 62 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <line x1="53" y1="83" x2="71" y2="83" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 62 83" to="360 62 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <circle cx="88" cy="83" r="9" fill="none" stroke="#2d6a4f" stroke-width="2.2"/>
  <circle cx="88" cy="83" r="3" fill="#2d6a4f"/>
  <line x1="88" y1="74" x2="88" y2="92" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 88 83" to="360 88 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <line x1="79" y1="83" x2="97" y2="83" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 88 83" to="360 88 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <!-- Right bogie — 3 axles -->
  <rect x="214" y="74" width="80" height="7" rx="3" fill="#1b3a28"/>
  <circle cx="228" cy="83" r="9" fill="none" stroke="#2d6a4f" stroke-width="2.2"/>
  <circle cx="228" cy="83" r="3" fill="#2d6a4f"/>
  <line x1="228" y1="74" x2="228" y2="92" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 228 83" to="360 228 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <line x1="219" y1="83" x2="237" y2="83" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 228 83" to="360 228 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <circle cx="254" cy="83" r="9" fill="none" stroke="#2d6a4f" stroke-width="2.2"/>
  <circle cx="254" cy="83" r="3" fill="#2d6a4f"/>
  <line x1="254" y1="74" x2="254" y2="92" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 254 83" to="360 254 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <line x1="245" y1="83" x2="263" y2="83" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 254 83" to="360 254 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <circle cx="280" cy="83" r="9" fill="none" stroke="#2d6a4f" stroke-width="2.2"/>
  <circle cx="280" cy="83" r="3" fill="#2d6a4f"/>
  <line x1="280" y1="74" x2="280" y2="92" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 280 83" to="360 280 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <line x1="271" y1="83" x2="289" y2="83" stroke="#2d6a4f" stroke-width="1.6">
    <animateTransform attributeName="transform" type="rotate"
      from="0 280 83" to="360 280 83" dur="2s" repeatCount="indefinite"/>
  </line>
  <!-- Rail -->
  <rect x="-60" y="91" width="440" height="3" rx="1.5" fill="#2d6a4f" opacity="0.45"/>
  <rect x="-60" y="88" width="440" height="1.5" rx="1" fill="#2d6a4f" opacity="0.25"/>
</svg>
"""
# Build background HTML using plain string concatenation (NOT f-string)
# so that { } chars in SVG path data are never interpreted by Python
_bg_html = (
    '<div class="bg-scene">'
    '<div class="india-wrap">' + _india_svg + '</div>'
    '<div class="loco-wrap">' + _loco_svg + '</div>'
    '</div>'
)
st.markdown(_bg_html, unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════
# Header
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="blw-header">
  <div class="blw-logo-row">
    <svg width="40" height="40" viewBox="0 0 40 40">
      <circle cx="20" cy="20" r="19" fill="#2d6a4f" fill-opacity="0.12"
              stroke="#2d6a4f" stroke-opacity="0.3" stroke-width="1.5"/>
      <text x="20" y="16" text-anchor="middle" fill="#1b4332"
            font-size="9.5" font-weight="700" font-family="Inter, sans-serif">BLW</text>
      <text x="20" y="25" text-anchor="middle" fill="#52796f"
            font-size="5" font-family="Inter, sans-serif">RAILWAYS</text>
      <path d="M8 32 Q20 26 32 32" stroke="#2d6a4f" stroke-width="1"
            fill="none" stroke-opacity="0.4"/>
    </svg>
    <div class="blw-title">BLW Assistant <span>/ Employee Portal</span></div>
  </div>
  <div class="blw-tagline">Banaras Locomotive Works · Salary · PF · HR Support</div>
  <div class="blw-divider"></div>
</div>
""", unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════
# Initial greeting
# ══════════════════════════════════════════════════════════════
if not st.session_state.messages:
    welcome = (
        greeting() + "! Welcome to the **BLW Employee Self-Service Portal**. 🙏\n\n"
        "I'm your personal assistant at **Banaras Locomotive Works**.\n\n"
        "I can help you with:\n"
        "- 💰 Monthly salary slip & deduction details\n"
        "- 🏦 Provident Fund information\n"
        "- 📞 HR contact details\n\n"
        "To get started, please tell me your **name**."
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome, "html": False})
    st.session_state.chips = ["Rajesh Kumar", "Priya Sharma", "Amit Pandey"]
# ══════════════════════════════════════════════════════════════
# Render chat history
# ══════════════════════════════════════════════════════════════
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🚂" if msg["role"] == "assistant" else "👤"):
        if msg.get("html"):
            st.markdown(msg["content"], unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])
# ══════════════════════════════════════════════════════════════
# Suggestion chips
# ══════════════════════════════════════════════════════════════
pending = None
if st.session_state.chips:
    cols = st.columns(len(st.session_state.chips))
    for i, chip_text in enumerate(st.session_state.chips):
        with cols[i]:
            if st.button(chip_text, key="chip_" + str(i) + "_" + chip_text):
                pending = chip_text
# ══════════════════════════════════════════════════════════════
# Chat input
# ══════════════════════════════════════════════════════════════
user_input = st.chat_input("Type your message here…")
raw_input = pending or user_input
if raw_input:
    st.session_state.chips = []
    st.session_state.messages.append({"role": "user", "content": raw_input, "html": False})
    response_text, is_html, new_chips = generate_response(raw_input)
    st.session_state.messages.append({"role": "assistant", "content": response_text, "html": is_html})
    st.session_state.chips = new_chips
    st.rerun()
