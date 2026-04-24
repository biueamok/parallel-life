"""
平行人生 · Streamlit 主应用
P1 Landing+决策输入 → P2 价值观 PK → P3 平行时空对比（灵魂页）
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

from styles import CUSTOM_CSS
from mock_data import (
    VALUE_DIMENSIONS, VALUE_PK_PAIRS, SCENARIOS,
    DEFAULT_SEED_CONTEXT, SCENARIO_CATALOG,
)
from core import (
    model_options, quantify_values, solve_constraints,
    monte_carlo_simulate, time_discount, detect_biases,
    generate_parallel_narratives, get_dominant_value,
    run_full_pipeline, USE_LLM,
)
from narratives import YEAR_EMOJIS, YEAR_LABELS

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="平行人生 · Life Decision OS",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 初始化 session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "user_context" not in st.session_state:
    st.session_state.user_context = dict(DEFAULT_SEED_CONTEXT)
if "pk_results" not in st.session_state:
    st.session_state.pk_results = {}
if "pk_index" not in st.session_state:
    st.session_state.pk_index = 0
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None


# ============================================================
# 工具函数
# ============================================================
def render_step_indicator(current: int, total: int = 3):
    dots = "".join(
        f'<div class="step-dot {"step-dot-active" if i < current else ""}"></div>'
        for i in range(total)
    )
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)


def go_to_step(n: int):
    st.session_state.step = n
    st.rerun()


# ============================================================
# 页面 1：Landing + 决策输入
# ============================================================
def page_1_landing():
    render_step_indicator(1)
    # Hero
    st.markdown(
        """
        <div class="hero-container">
            <h1>平行人生</h1>
            <div class="hero-subtitle">在一个决定之前，先活一遍未来</div>
            <div class="hero-tagline">LIFE DECISION OS · POWERED BY MONTE CARLO × BEHAVIORAL ECONOMICS</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 免责 Banner
    st.markdown(
        '<div class="disclaimer-banner">🔒 本系统基于蒙特卡洛模拟与行为经济学模型，输出为概率分布而非预言；不存储任何用户输入</div>',
        unsafe_allow_html=True,
    )

    # 场景选择（仅职业转型可用，其他占位）
    st.markdown("#### 🎯 选择一个你正在面对的人生决策")
    cols = st.columns(3)
    for i, sc in enumerate(SCENARIO_CATALOG):
        with cols[i]:
            if sc["enabled"]:
                st.markdown(
                    f"""
                    <div class="life-card" style="cursor:pointer;min-height:140px;border:1px solid #6366F1;">
                        <div style="font-size:2rem;">{sc['emoji']}</div>
                        <div style="font-size:1.1rem;font-weight:700;margin-top:8px;">{sc['name']}</div>
                        <div style="font-size:0.85rem;color:#94A3B8;margin-top:6px;font-family:'Noto Serif SC',serif;">{sc['desc']}</div>
                        <div style="font-size:0.7rem;color:#A5B4FC;margin-top:10px;letter-spacing:0.1em;">✓ AVAILABLE</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="life-card" style="opacity:0.5;min-height:140px;border:1px dashed rgba(100,116,139,0.4);">
                        <div style="font-size:2rem;">{sc['emoji']}</div>
                        <div style="font-size:1.1rem;font-weight:700;margin-top:8px;color:#64748B;">{sc['name']}</div>
                        <div style="font-size:0.85rem;color:#64748B;margin-top:6px;font-family:'Noto Serif SC',serif;">{sc['desc']}</div>
                        <div style="font-size:0.7rem;color:#64748B;margin-top:10px;letter-spacing:0.1em;">⏳ COMING SOON</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # 决策输入
    st.markdown("#### 📝 描述你的处境")
    st.markdown(
        '<div style="font-size:0.85rem;color:#94A3B8;margin-bottom:10px;">越具体越好 — 系统会从你的原话里抽取你在意的词，并在「平行时空」里引用它们</div>',
        unsafe_allow_html=True,
    )

    raw_text = st.text_area(
        label="",
        value=st.session_state.user_context.get("raw_text", ""),
        height=140,
        placeholder="例如：我29岁了，在国企干了6年，月薪1万5稳定但一眼望到头。我说过自由对我最重要，但父母希望我稳定…",
        label_visibility="collapsed",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("🎂 年龄", 18, 70,
                              int(st.session_state.user_context.get("age", 29)))
    with c2:
        savings = st.number_input("💰 存款（万元）", 0, 10000,
                                  int(st.session_state.user_context.get("savings_wan", 40)))
    with c3:
        est_success = st.slider("🎯 你主观估计的「转型成功率」",
                                0.0, 1.0,
                                float(st.session_state.user_context.get("user_estimated_success", 0.55)),
                                0.05)

    # 硬约束
    st.markdown("#### 🔒 你的硬约束（可多选）")
    hard_constraints = st.multiselect(
        label="",
        options=["不能降薪", "必须陪家人", "不能负债", "不能异地", "不能高强度加班"],
        default=["必须陪家人"],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA
    c_left, c_mid, c_right = st.columns([1, 1, 1])
    with c_mid:
        if st.button("🌌 开启平行时空之旅 →", use_container_width=True, key="cta_1"):
            # 保存上下文
            st.session_state.user_context.update({
                "raw_text": raw_text,
                "age": age,
                "savings_wan": savings,
                "user_estimated_success": est_success,
                "hard_constraints": hard_constraints,
            })
            go_to_step(2)


# ============================================================
# 页面 2：价值观 PK
# ============================================================
def page_2_values():
    render_step_indicator(2)

    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    st.markdown("## 价值观校准")
    st.markdown(
        '<div style="color:#94A3B8;font-family:\'Noto Serif SC\',serif;margin-bottom:20px;">'
        '大多数决策痛苦不在于缺乏信息，而在于不清楚自己最在乎什么。<br>'
        '用 7 个两两取舍，找到你真实的价值指纹。</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    idx = st.session_state.pk_index
    total = len(VALUE_PK_PAIRS)

    # 进度
    st.progress((idx) / total, text=f"进度 {idx}/{total}")
    st.markdown("<br>", unsafe_allow_html=True)

    if idx < total:
        dim_a, dim_b = VALUE_PK_PAIRS[idx]
        info_a = VALUE_DIMENSIONS[dim_a]
        info_b = VALUE_DIMENSIONS[dim_b]

        st.markdown(
            '<div style="text-align:center;font-size:1.1rem;color:#CBD5E1;margin-bottom:20px;">'
            '如果只能保留一个，你选：</div>',
            unsafe_allow_html=True,
        )

        c1, c_vs, c2 = st.columns([5, 1, 5])
        with c1:
            st.markdown(
                f"""
                <div class="vs-card">
                    <div class="vs-card-emoji">{info_a['emoji']}</div>
                    <div class="vs-card-title">{info_a['name']}</div>
                    <div class="vs-card-desc">{info_a['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"选择 {info_a['emoji']} {info_a['name']}",
                         key=f"pk_{idx}_a", use_container_width=True):
                st.session_state.pk_results[(dim_a, dim_b)] = dim_a
                st.session_state.pk_index += 1
                st.rerun()

        with c_vs:
            st.markdown('<div class="vs-divider">VS</div>', unsafe_allow_html=True)

        with c2:
            st.markdown(
                f"""
                <div class="vs-card">
                    <div class="vs-card-emoji">{info_b['emoji']}</div>
                    <div class="vs-card-title">{info_b['name']}</div>
                    <div class="vs-card-desc">{info_b['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"选择 {info_b['emoji']} {info_b['name']}",
                         key=f"pk_{idx}_b", use_container_width=True):
                st.session_state.pk_results[(dim_a, dim_b)] = dim_b
                st.session_state.pk_index += 1
                st.rerun()
    else:
        # PK 完成：展示价值雷达
        weights = quantify_values(st.session_state.pk_results)
        st.session_state.user_context["value_weights"] = weights
        dominant = get_dominant_value(weights)
        dom_info = VALUE_DIMENSIONS[dominant]

        st.markdown(
            f'<div style="text-align:center;margin:10px 0 20px;">'
            f'<div style="color:#94A3B8;font-size:0.9rem;">你的价值指纹</div>'
            f'<div style="font-size:1.5rem;margin-top:6px;">主导维度 · {dom_info["emoji"]} <span class="highlight-gold">{dom_info["name"]}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 雷达图
        categories = [VALUE_DIMENSIONS[d]["name"] for d in weights.keys()]
        values = [weights[d] for d in weights.keys()]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            line=dict(color='#6366F1', width=3),
            fillcolor='rgba(99,102,241,0.3)',
            name='你的价值指纹',
        ))
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(15,23,42,0)',
                radialaxis=dict(visible=True, range=[0, max(values)*1.1],
                                tickfont=dict(color='#94A3B8', size=10),
                                gridcolor='rgba(148,163,184,0.2)'),
                angularaxis=dict(tickfont=dict(color='#E2E8F0', size=13),
                                 gridcolor='rgba(148,163,184,0.2)'),
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            height=440,
            margin=dict(l=50, r=50, t=30, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)

        # CTA
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("⚡ 启动平行时空模拟器 →", use_container_width=True, key="cta_2"):
                with st.spinner("🌌 正在模拟 1000 次平行人生..."):
                    result = run_full_pipeline(
                        scenario_id="career_transition",
                        user_context=st.session_state.user_context,
                        pk_results=st.session_state.pk_results,
                        hard_constraints=st.session_state.user_context.get("hard_constraints", []),
                    )
                    st.session_state.pipeline_result = result
                go_to_step(3)

        if st.button("🔄 重新校准", key="reset_pk"):
            st.session_state.pk_results = {}
            st.session_state.pk_index = 0
            st.rerun()


# ============================================================
# 页面 3：平行时空对比（灵魂页）
# ============================================================
def render_sankey(result):
    scenario = result["scenario"]
    nodes = scenario["sankey_nodes"]
    flows = scenario["sankey_flows"]

    node_colors = [
        "#6366F1",          # 起点
        "#0EA5E9", "#F97316",  # 两条路径
        "#38BDF8", "#0EA5E9", "#0369A1",  # 国企三档
        "#FB923C", "#F97316", "#C2410C",  # 创业三档
    ]
    link_colors = [
        "rgba(14,165,233,0.5)", "rgba(249,115,22,0.5)",
        "rgba(56,189,248,0.4)", "rgba(14,165,233,0.3)", "rgba(3,105,161,0.35)",
        "rgba(251,146,60,0.5)", "rgba(249,115,22,0.4)", "rgba(194,65,12,0.45)",
    ]

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=22, thickness=20,
            line=dict(color="rgba(148,163,184,0.3)", width=1),
            label=nodes,
            color=node_colors,
            hoverlabel=dict(bgcolor="#1E293B", font=dict(color="#F8FAFC")),
        ),
        link=dict(
            source=[f[0] for f in flows],
            target=[f[1] for f in flows],
            value=[f[2] for f in flows],
            color=link_colors,
            hoverlabel=dict(bgcolor="#1E293B", font=dict(color="#F8FAFC")),
        ),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#E2E8F0", size=12, family="Inter"),
        height=360,
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(text="🌌 命运分叉图 · 1000 次平行人生的流向", x=0.02,
                   font=dict(size=15, color="#F8FAFC")),
    )
    return fig


def render_dual_timeline(result):
    """双折线时间轴图：收入（含置信带）+ 幸福感"""
    years = [1, 3, 5, 10]
    sim = result["sim_results"]
    options = result["options"]

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        subplot_titles=("💰 年收入（万元）· 含 P20–P80 置信带", "😌 幸福指数（0–1）"),
        vertical_spacing=0.14,
        row_heights=[0.55, 0.45],
    )

    for opt in options:
        sid = opt["id"]
        color = opt["color"]
        p20 = [sim[sid][y]["income"]["p20"] for y in years]
        p50 = [sim[sid][y]["income"]["p50"] for y in years]
        p80 = [sim[sid][y]["income"]["p80"] for y in years]
        happiness = [sim[sid][y]["happiness"]["p50"] for y in years]

        # 置信带：p20-p80
        fig.add_trace(go.Scatter(
            x=years + years[::-1],
            y=p80 + p20[::-1],
            fill='toself',
            fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15)',
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False,
            hoverinfo='skip',
            name=f"{opt['name']} 置信带",
        ), row=1, col=1)

        # P50 主线
        fig.add_trace(go.Scatter(
            x=years, y=p50, mode='lines+markers',
            name=f"{opt['emoji']} {opt['name']}",
            line=dict(color=color, width=3),
            marker=dict(size=10, line=dict(color='white', width=2)),
            hovertemplate=f"{opt['name']}<br>第 %{{x}} 年<br>中位收入：¥%{{y:.1f}} 万<extra></extra>",
        ), row=1, col=1)

        # 幸福指数
        fig.add_trace(go.Scatter(
            x=years, y=happiness, mode='lines+markers',
            name=f"{opt['name']} 幸福",
            line=dict(color=color, width=2.5, dash='dot'),
            marker=dict(size=8),
            showlegend=False,
            hovertemplate=f"{opt['name']}<br>第 %{{x}} 年<br>幸福指数：%{{y:.2f}}<extra></extra>",
        ), row=2, col=1)

    fig.update_xaxes(
        title_text="年份（从今天开始）",
        tickvals=years, ticktext=[f"{y}年" for y in years],
        gridcolor='rgba(148,163,184,0.15)',
        color='#94A3B8', row=2, col=1,
    )
    fig.update_xaxes(gridcolor='rgba(148,163,184,0.15)', color='#94A3B8', row=1, col=1)
    fig.update_yaxes(gridcolor='rgba(148,163,184,0.15)', color='#94A3B8')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0', family='Inter', size=12),
        height=520,
        margin=dict(l=40, r=30, t=50, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.08,
                    xanchor='center', x=0.5,
                    bgcolor='rgba(30,41,59,0.5)',
                    bordercolor='rgba(148,163,184,0.2)',
                    borderwidth=1),
        hovermode='x unified',
    )
    for ann in fig['layout']['annotations']:
        ann['font'] = dict(color='#F8FAFC', size=13, family='Inter')
    return fig


def render_narrative_column(narr: dict, is_stable: bool):
    """渲染一列平行故事"""
    header_class = "option-header-stable" if is_stable else "option-header-adventure"
    outcome_label = {
        "optimistic": "顺境档 📈", "baseline": "常态档 ➡️", "pessimistic": "逆境档 📉"
    }[narr["outcome"]]

    st.markdown(
        f"""
        <div class="{header_class}">
            <div class="option-title">{narr['option_emoji']} {narr['option_name']}</div>
            <div class="option-subtitle">这条时间线被判定为：{outcome_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for tl in narr["timeline"]:
        st.markdown(
            f"""
            <div class="timeline-card">
                <div class="timeline-year">{tl['emoji']}  {tl['year_label']} · 年龄 {29 + tl['year']}</div>
                <div class="narrative-text">{tl['text']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 扎心总结
    st.markdown(
        f"""
        <div class="punchline">
            {narr['punchline']}
            <div class="punchline-disclaimer">
                以上为基于有限输入的概率模拟，不构成任何建议。真实的你，永远比模型更复杂。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_markdown_report(result) -> str:
    """生成可下载的 markdown 报告"""
    lines = [
        "# 🌌 平行人生 · 个人决策报告",
        f"\n> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "\n> 本报告由蒙特卡洛模拟 + 行为经济学模型生成，仅供决策参考。\n",
        "---\n",
        "## 一、你的价值指纹\n",
    ]
    for dim, w in sorted(result["value_weights"].items(), key=lambda kv: -kv[1]):
        info = VALUE_DIMENSIONS[dim]
        lines.append(f"- {info['emoji']} **{info['name']}**：{w*100:.1f}%")

    lines.append("\n---\n## 二、平行时空对比\n")
    for opt_id, narr in result["narratives"].items():
        lines.append(f"### {narr['option_emoji']} {narr['option_name']}\n")
        lines.append(f"*结局判定：{narr['outcome']}*\n")
        for tl in narr["timeline"]:
            lines.append(f"\n#### {tl['emoji']} {tl['year_label']}\n")
            lines.append(tl["text"])
        lines.append(f"\n> 💬 {narr['punchline']}\n")

    lines.append("\n---\n## 三、检测到的认知偏差\n")
    for b in result["biases"]:
        lines.append(f"- **{b['emoji']} {b['name']}**：{b['evidence']}")
        lines.append(f"  - 反思一问：*{b['reflection_question']}*")

    lines.append("\n---\n## 四、效用加权分\n")
    for oid, u in result["utilities"].items():
        name = next(o["name"] for o in result["options"] if o["id"] == oid)
        lines.append(f"- {name}: **{u:.4f}**")

    lines.append("\n\n---\n*平行人生 Life Decision OS · Powered by Monte Carlo × Behavioral Economics*")
    return "\n".join(lines)


def page_3_parallel_lives():
    """灵魂页：平行时空对比"""
    result = st.session_state.pipeline_result
    if not result:
        st.error("模拟数据缺失，请返回上一步重新触发")
        if st.button("← 返回"):
            go_to_step(2)
        return

    render_step_indicator(3)

    # Hero
    st.markdown(
        '<div class="hero-container" style="padding:1.5rem 1rem;">'
        '<h1 style="font-size:2rem;">你的平行人生</h1>'
        '<div class="hero-subtitle">基于 1000 次蒙特卡洛模拟 · 两个自己，同时在未来活着</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Sankey 分叉图
    st.plotly_chart(render_sankey(result), use_container_width=True, config={"displayModeBar": False})

    # 双折线时间轴
    st.plotly_chart(render_dual_timeline(result), use_container_width=True,
                    config={"displayModeBar": False})

    # 认知偏差检测弹窗
    if result["biases"]:
        st.markdown("#### ⚠️ 在继续阅读前，系统检测到你可能存在以下认知偏差")
        for b in result["biases"]:
            st.markdown(
                f"""
                <div class="bias-alert">
                    <div class="bias-title">{b['emoji']} 检测到【{b['name']}】</div>
                    <div class="bias-evidence">📍 证据：{b['evidence']}</div>
                    <div style="color:#FDE68A;font-size:13px;margin-top:10px;">💡 {b['explanation']}</div>
                    <div class="bias-reflection">🔍 反思一问：{b['reflection_question']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # 双栏平行故事
    st.markdown("### 📖 两条时间线上的你")
    st.markdown(
        '<div style="color:#94A3B8;font-family:\'Noto Serif SC\',serif;margin-bottom:20px;">'
        '不是推荐你选哪个。只是让你看见——每一条路的尽头，有什么在等你。</div>',
        unsafe_allow_html=True,
    )

    opt_ids = list(result["narratives"].keys())
    c_left, c_right = st.columns(2, gap="large")
    with c_left:
        render_narrative_column(result["narratives"][opt_ids[0]], is_stable=True)
    with c_right:
        render_narrative_column(result["narratives"][opt_ids[1]], is_stable=False)

    # 时间折现洞察（主区而非 sidebar，让它有更强存在感）
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("💡 打开「时间的真相」 · 为什么我们总是低估 10 年后的自己？", expanded=False):
        st.markdown(
            '<div style="color:#E2E8F0;font-family:\'Noto Serif SC\',serif;line-height:1.8;">'
            '人类有一种叫<b>「双曲折现」</b>的思维习惯——10 年后的 100 万，在我们今天心里不值 100 万。<br>'
            '这导致我们系统性地低估长期选项，高估短期收益。<br>'
            '下图展示了两个选项在「名义收入」和「折现后感受收入」（γ=0.9）之间的差异：</div>',
            unsafe_allow_html=True,
        )

        fig_discount = go.Figure()
        years = [1, 3, 5, 10]
        for opt in result["options"]:
            sid = opt["id"]
            nominal = [result["sim_results"][sid][y]["income"]["p50"] for y in years]
            discounted = [nominal[i] * (0.9 ** years[i]) for i in range(len(years))]
            fig_discount.add_trace(go.Scatter(
                x=years, y=nominal, mode='lines+markers',
                name=f"{opt['emoji']} {opt['name']} · 名义值",
                line=dict(color=opt["color"], width=3),
            ))
            fig_discount.add_trace(go.Scatter(
                x=years, y=discounted, mode='lines+markers',
                name=f"{opt['emoji']} {opt['name']} · 折现后",
                line=dict(color=opt["color"], width=2, dash="dash"),
            ))
        fig_discount.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0', family='Inter'),
            xaxis=dict(title="年份", gridcolor='rgba(148,163,184,0.15)', color='#94A3B8'),
            yaxis=dict(title="收入（万元）", gridcolor='rgba(148,163,184,0.15)', color='#94A3B8'),
            height=320, margin=dict(l=40, r=30, t=30, b=40),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        )
        st.plotly_chart(fig_discount, use_container_width=True, config={"displayModeBar": False})

        # 双数字对比
        nominal_10 = result["sim_results"]["entrepreneur"][10]["income"]["p50"]
        discounted_10 = nominal_10 * (0.9 ** 10)
        st.markdown(
            f"""
            <div class="discount-panel">
                <div style="text-align:center;font-family:'Noto Serif SC',serif;color:#C7D2FE;">
                    以「创业」10 年后的中位收入为例：
                </div>
                <div class="discount-numbers">
                    <div>
                        <div class="discount-label">名义值</div>
                        <div class="discount-num-big">¥ {nominal_10:,.1f} 万</div>
                    </div>
                    <div class="discount-arrow">→</div>
                    <div>
                        <div class="discount-label">折现后（γ=0.9, t=10）</div>
                        <div class="discount-num-small">¥ {discounted_10:,.1f} 万</div>
                    </div>
                </div>
                <div style="text-align:center;font-family:'Noto Serif SC',serif;color:#A78BFA;margin-top:10px;font-style:italic;">
                    这就是为什么「等 10 年再说」是大多数人的陷阱。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 底部：效用分 + 导出
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎯 最终提示")
    utilities = result["utilities"]
    opts_sorted = sorted(result["options"], key=lambda o: -utilities[o["id"]])
    top, second = opts_sorted[0], opts_sorted[1]
    diff_pct = (utilities[top["id"]] - utilities[second["id"]]) / max(utilities[second["id"]], 0.001) * 100

    st.markdown(
        f"""
        <div class="life-card" style="border-left:4px solid #10B981;">
            <div style="font-size:1rem;color:#94A3B8;margin-bottom:8px;">基于你的价值权重加权计算</div>
            <div style="font-size:1.3rem;color:#F8FAFC;font-family:'Noto Serif SC',serif;line-height:1.8;">
                <b>{top['emoji']} {top['name']}</b> 的综合效用比 <b>{second['emoji']} {second['name']}</b> 高约
                <span class="highlight-gold">{diff_pct:.1f}%</span>。
            </div>
            <div style="font-size:1rem;color:#94A3B8;margin-top:14px;font-family:'Noto Serif SC',serif;font-style:italic;">
                但这是概率，不是剧本。本系统不做决策——笔，始终在你手上。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 操作按钮
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        report_md = build_markdown_report(result)
        st.download_button(
            "📄 导出人生报告 (Markdown)",
            data=report_md.encode("utf-8"),
            file_name=f"parallel_life_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with c2:
        if st.button("🔄 重新校准价值观", use_container_width=True):
            st.session_state.pk_results = {}
            st.session_state.pk_index = 0
            go_to_step(2)
    with c3:
        if st.button("🏠 返回首页", use_container_width=True):
            for k in ["step", "pk_results", "pk_index", "pipeline_result"]:
                st.session_state.pop(k, None)
            st.rerun()


# ============================================================
# Sidebar：全局上下文说明
# ============================================================
with st.sidebar:
    st.markdown("## 🌌 平行人生")
    st.markdown("*Life Decision OS*")
    st.markdown("---")
    st.markdown(f"""
    **当前进度**  
    Step {st.session_state.step} / 3

    **模式**  
    {'🟢 LLM 模式' if USE_LLM else '🟡 模板模式（Demo）'}

    **核心引擎**
    - 🔧 选项建模器
    - ⚖️ 价值观量化器
    - 🔒 约束求解器
    - 🎲 蒙特卡洛模拟器
    - ⏳ 时间折现器
    - 🧠 认知偏差检测器
    - 📖 平行叙事引擎

    ---
    *架构预留：*  
    `USE_LLM=True` 即可切换到 GPT-4/Claude 实时生成个性化叙事
    """)


# ============================================================
# 路由
# ============================================================
if st.session_state.step == 1:
    page_1_landing()
elif st.session_state.step == 2:
    page_2_values()
elif st.session_state.step == 3:
    page_3_parallel_lives()
