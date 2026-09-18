"""
UI Theme & Design System Module
Unified Light and Dark Mode Engine with High-Contrast Typography, Glassmorphism, and Avatars
"""
import streamlit as st
import hashlib

# Curated palette for SVG avatars
AVATAR_GRADIENTS = [
    ("linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)", "#FFFFFF"),
    ("linear-gradient(135deg, #EC4899 0%, #BE185D 100%)", "#FFFFFF"),
    ("linear-gradient(135deg, #10B981 0%, #059669 100%)", "#FFFFFF"),
    ("linear-gradient(135deg, #F59E0B 0%, #D97706 100%)", "#FFFFFF"),
    ("linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)", "#FFFFFF"),
    ("linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)", "#FFFFFF"),
    ("linear-gradient(135deg, #14B8A6 0%, #0F766E 100%)", "#FFFFFF"),
]

def get_current_theme() -> str:
    """Return active theme ('dark' or 'light')"""
    if 'app_theme' not in st.session_state:
        st.session_state.app_theme = "dark"
    return st.session_state.app_theme

def inject_custom_theme():
    """Inject modern CSS, Google Fonts, and design system tokens for active theme"""
    theme = get_current_theme()
    is_dark = (theme == "dark")

    # Tokens based on active theme
    bg_main = "#0B0F19" if is_dark else "#F8FAFC"
    bg_card = "rgba(17, 24, 39, 0.85)" if is_dark else "#FFFFFF"
    border_card = "rgba(55, 65, 81, 0.6)" if is_dark else "rgba(226, 232, 240, 0.85)"
    text_primary = "#F9FAFB" if is_dark else "#0F172A"
    text_secondary = "#9CA3AF" if is_dark else "#475569"
    
    sidebar_bg = "#111827" if is_dark else "#FFFFFF"
    sidebar_border = "#1F2937" if is_dark else "#E2E8F0"
    sidebar_text = "#F3F4F6" if is_dark else "#0F172A"
    sidebar_subtext = "#9CA3AF" if is_dark else "#475569"
    sidebar_nav_bg = "rgba(31, 41, 55, 0.7)" if is_dark else "#FFFFFF"
    sidebar_nav_border = "#374151" if is_dark else "#CBD5E1"
    sidebar_nav_hover = "rgba(99, 102, 241, 0.25)" if is_dark else "#EEF2FF"
    sidebar_nav_active = "rgba(99, 102, 241, 0.35)" if is_dark else "#E0E7FF"
    sidebar_nav_active_border = "#818CF8" if is_dark else "#4F46E5"
    sidebar_nav_active_text = "#A5B4FC" if is_dark else "#4338CA"

    tab_bg = "rgba(17, 24, 39, 0.85)" if is_dark else "#F1F5F9"
    tab_border = "#374151" if is_dark else "#CBD5E1"
    tab_active_bg = "#1F2937" if is_dark else "#FFFFFF"
    tab_active_text = "#818CF8" if is_dark else "#4338CA"
    tab_inactive_text = "#9CA3AF" if is_dark else "#475569"

    btn_sec_bg = "#1F2937" if is_dark else "#FFFFFF"
    btn_sec_border = "#374151" if is_dark else "#CBD5E1"
    btn_sec_text = "#F9FAFB" if is_dark else "#0F172A"
    btn_sec_hover = "#374151" if is_dark else "#F1F5F9"

    input_bg = "#1F2937" if is_dark else "#FFFFFF"
    input_border = "#374151" if is_dark else "#CBD5E1"
    input_text = "#F9FAFB" if is_dark else "#0F172A"

    st.markdown(f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">

    <style>
        /* Modern Font & Global Overrides (Exempt Material Symbols to avoid raw text leakage) */
        html, body, [class*="css"], [class*="st-"]:not([class*="material-symbols"]):not([data-testid="stIconMaterial"]) {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* Material Symbols Icon Protection - Ensures icons render as glyphs, NOT raw text strings like keyboard_double_arrow_right */
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-symbols-sharp,
        [data-testid="stIconMaterial"],
        span[class*="material-symbols"] {{
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
            font-weight: normal !important;
            font-style: normal !important;
            font-size: 24px !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            display: inline-block !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-feature-settings: 'liga' !important;
            -webkit-font-smoothing: antialiased !important;
        }}

        /* App Background & Base Text */
        .stApp {{
            background-color: {bg_main} !important;
            color: {text_primary} !important;
        }}

        h1, h2, h3, h4, h5, h6, .main-header, .page-title {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            letter-spacing: -0.025em;
            font-weight: 700;
            color: {text_primary} !important;
        }}

        p, span, label, div {{
            color: inherit;
        }}

        /* ============================================================
           SIDEBAR & NAVIGATION FIXES (High-Contrast Frames and Fonts)
           ============================================================ */
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {sidebar_border} !important;
        }}

        section[data-testid="stSidebar"] * {{
            color: {sidebar_text} !important;
        }}

        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] h4, 
        section[data-testid="stSidebar"] h5, 
        section[data-testid="stSidebar"] h6 {{
            color: {text_primary} !important;
            font-weight: 700 !important;
        }}

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {{
            color: {sidebar_text} !important;
        }}

        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] small {{
            color: {sidebar_subtext} !important;
        }}

        /* Left-side navigation links container */
        div[data-testid="stSidebarNav"],
        nav[data-testid="stSidebarNav"],
        div[data-testid="stSidebarNavSeparator"] {{
            background-color: transparent !important;
            padding-top: 10px !important;
            padding-bottom: 10px !important;
        }}

        /* Individual page link items in sidebar */
        div[data-testid="stSidebarNav"] ul,
        nav[data-testid="stSidebarNav"] ul,
        ul[data-testid="stSidebarNavItems"] {{
            gap: 6px !important;
            padding: 0 !important;
        }}

        div[data-testid="stSidebarNav"] li,
        nav[data-testid="stSidebarNav"] li,
        li[data-testid="stSidebarNavLink"] {{
            margin-bottom: 4px !important;
        }}

        div[data-testid="stSidebarNav"] a,
        nav[data-testid="stSidebarNav"] a,
        ul[data-testid="stSidebarNavItems"] a,
        li[data-testid="stSidebarNavLink"] a,
        a[data-testid="stSidebarNavLink"] {{
            background-color: {sidebar_nav_bg} !important;
            border: 1.5px solid {sidebar_nav_border} !important;
            border-radius: 10px !important;
            padding: 9px 14px !important;
            display: flex !important;
            align-items: center !important;
            text-decoration: none !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}

        div[data-testid="stSidebarNav"] a:hover,
        nav[data-testid="stSidebarNav"] a:hover,
        ul[data-testid="stSidebarNavItems"] a:hover,
        a[data-testid="stSidebarNavLink"]:hover {{
            background-color: {sidebar_nav_hover} !important;
            border-color: #6366F1 !important;
            transform: translateX(3px) !important;
        }}

        div[data-testid="stSidebarNav"] a *,
        nav[data-testid="stSidebarNav"] a *,
        ul[data-testid="stSidebarNavItems"] a *,
        li[data-testid="stSidebarNavLink"] *,
        a[data-testid="stSidebarNavLink"] * {{
            color: {sidebar_text} !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            letter-spacing: -0.01em !important;
        }}

        div[data-testid="stSidebarNav"] a svg,
        nav[data-testid="stSidebarNav"] a svg,
        a[data-testid="stSidebarNavLink"] svg {{
            fill: {sidebar_text} !important;
            stroke: {sidebar_text} !important;
        }}

        /* Active navigation link */
        div[data-testid="stSidebarNav"] a[aria-current="page"],
        nav[data-testid="stSidebarNav"] a[aria-current="page"],
        ul[data-testid="stSidebarNavItems"] a[aria-current="page"],
        a[data-testid="stSidebarNavLink"][aria-current="page"] {{
            background-color: {sidebar_nav_active} !important;
            border: 1.5px solid {sidebar_nav_active_border} !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
        }}

        div[data-testid="stSidebarNav"] a[aria-current="page"] *,
        nav[data-testid="stSidebarNav"] a[aria-current="page"] *,
        ul[data-testid="stSidebarNavItems"] a[aria-current="page"] *,
        a[data-testid="stSidebarNavLink"][aria-current="page"] * {{
            color: {sidebar_nav_active_text} !important;
            font-weight: 700 !important;
        }}

        div[data-testid="stSidebarNav"] a[aria-current="page"] svg,
        nav[data-testid="stSidebarNav"] a[aria-current="page"] svg,
        a[data-testid="stSidebarNavLink"][aria-current="page"] svg {{
            fill: {sidebar_nav_active_text} !important;
            stroke: {sidebar_nav_active_text} !important;
        }}

        button[data-testid="stSidebarCollapseButton"] {{
            color: {sidebar_text} !important;
        }}
        button[data-testid="stSidebarCollapseButton"] svg {{
            fill: {sidebar_text} !important;
            stroke: {sidebar_text} !important;
        }}

        /* Sidebar Buttons */
        section[data-testid="stSidebar"] div.stButton > button {{
            background-color: {btn_sec_bg} !important;
            color: {btn_sec_text} !important;
            border: 1px solid {btn_sec_border} !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }}

        section[data-testid="stSidebar"] div.stButton > button:hover {{
            background-color: {btn_sec_hover} !important;
            border-color: #6366F1 !important;
            color: #FFFFFF !important;
            transform: translateY(-1px) !important;
        }}

        section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35) !important;
        }}

        /* Radio buttons in sidebar */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label span {{
            color: {sidebar_text} !important;
            font-weight: 500 !important;
        }}

        /* ============================================================
           MAIN CONTENT TABS (st.tabs) STYLING FIX
           ============================================================ */
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
            background-color: {tab_bg} !important;
            border: 1px solid {tab_border} !important;
            border-radius: 12px !important;
            padding: 4px !important;
            gap: 4px !important;
        }}

        div[data-testid="stTabs"] button[data-baseweb="tab"] {{
            color: {tab_inactive_text} !important;
            border-radius: 8px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            padding: 8px 18px !important;
            border: none !important;
            background: transparent !important;
            transition: all 0.2s ease !important;
        }}

        div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
            color: {text_primary} !important;
            background-color: rgba(99, 102, 241, 0.1) !important;
        }}

        div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
            background-color: {tab_active_bg} !important;
            color: {tab_active_text} !important;
            border-bottom: 2.5px solid #6366F1 !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab-border"] {{
            display: none !important;
        }}

        /* ============================================================
           CARD & KPI METRIC TILES
           ============================================================ */
        .glass-card {{
            background: {bg_card} !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {border_card} !important;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin-bottom: 16px;
            color: {text_primary} !important;
        }}

        .glass-card:hover {{
            transform: translateY(-2px);
            border-color: #6366F1 !important;
        }}

        .kpi-tile {{
            background: {bg_card} !important;
            border: 1px solid {border_card} !important;
            border-radius: 14px;
            padding: 20px;
            text-align: left;
            position: relative;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            color: {text_primary} !important;
        }}

        .kpi-tile:hover {{
            border-color: #6366F1 !important;
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15) !important;
            transform: translateY(-2px);
        }}

        .kpi-icon {{
            font-size: 1.5rem;
            margin-bottom: 10px;
            display: inline-block;
        }}

        .kpi-label {{
            font-size: 0.8rem;
            color: {text_secondary} !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}

        .kpi-value {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 1.85rem;
            font-weight: 800;
            color: {text_primary} !important;
            line-height: 1.1;
        }}

        /* Grade Badges */
        .grade-pill {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 4px 12px;
            border-radius: 9999px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 700;
            font-size: 0.85rem;
            letter-spacing: 0.02em;
        }}

        .grade-aplus {{
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            color: white !important;
            box-shadow: 0 2px 6px rgba(16, 185, 129, 0.25);
        }}

        .grade-a {{
            background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%);
            color: white !important;
        }}

        .grade-bplus, .grade-b {{
            background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
            color: white !important;
            box-shadow: 0 2px 6px rgba(59, 130, 246, 0.25);
        }}

        .grade-cplus, .grade-c {{
            background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
            color: white !important;
        }}

        .grade-f {{
            background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
            color: white !important;
            box-shadow: 0 2px 6px rgba(239, 68, 68, 0.25);
        }}

        /* Main Buttons */
        div.stButton > button {{
            border-radius: 10px;
            font-weight: 600;
            letter-spacing: -0.01em;
            transition: all 0.2s ease;
            background-color: {btn_sec_bg} !important;
            color: {btn_sec_text} !important;
            border: 1px solid {btn_sec_border} !important;
        }}

        div.stButton > button:hover {{
            background-color: {btn_sec_hover} !important;
            border-color: #6366F1 !important;
            transform: translateY(-1px);
        }}

        div.stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
        }}

        div.stButton > button[kind="primary"]:hover {{
            box-shadow: 0 6px 18px rgba(79, 70, 229, 0.45) !important;
        }}

        /* Inputs & Selectboxes */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"] > input {{
            background-color: {input_bg} !important;
            border-color: {input_border} !important;
            color: {input_text} !important;
            border-radius: 8px !important;
        }}

        div[data-baseweb="select"] * {{
            color: {input_text} !important;
        }}

        div[data-baseweb="popover"],
        ul[data-baseweb="menu"] {{
            background-color: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 10px !important;
        }}

        li[data-baseweb="menu-item"],
        li[data-baseweb="menu-item"] * {{
            color: {input_text} !important;
        }}

        /* Sidebar Status Card */
        .sidebar-status-card {{
            background: {sidebar_nav_bg} !important;
            border: 1px solid {sidebar_border} !important;
            border-radius: 12px;
            padding: 12px;
            font-size: 0.85rem;
            color: {sidebar_subtext} !important;
        }}
        .sidebar-status-card strong {{
            color: {sidebar_text} !important;
        }}

        /* Dataframe Containers */
        div[data-testid="stDataFrame"] {{
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid {border_card} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

def render_theme_switcher():
    """Render Light / Dark mode toggle in sidebar with instant re-styling"""
    curr = get_current_theme()
    st.sidebar.markdown("""
    <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; 
                letter-spacing: 0.05em; margin-bottom: 4px; opacity: 0.85;">
        🌓 Display Theme
    </div>
    """, unsafe_allow_html=True)

    choice = st.sidebar.radio(
        "Display Theme:",
        options=["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if curr == "dark" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="theme_toggle_radio"
    )
    new_theme = "dark" if "Dark" in choice else "light"
    if new_theme != curr:
        st.session_state.app_theme = new_theme
        st.rerun()

def render_sidebar_header():
    """Render unified ApexTracker branding & theme switcher in sidebar"""
    st.sidebar.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <div style="background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%); color: white; width: 38px; height: 38px; border-radius: 10px; 
                    display: flex; align-items: center; justify-content: center; font-size: 19px; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.35);">🎓</div>
        <div>
            <h3 style="margin: 0; font-size: 1.12rem; font-weight: 800; letter-spacing: -0.02em;">ApexTracker</h3>
            <span style="font-size: 0.73rem; opacity: 0.8; font-weight: 600;">Academic Intelligence</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    render_theme_switcher()
    st.sidebar.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

def get_student_avatar_svg(name: str, size: int = 42) -> str:
    """Generate dynamic SVG initials avatar with consistent gradient"""
    clean_name = name.strip() if name else "ST"
    parts = clean_name.split()
    initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else (clean_name[:2].upper() if len(clean_name) >= 2 else "ST")
    
    hash_idx = int(hashlib.md5(clean_name.encode()).hexdigest(), 16) % len(AVATAR_GRADIENTS)
    bg_gradient, text_color = AVATAR_GRADIENTS[hash_idx]

    svg = f"""
    <div style="
        width: {size}px;
        height: {size}px;
        border-radius: 50%;
        background: {bg_gradient};
        color: {text_color};
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: {int(size * 0.42)}px;
        letter-spacing: -0.02em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        vertical-align: middle;
        margin-right: 10px;
    ">{initials}</div>
    """
    return svg

def render_kpi_card(label: str, value: str, subtext: str = "", icon: str = "📊", delta: str = None, delta_type: str = "positive") -> str:
    """Render a modern glassmorphic KPI tile directly to Streamlit and return HTML"""
    if delta and delta.startswith("#"):
        color = delta
        delta_badge = ""
    else:
        color = "#10B981" if delta_type in ("positive", "good") else ("#EF4444" if delta_type in ("negative", "bad") else "#64748B")
        delta_badge = f'<span style="background: {color}20; color: {color}; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; margin-left: 6px;">{delta}</span>' if delta else ''

    sub_html = f'<div class="kpi-sub" style="color: #94A3B8; font-size: 0.8rem; margin-top: 5px;">{subtext} {delta_badge}</div>' if (subtext or delta_badge) else ''

    html = f"""
    <div class="kpi-tile">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    return html

def render_grade_pill(grade: str) -> str:
    """Generate HTML pill badge for letter grades"""
    cls_map = {
        'A+': 'grade-aplus',
        'A': 'grade-a',
        'B+': 'grade-bplus',
        'B': 'grade-b',
        'C+': 'grade-cplus',
        'C': 'grade-c',
        'F': 'grade-f'
    }
    css_class = cls_map.get(grade, 'grade-c')
    return f'<span class="grade-pill {css_class}">{grade}</span>'

# Alias for backwards compatibility
render_grade_pill_html = render_grade_pill

def render_glass_card(content_html: str):
    """Render content inside a glassmorphic card"""
    st.markdown(f'<div class="glass-card">{content_html}</div>', unsafe_allow_html=True)

def render_role_selector() -> str:
    """Render top-level role simulation toggle in sidebar and return active role"""
    if 'user_role' not in st.session_state:
        st.session_state.user_role = "Teacher / Administrator"

    st.sidebar.markdown("""
    <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; 
                letter-spacing: 0.05em; margin-bottom: 4px; opacity: 0.85;">
        🎭 Portal Role Perspective
    </div>
    """, unsafe_allow_html=True)

    role = st.sidebar.radio(
        "View Perspective:",
        options=["Teacher / Administrator", "Student / Parent Portal"],
        index=0 if st.session_state.user_role == "Teacher / Administrator" else 1,
        label_visibility="collapsed",
        help="Switch perspectives to preview student/parent self-service experience vs admin management"
    )
    st.session_state.user_role = role

    role_badge = "👨‍🏫 Faculty Admin" if role.startswith("Teacher") else "🎓 Student Access"
    role_color = "#6366F1" if role.startswith("Teacher") else "#10B981"
    st.sidebar.markdown(f"""
    <div style="background: {role_color}25; color: {role_color}; border: 1px solid {role_color}50; 
                padding: 6px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; 
                text-align: center; margin-bottom: 15px;">
        {role_badge} Mode Active
    </div>
    """, unsafe_allow_html=True)
    return role
