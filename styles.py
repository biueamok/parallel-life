"""
平行人生 · 自定义 CSS 样式
强制覆盖 Streamlit 默认主题，打造影院级深色界面
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Serif+SC:wght@400;500;700&display=swap');

/* ========== 隐藏 Streamlit 默认元素 ========== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
.viewerBadge_container__1QSob {display: none;}
div[data-testid="stStatusWidget"] {display: none;}

/* ========== 全局深色主题 ========== */
html, body, [class*="css"], .stApp {
    background: linear-gradient(180deg, #0F172A 0%, #0B1120 100%) !important;
    color: #F8FAFC !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* ========== 标题排版 ========== */
h1, h2, h3, h4 {
    color: #F8FAFC !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 2.6rem !important;
    background: linear-gradient(135deg, #A5B4FC 0%, #F0ABFC 50%, #FCA5A5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem !important;
}

h2 { font-size: 1.6rem !important; }
h3 { font-size: 1.2rem !important; }

p, li, label, span, div {
    color: #E2E8F0;
}

/* ========== Hero 横幅 ========== */
.hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    background: radial-gradient(ellipse at top, rgba(99,102,241,0.15) 0%, transparent 70%);
    border-radius: 16px;
    margin-bottom: 1.5rem;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #94A3B8;
    font-family: 'Noto Serif SC', serif;
    font-style: italic;
    margin-top: 0.5rem;
    letter-spacing: 0.05em;
}
.hero-tagline {
    font-size: 0.85rem;
    color: #64748B;
    margin-top: 1rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* ========== 卡片通用 ========== */
.life-card {
    background: linear-gradient(135deg, #1E293B 0%, #182234 100%);
    border-radius: 14px;
    padding: 22px;
    margin: 12px 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    border: 1px solid rgba(148,163,184,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}
.life-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.45);
}

/* ========== 双栏分色边框（灵魂页核心） ========== */
.option-stable {
    border-left: 4px solid #0EA5E9;
    box-shadow: 0 4px 24px rgba(14,165,233,0.15);
}
.option-adventure {
    border-left: 4px solid #F97316;
    box-shadow: 0 4px 24px rgba(249,115,22,0.15);
}

.option-header-stable {
    background: linear-gradient(135deg, rgba(14,165,233,0.2), rgba(14,165,233,0.05));
    padding: 14px 18px;
    border-radius: 10px;
    border-left: 3px solid #0EA5E9;
    margin-bottom: 14px;
}
.option-header-adventure {
    background: linear-gradient(135deg, rgba(249,115,22,0.2), rgba(249,115,22,0.05));
    padding: 14px 18px;
    border-radius: 10px;
    border-left: 3px solid #F97316;
    margin-bottom: 14px;
}

.option-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #F8FAFC;
    margin: 0;
}
.option-subtitle {
    font-size: 0.85rem;
    color: #94A3B8;
    margin-top: 4px;
}

/* ========== 时间节点故事卡 ========== */
.timeline-card {
    background: rgba(30,41,59,0.6);
    border-radius: 10px;
    padding: 16px 18px;
    margin: 10px 0;
    border: 1px solid rgba(148,163,184,0.1);
    position: relative;
}
.timeline-year {
    display: inline-block;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    color: #94A3B8;
    text-transform: uppercase;
    margin-bottom: 8px;
    font-weight: 600;
}
.timeline-emoji {
    font-size: 1.4rem;
    margin-right: 8px;
}

/* ========== 叙事文本（衬线字体营造文学感） ========== */
.narrative-text {
    font-family: 'Noto Serif SC', serif;
    font-size: 15px;
    line-height: 1.9;
    color: #E2E8F0;
    letter-spacing: 0.01em;
}

/* ========== 扎心总结带 ========== */
.punchline {
    background: linear-gradient(135deg, rgba(127,29,29,0.25) 0%, rgba(30,41,59,0.8) 100%);
    border: 1px solid rgba(220,38,38,0.4);
    border-radius: 12px;
    padding: 18px 22px;
    margin-top: 18px;
    font-family: 'Noto Serif SC', serif;
    font-style: italic;
    color: #FCA5A5;
    font-size: 14.5px;
    line-height: 1.75;
    position: relative;
}
.punchline::before {
    content: '";
    font-size: 3rem;
    color: rgba(220,38,38,0.3);
    position: absolute;
    top: -10px;
    left: 10px;
    font-family: 'Noto Serif SC', serif;
}
.punchline-disclaimer {
    font-size: 11px;
    color: #64748B;
    margin-top: 10px;
    font-style: normal;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.03em;
}

/* ========== 偏差检测弹窗 ========== */
.bias-alert {
    background: linear-gradient(135deg, rgba(251,191,36,0.12) 0%, rgba(30,41,59,0.6) 100%);
    border: 1px solid rgba(251,191,36,0.4);
    border-radius: 12px;
    padding: 18px 20px;
    margin: 14px 0;
    color: #FDE68A;
}
.bias-title {
    font-weight: 700;
    color: #FCD34D;
    font-size: 1.05rem;
    margin-bottom: 10px;
}
.bias-evidence {
    color: #FDE68A;
    font-size: 13px;
    background: rgba(0,0,0,0.2);
    padding: 8px 12px;
    border-radius: 6px;
    margin: 8px 0;
    font-family: 'Noto Serif SC', serif;
}
.bias-reflection {
    color: #FEF3C7;
    font-style: italic;
    font-family: 'Noto Serif SC', serif;
    font-size: 14px;
    margin-top: 10px;
    padding-left: 12px;
    border-left: 2px solid #FCD34D;
}

/* ========== 时间折现面板 ========== */
.discount-panel {
    background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(30,41,59,0.8) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 12px;
    padding: 18px;
    margin: 12px 0;
}
.discount-numbers {
    display: flex;
    align-items: center;
    justify-content: space-around;
    margin: 14px 0;
    font-family: 'Inter', sans-serif;
}
.discount-num-big {
    font-size: 1.6rem;
    font-weight: 700;
    color: #F8FAFC;
}
.discount-num-small {
    font-size: 1.3rem;
    font-weight: 700;
    color: #A78BFA;
}
.discount-label {
    font-size: 0.75rem;
    color: #94A3B8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.discount-arrow {
    font-size: 1.5rem;
    color: #6366F1;
}

/* ========== 按钮主题 ========== */
.stButton > button {
    background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%) !important;
    color: white !important;
    border: none !important;
    padding: 12px 32px !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(236,72,153,0.4) !important;
}
.stButton > button:active { transform: translateY(0); }

/* Secondary 按钮 */
.stButton > button[kind="secondary"] {
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(148,163,184,0.3) !important;
    box-shadow: none !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* ========== 输入控件 ========== */
.stTextInput > div > div > input,
.stTextArea textarea {
    background: rgba(15,23,42,0.7) !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(148,163,184,0.25) !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    padding: 12px 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
}

/* 滑块 */
.stSlider [data-baseweb="slider"] > div > div > div {
    background: linear-gradient(90deg, #6366F1, #EC4899) !important;
}
.stSlider [role="slider"] {
    background: #F8FAFC !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.4) !important;
}

/* 单选/多选 */
.stRadio > div {
    background: transparent !important;
    gap: 10px;
}
.stRadio label {
    background: rgba(30,41,59,0.5);
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid rgba(148,163,184,0.15);
    transition: all 0.2s;
}
.stRadio label:hover {
    background: rgba(30,41,59,0.8);
    border-color: rgba(99,102,241,0.5);
}

/* 进度条 */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6366F1, #EC4899) !important;
}

/* ========== 价值观 PK 卡片 ========== */
.vs-card {
    background: linear-gradient(135deg, #1E293B 0%, #182234 100%);
    border-radius: 14px;
    padding: 28px;
    margin: 8px;
    text-align: center;
    border: 2px solid rgba(148,163,184,0.1);
    cursor: pointer;
    transition: all 0.25s ease;
    min-height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.vs-card:hover {
    border-color: #6366F1;
    transform: scale(1.02);
    box-shadow: 0 8px 28px rgba(99,102,241,0.3);
}
.vs-card-emoji { font-size: 2.4rem; margin-bottom: 8px; }
.vs-card-title { font-size: 1.2rem; font-weight: 700; color: #F8FAFC; margin: 6px 0; }
.vs-card-desc { font-size: 0.85rem; color: #94A3B8; font-family: 'Noto Serif SC', serif; }

.vs-divider {
    text-align: center;
    font-size: 1.3rem;
    color: #6366F1;
    font-weight: 800;
    letter-spacing: 0.2em;
    padding: 20px 0;
}

/* ========== 示例场景芯片 ========== */
.scenario-chip {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 20px;
    padding: 6px 14px;
    margin: 4px;
    font-size: 0.85rem;
    color: #C7D2FE;
    cursor: pointer;
    transition: all 0.2s;
}
.scenario-chip:hover {
    background: rgba(99,102,241,0.3);
}
.scenario-chip-disabled {
    display: inline-block;
    background: rgba(71,85,105,0.2);
    border: 1px dashed rgba(100,116,139,0.4);
    border-radius: 20px;
    padding: 6px 14px;
    margin: 4px;
    font-size: 0.85rem;
    color: #64748B;
}

/* ========== 免责 Banner ========== */
.disclaimer-banner {
    background: rgba(30,41,59,0.6);
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 1rem;
    font-size: 0.78rem;
    color: #94A3B8;
    text-align: center;
    letter-spacing: 0.02em;
}

/* ========== 步骤指示器 ========== */
.step-indicator {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin: 0 0 2rem 0;
}
.step-dot {
    width: 36px;
    height: 4px;
    background: rgba(148,163,184,0.2);
    border-radius: 2px;
}
.step-dot-active {
    background: linear-gradient(90deg, #6366F1, #EC4899);
    box-shadow: 0 0 10px rgba(99,102,241,0.5);
}

/* ========== 雷达图 & 图表容器 ========== */
[data-testid="stPlotlyChart"] {
    background: transparent;
    border-radius: 12px;
    overflow: hidden;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(30,41,59,0.5) !important;
    border-radius: 10px !important;
    color: #F8FAFC !important;
    font-weight: 600 !important;
}

/* Sidebar 背景 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1120 0%, #0F172A 100%);
    border-right: 1px solid rgba(148,163,184,0.1);
}
[data-testid="stSidebar"] h2 {
    font-size: 1.1rem !important;
    color: #A5B4FC !important;
}

/* 滚动条 */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #0F172A; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #6366F1, #EC4899);
    border-radius: 4px;
}

/* 金色点缀：关键数值 */
.highlight-gold {
    color: #FBBF24;
    font-weight: 700;
}
.highlight-blue { color: #38BDF8; font-weight: 700; }
.highlight-orange { color: #FB923C; font-weight: 700; }

/* ============================================================
   📱 移动端响应式适配（核心新增）
   ============================================================ */
@media (max-width: 768px) {
    /* 主容器：收窄内边距 */
    .main .block-container {
        padding: 0.6rem 0.7rem 2rem !important;
        max-width: 100% !important;
    }

    /* 标题：降字号，避免溢出 */
    h1 { font-size: 1.7rem !important; line-height: 1.25 !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.05rem !important; }

    /* Hero 区 */
    .hero-container {
        padding: 1.2rem 0.6rem 0.8rem !important;
    }
    .hero-subtitle { font-size: 0.95rem !important; }
    .hero-tagline { font-size: 0.65rem !important; letter-spacing: 0.08em !important; }

    /* 卡片：降低内边距 + 降低 min-height */
    .life-card {
        padding: 14px 13px !important;
        margin: 8px 0 !important;
        border-radius: 12px !important;
    }

    /* 场景卡网格：让三列场景卡强制堆叠（通过 columns 子元素） */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 8px !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* 价值观 PK 卡片 */
    .vs-card {
        padding: 18px 14px !important;
        min-height: 110px !important;
    }
    .vs-card-emoji { font-size: 2rem !important; }
    .vs-card-title { font-size: 1.05rem !important; }
    .vs-card-desc { font-size: 0.8rem !important; }
    .vs-divider {
        font-size: 1rem !important;
        padding: 10px 0 !important;
        letter-spacing: 0.15em !important;
    }

    /* 按钮：全宽、更大点击区 */
    .stButton > button,
    .stDownloadButton > button {
        width: 100% !important;
        padding: 14px 16px !important;
        font-size: 0.95rem !important;
        letter-spacing: 0 !important;
    }

    /* 时间线卡片：降低行距 */
    .timeline-card {
        padding: 13px 14px !important;
        margin: 8px 0 !important;
    }
    .narrative-text {
        font-size: 14px !important;
        line-height: 1.8 !important;
    }

    /* 扎心总结 */
    .punchline {
        padding: 14px 16px !important;
        font-size: 13.5px !important;
        line-height: 1.7 !important;
    }
    .punchline-disclaimer { font-size: 10.5px !important; }

    /* 偏差弹窗 */
    .bias-alert {
        padding: 13px 14px !important;
    }
    .bias-title { font-size: 0.98rem !important; }
    .bias-evidence { font-size: 12px !important; }

    /* 时间折现面板 */
    .discount-panel { padding: 14px !important; }
    .discount-numbers {
        flex-direction: column !important;
        gap: 10px !important;
    }
    .discount-arrow { transform: rotate(90deg); }
    .discount-num-big { font-size: 1.3rem !important; }
    .discount-num-small { font-size: 1.1rem !important; }

    /* 步骤指示器 */
    .step-dot { width: 28px !important; }

    /* 免责 Banner */
    .disclaimer-banner {
        font-size: 0.72rem !important;
        padding: 8px 12px !important;
    }

    /* Option header */
    .option-header-stable,
    .option-header-adventure {
        padding: 12px 14px !important;
    }
    .option-title { font-size: 1.1rem !important; }
    .option-subtitle { font-size: 0.78rem !important; }

    /* 输入框：更易点击 */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    [data-testid="stNumberInput"] input {
        font-size: 16px !important;  /* iOS 16px 不触发缩放 */
        padding: 12px 12px !important;
    }

    /* Sidebar：移动端折叠更彻底 */
    [data-testid="stSidebar"] {
        min-width: 0 !important;
    }

    /* Plotly 图表容器：限制高度 */
    .js-plotly-plot {
        font-size: 11px !important;
    }

    /* 多选/下拉 */
    .stMultiSelect [data-baseweb="select"] {
        font-size: 14px !important;
    }
}

/* 超小屏幕（< 480px） */
@media (max-width: 480px) {
    h1 { font-size: 1.5rem !important; }
    .hero-container { padding: 1rem 0.4rem 0.6rem !important; }
    .narrative-text { font-size: 13.5px !important; }
    .vs-card-title { font-size: 1rem !important; }
    .life-card { padding: 12px 11px !important; }
}

/* ============================================================
   💎 Landing 引导组件（新增，配合友好化改造）
   ============================================================ */
.guide-strip {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(236,72,153,0.08));
    border-left: 3px solid #A78BFA;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 14px 0;
    color: #E2E8F0;
    font-family: 'Noto Serif SC', serif;
    line-height: 1.8;
    font-size: 14.5px;
}
.guide-strip b { color: #FCD34D; }

.example-chip {
    display: inline-block;
    background: rgba(99,102,241,0.18);
    border: 1px solid rgba(165,180,252,0.45);
    border-radius: 18px;
    padding: 7px 14px;
    margin: 4px 4px 4px 0;
    font-size: 0.82rem;
    color: #E0E7FF;
    cursor: pointer;
    transition: all 0.2s;
}
.example-chip:hover {
    background: rgba(99,102,241,0.32);
    transform: translateY(-1px);
}

.kpi-row {
    display: flex;
    gap: 10px;
    margin: 14px 0;
    flex-wrap: wrap;
}
.kpi-chip {
    background: rgba(30,41,59,0.7);
    border: 1px solid rgba(148,163,184,0.2);
    border-radius: 10px;
    padding: 10px 14px;
    min-width: 100px;
    flex: 1;
}
.kpi-label {
    font-size: 0.7rem;
    color: #94A3B8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.kpi-value {
    font-size: 1.15rem;
    color: #F8FAFC;
    font-weight: 700;
    margin-top: 3px;
}

/* LLM 开关徽标 */
.llm-badge-on {
    display: inline-block;
    background: linear-gradient(135deg, #10B981, #059669);
    color: white;
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(16,185,129,0.3);
}
.llm-badge-off {
    display: inline-block;
    background: rgba(148,163,184,0.25);
    color: #CBD5E1;
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    font-weight: 700;
}

/* 读图引导 */
.reading-guide {
    background: rgba(6,78,59,0.22);
    border: 1px solid rgba(52,211,153,0.4);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 10px 0 18px;
    font-size: 13.5px;
    color: #A7F3D0;
    line-height: 1.7;
    font-family: 'Noto Serif SC', serif;
}
.reading-guide b { color: #FEF3C7; }
</style>
"""
