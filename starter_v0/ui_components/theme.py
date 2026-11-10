from __future__ import annotations


def build_shadcn_css(theme: str = "dark") -> str:
    """Return clean shadcn/ui Neutral Zinc CSS for Streamlit shell (light or dark)."""
    is_light = theme == "light"

    if is_light:
        tokens = """
        --bg: #FFFFFF;
        --fg: #09090B;
        --card: #FFFFFF;
        --secondary: #F4F4F5;
        --muted: #F4F4F5;
        --muted-fg: #71717A;
        --border: #E4E4E7;
        --input: #E4E4E7;
        --primary: #18181B;
        --primary-fg: #FAFAFA;
        --accent: #F4F4F5;
        --destructive: #DC2626;
        --sidebar-bg: #FAFAFA;
        --code-bg: #F4F4F5;
        --shadow-sm: 0 1px 2px 0 rgba(9, 9, 11, 0.04);
        """
    else:
        tokens = """
        --bg: #09090B;
        --fg: #FAFAFA;
        --card: #18181B;
        --secondary: #27272A;
        --muted: #27272A;
        --muted-fg: #A1A1AA;
        --border: #27272A;
        --input: #27272A;
        --primary: #FAFAFA;
        --primary-fg: #18181B;
        --accent: #27272A;
        --destructive: #DC2626;
        --sidebar-bg: #09090B;
        --code-bg: #18181B;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.25);
        """

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
{tokens}
    --radius: 10px;
}}

html, body, .stApp {{
    background-color: var(--bg) !important;
    color: var(--fg) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}

/* Keep Streamlit header transparent so sidebar toggle works on desktop/tablet/mobile */
header[data-testid="stHeader"] {{
    background: transparent !important;
    border-bottom: none !important;
}}

[data-testid="stDecoration"],
#MainMenu,
footer {{
    display: none !important;
}}

/* Main reading column container */
.main .block-container {{
    max-width: 880px !important;
    padding-top: 2rem !important;
    padding-bottom: 5rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}}

/* Typography */
h1, h2, h3, h4, p, li, label, span, div {{
    color: var(--fg);
}}

p, li {{
    line-height: 1.6;
}}

a {{
    color: var(--fg) !important;
    text-decoration: underline;
    text-decoration-color: var(--muted-fg);
    text-underline-offset: 3px;
}}

a:hover {{
    text-decoration-color: var(--fg);
}}

code, pre, .mono {{
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace !important;
}}

pre {{
    background-color: var(--code-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 12px 14px !important;
}}

code {{
    background-color: var(--muted);
    border-radius: 4px;
    padding: 0.12rem 0.35rem;
    font-size: 0.85em;
}}

pre code {{
    background-color: transparent !important;
    padding: 0 !important;
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
}}

[data-testid="stSidebar"] .block-container {{
    padding-top: 1.25rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}}

/* Clean shadcn Buttons */
.stButton > button {{
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    background-color: var(--card) !important;
    color: var(--fg) !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.42rem 0.85rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: background-color 140ms ease, border-color 140ms ease, opacity 140ms ease !important;
}}

.stButton > button:hover:not(:disabled) {{
    background-color: var(--accent) !important;
    border-color: var(--muted-fg) !important;
}}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {{
    background-color: var(--primary) !important;
    color: var(--primary-fg) !important;
    border-color: var(--primary) !important;
}}

.stButton > button[kind="primary"] p,
.stButton > button[data-testid="baseButton-primary"] p {{
    color: var(--primary-fg) !important;
}}

.stButton > button[kind="primary"]:hover:not(:disabled),
.stButton > button[data-testid="baseButton-primary"]:hover:not(:disabled) {{
    opacity: 0.9 !important;
}}

/* Inputs, Selectbox, TextInput */
[data-baseweb="select"] > div,
.stTextInput input,
.stTextArea textarea {{
    background-color: var(--card) !important;
    border: 1px solid var(--input) !important;
    border-radius: 8px !important;
    color: var(--fg) !important;
    font-size: 0.85rem !important;
}}

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {{
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--fg) !important;
}}

[role="option"] {{
    color: var(--fg) !important;
    background-color: transparent !important;
}}

[role="option"]:hover,
[role="option"][aria-selected="true"] {{
    background-color: var(--accent) !important;
    color: var(--fg) !important;
}}

/* Toast notification */
[data-testid="stToast"] {{
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--fg) !important;
    box-shadow: var(--shadow-sm) !important;
}}

/* Expander & Status */
[data-testid="stExpander"],
[data-testid="stStatusWidget"] {{
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}}

[data-testid="stExpander"] summary {{
    color: var(--fg) !important;
}}

/* Checkbox & Slider labels */
.stCheckbox label span,
.stSlider label {{
    color: var(--fg) !important;
}}

/* Chat Messages — Clean Claude/Linear/ChatGPT alignment */
[data-testid="stChatMessage"] {{
    background-color: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
    gap: 0.75rem !important;
}}

/* User message aligned right with subtle pill */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    flex-direction: row-reverse !important;
    justify-content: flex-start !important;
}}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {{
    background-color: var(--secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0.65rem 1rem !important;
    max-width: 78% !important;
    width: fit-content !important;
    margin-left: auto !important;
}}

/* Assistant message clean left-aligned prose */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {{
    background-color: transparent !important;
    padding: 0.15rem 0 !important;
    width: 100% !important;
}}

/* Subtle monochrome avatars */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {{
    background-color: var(--secondary) !important;
    color: var(--fg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    width: 30px !important;
    height: 30px !important;
}}

/* Chat Input Bar */
[data-testid="stBottom"],
[data-testid="stBottom"] > div {{
    background-color: var(--bg) !important;
    border-top: 1px solid var(--border) !important;
}}

[data-testid="stChatInput"] {{
    max-width: 840px !important;
    margin: 0 auto !important;
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    box-shadow: var(--shadow-sm) !important;
}}

[data-testid="stChatInput"] textarea {{
    color: var(--fg) !important;
    font-size: 0.9rem !important;
}}

/* Dialog Modal */
[data-testid="stDialog"] [role="dialog"] {{
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}}

/* Seamless React custom component iframes */
iframe[title*="ui_components"],
.stCustomComponentV1 iframe {{
    border: none !important;
    background: transparent !important;
    width: 100% !important;
}}

/* Workspace top bar & utility classes */
.ws-topbar {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding-bottom: 12px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border);
}}

.ws-title {{
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--fg);
    margin: 0;
}}

.ws-meta-row {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
}}

.ws-pill {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 8px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background-color: var(--secondary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted-fg);
}}

.ws-pill strong {{
    color: var(--fg);
    font-weight: 500;
}}

.sb-brand {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 10px;
    margin-bottom: 10px;
    border-bottom: 1px solid var(--border);
}}

.sb-brand-name {{
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--fg);
}}

.sb-section-label {{
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted-fg);
    margin: 12px 0 6px 0;
}}

.sb-status-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 10px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background-color: var(--card);
    font-size: 0.75rem;
    margin-top: 6px;
}}

.sb-dot {{
    width: 7px;
    height: 7px;
    border-radius: 999px;
    display: inline-block;
    margin-right: 6px;
}}

.sb-dot.ok {{ background-color: #22C55E; }}
.sb-dot.warn {{ background-color: #F59E0B; }}
.sb-dot.err {{ background-color: #DC2626; }}

@media (max-width: 768px) {{
    .main .block-container {{
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        padding-top: 1.5rem !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {{
        max-width: 90% !important;
    }}
}}
</style>
"""
