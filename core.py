"""
平行人生 · 核心决策引擎（7 大模块）
- 选项建模器 · 价值观量化器 · 约束求解器
- 蒙特卡洛模拟器 · 时间折现器 · 认知偏差检测器
- 叙事引擎（含 LLM stub 升级路径）
"""
from __future__ import annotations
import numpy as np
from typing import Dict, List, Any, Optional

from mock_data import (
    VALUE_DIMENSIONS, VALUE_PK_PAIRS, SCENARIOS,
    BIAS_PATTERNS, KEYWORD_BANK, DEFAULT_SEED_CONTEXT,
)
from narratives import get_narrative, get_punchline, YEAR_EMOJIS, YEAR_LABELS

# ============================================================
# LLM 升级开关（动态：有 API Key 时自动启用 DeepSeek）
# ============================================================
try:
    from llm_client import (
        is_available as _llm_available,
        generate_timeline_narrative as _llm_narrative,
        generate_punchline as _llm_punchline,
    )
    LLM_CLIENT_LOADED = True
except Exception:
    LLM_CLIENT_LOADED = False
    def _llm_available() -> bool:
        return False


def USE_LLM() -> bool:  # 保留旧命名，改为函数避免启动时固化
    """运行时判断：有 Key 且模块加载成功时启用"""
    return LLM_CLIENT_LOADED and _llm_available()


# ============================================================
# 模块 1：选项建模器
# ============================================================
def model_options(scenario_id: str, user_context: Dict) -> List[Dict]:
    """
    把场景配置转化为结构化决策选项。
    Args:
        scenario_id: 场景 id
        user_context: 用户上下文（年龄/存款等）
    Returns:
        [Option, ...] 结构化选项列表
    """
    scenario = SCENARIOS[scenario_id]
    options = []
    for opt_id, opt_data in scenario["options"].items():
        options.append({
            "id": opt_id,
            "name": opt_data["name"],
            "short_desc": opt_data["short_desc"],
            "color": opt_data["color"],
            "emoji": opt_data["emoji"],
            "params": opt_data["params"],
            "outcome_probs": opt_data["outcome_probs"],
            "reversible": opt_id == "stay_soe",  # 留国企相对可逆
        })
    return options


# ============================================================
# 模块 2：价值观量化器（强制两两取舍 → 归一化权重）
# ============================================================
def quantify_values(pk_results: Dict[tuple, str]) -> Dict[str, float]:
    """
    根据两两 PK 结果计算价值权重（AHP 简化版）。
    Args:
        pk_results: {(dim_a, dim_b): winner_dim}
    Returns:
        {dim: weight} 归一化后权重（和=1.0）
    """
    scores = {dim: 1.0 for dim in VALUE_DIMENSIONS}
    for (a, b), winner in pk_results.items():
        if winner == a:
            scores[a] += 1.2
            scores[b] *= 0.85
        elif winner == b:
            scores[b] += 1.2
            scores[a] *= 0.85
    total = sum(scores.values())
    return {dim: round(v / total, 4) for dim, v in scores.items()}


def get_dominant_value(weights: Dict[str, float]) -> str:
    """取权重最高的维度作为叙事主线"""
    return max(weights.items(), key=lambda kv: kv[1])[0]


# ============================================================
# 模块 3：约束求解器
# ============================================================
def solve_constraints(options: List[Dict], hard_constraints: List[str],
                      user_context: Dict) -> Dict[str, Any]:
    """
    硬约束过滤 + 弹性约束打分。
    Args:
        hard_constraints: 勾选的硬约束列表（如 '不能负债', '必须陪家人'）
    Returns:
        {'feasible': [opt_id,...], 'warnings': [{opt_id, reason},...]}
    """
    feasible = []
    warnings = []
    for opt in options:
        violated = []
        if "不能降薪" in hard_constraints and opt["params"]["income_mu"] < user_context.get("current_income", 18):
            violated.append(f"初期预期收入 ¥{opt['params']['income_mu']:.0f} 万，可能触发降薪")
        if "必须陪家人" in hard_constraints and opt["params"]["family_time_score"] < 0.5:
            violated.append(f"家庭时间评分仅 {opt['params']['family_time_score']*100:.0f}%，可能无法兼顾")
        if "不能负债" in hard_constraints and opt["params"]["failure_prob"] > 0.35:
            violated.append(f"失败概率 {opt['params']['failure_prob']*100:.0f}%，有负债风险")

        if violated:
            warnings.append({"opt_id": opt["id"], "reasons": violated})
        feasible.append(opt["id"])  # Demo 中不真正过滤，仅给出警告
    return {"feasible": feasible, "warnings": warnings}


# ============================================================
# 模块 4：蒙特卡洛模拟器
# ============================================================
def monte_carlo_simulate(option: Dict, years: List[int] = None,
                         N: int = 1000, seed: int = 42) -> Dict:
    """
    对单个选项进行 N 次抽样模拟，返回多时间点的概率分布。
    Returns:
        {year: {
            'income': {p20, p50, p80, mean, samples},
            'happiness': {...},
            'achievement': {...}
        }}
    """
    if years is None:
        years = [1, 3, 5, 10]
    np.random.seed(seed + hash(option["id"]) % 1000)

    p = option["params"]
    results = {}

    for y in years:
        # --- 收入模拟：对数正态 + 失败事件 ---
        # 累计增长的对数均值
        log_mu = np.log(p["income_mu"]) + p["growth_rate"] * y
        # 方差随时间扩散
        log_sigma = p["income_sigma"] * np.sqrt(y)
        income = np.random.lognormal(mean=log_mu, sigma=log_sigma, size=N)

        # 创业有失败事件：累计失败概率 = 1 - (1-p)^y
        if p["failure_prob"] > 0.1:
            cumulative_fail = 1 - (1 - p["failure_prob"]) ** min(y, 5)
            failed = np.random.random(N) < cumulative_fail
            # 失败后：残值按一个较低区间分布
            income[failed] = np.random.uniform(8, 20, size=failed.sum())

        # 数值 clip（防止荒谬输出）
        income = np.clip(income, 3, p["income_ceiling"])

        # --- 幸福感模拟：基线 + 自主性加成 - 风险焦虑 ---
        happiness = (
            p["happiness_base"]
            + p["autonomy_score"] * 0.3
            - p["risk_factor"] * np.random.random(N) * 0.5
            + np.random.normal(0, 0.1, size=N)
        )
        happiness = np.clip(happiness, 0, 1)

        # --- 成就感模拟 ---
        achievement = (
            p["achievement_ceiling"] * (1 - np.exp(-y / 6))  # 饱和曲线
            + np.random.normal(0, 0.08, size=N)
        )
        achievement = np.clip(achievement, 0, 1)

        results[y] = {
            "income": {
                "p20": float(np.percentile(income, 20)),
                "p50": float(np.percentile(income, 50)),
                "p80": float(np.percentile(income, 80)),
                "mean": float(income.mean()),
                "std": float(income.std()),
                "samples": income,
            },
            "happiness": {
                "p20": float(np.percentile(happiness, 20)),
                "p50": float(np.percentile(happiness, 50)),
                "p80": float(np.percentile(happiness, 80)),
                "mean": float(happiness.mean()),
            },
            "achievement": {
                "p50": float(np.percentile(achievement, 50)),
                "mean": float(achievement.mean()),
            },
        }
    return results


def classify_outcome(sim_result: Dict, final_year: int = 10) -> str:
    """根据 10 年后收入分位，判定整体结局档"""
    final = sim_result[final_year]
    p50, p20, p80 = final["income"]["p50"], final["income"]["p20"], final["income"]["p80"]
    if p50 > (p20 + p80) / 2 * 1.2:
        return "optimistic"
    elif p50 < (p20 + p80) / 2 * 0.85:
        return "pessimistic"
    return "baseline"


# ============================================================
# 模块 5：时间折现器
# ============================================================
def time_discount(nominal_values: Dict[int, float], gamma: float = 0.9) -> Dict:
    """
    指数折现，计算 NPV 及折现曲线。
    Args:
        nominal_values: {year: value}
        gamma: 年折现系数（0.9 ≈ 双曲折现温和版）
    Returns:
        {
            'discounted': {year: value},
            'nominal_curve': [(year, value)],
            'discounted_curve': [(year, value)],
            'npv': 总折现值
        }
    """
    discounted = {y: v * (gamma ** y) for y, v in nominal_values.items()}
    npv = sum(discounted.values())
    years = sorted(nominal_values.keys())
    return {
        "discounted": discounted,
        "nominal_curve": [(y, nominal_values[y]) for y in years],
        "discounted_curve": [(y, discounted[y]) for y in years],
        "npv": npv,
        "gamma": gamma,
    }


# ============================================================
# 模块 6：认知偏差检测器
# ============================================================
def detect_biases(user_context: Dict) -> List[Dict]:
    """
    识别用户决策中的认知偏差。
    Returns:
        [{'id', 'name', 'emoji', 'evidence', 'explanation', 'reflection_question'}, ...]
    """
    alerts = []
    for bias_id, pattern in BIAS_PATTERNS.items():
        try:
            if pattern["trigger_check"](user_context):
                # 提取证据
                evidence_parts = []
                raw = user_context.get("raw_text", "")
                for kw in pattern.get("trigger_keywords", []):
                    if kw in raw:
                        evidence_parts.append(f"你在描述中提到了「{kw}」")
                        break
                if not evidence_parts:
                    # 从 value_weights 提取
                    if bias_id == "loss_aversion":
                        w = user_context.get("value_weights", {}).get("wealth", 0)
                        evidence_parts.append(f"你对财富维度的权重打到了 {w*100:.0f}%（高于同年龄段均值约 22%）")
                    elif bias_id == "status_quo":
                        sw = user_context.get("stability_weight", 0)
                        evidence_parts.append(f"你对「稳定」相关表达的权重达 {sw*100:.0f}%")
                    elif bias_id == "overconfidence":
                        p = user_context.get("user_estimated_success", 0)
                        evidence_parts.append(f"你主观估计成功率 {p*100:.0f}%，高于实际创业 5 年存活率 18%")
                    elif bias_id == "anchoring":
                        num = user_context.get("reference_number", 0)
                        evidence_parts.append(f"你在决策中多次提及 ¥{num} 万这一参照值")
                    else:
                        evidence_parts.append("从你的语言模式中识别到典型信号")

                alerts.append({
                    "id": bias_id,
                    "name": pattern["name"],
                    "emoji": pattern["emoji"],
                    "evidence": "；".join(evidence_parts),
                    "explanation": pattern["explanation"],
                    "reflection_question": pattern["reflection_question"],
                })
        except Exception:
            continue
    # 最多展示 3 个（避免用户被打断太多）
    return alerts[:3]


# ============================================================
# 模块 7：叙事引擎
# ============================================================
def extract_user_tokens(raw_text: str, value_weights: Dict[str, float]) -> Dict[str, str]:
    """
    从用户输入中抽取原词。无 jieba 时退化为关键词匹配。
    Returns:
        {'user_value_keyword': '自由', 'user_raw_concern': '女儿', ...}
    """
    # 简易关键词抽取（避免强依赖 jieba）
    found = {}  # dim -> 第一个命中词
    for dim_key, keywords in KEYWORD_BANK.items():
        for kw in keywords:
            if kw in raw_text:
                found[dim_key] = kw
                break

    # 主关键词：优先取 value_weights top1 对应的词，fallback 到原词命中最多的
    dominant = get_dominant_value(value_weights) if value_weights else "freedom"
    value_keyword = found.get(dominant) or found.get("freedom") or "自由"

    # 关注词：取 relation 族的词（通常是 "女儿"/"父母"/"老婆"）
    concern = found.get("relation") or "家人"

    return {
        "user_value_keyword": value_keyword,
        "user_raw_concern": concern,
        "user_raw_phrase": raw_text[:30] if raw_text else "",
    }


def generate_parallel_narratives(options: List[Dict], sim_results: Dict[str, Dict],
                                 value_weights: Dict[str, float],
                                 user_context: Dict,
                                 years: List[int] = None) -> Dict:
    """
    为两个选项生成平行叙事。
    Returns:
        {
            option_id: {
                'outcome': 'optimistic|baseline|pessimistic',
                'timeline': [{year, emoji, text}, ...],
                'punchline': str,
            }
        }
    """
    if years is None:
        years = [1, 3, 5, 10]

    dom_value = get_dominant_value(value_weights)
    user_tokens = extract_user_tokens(user_context.get("raw_text", ""), value_weights)
    age = user_context.get("age", 29)

    narratives = {}
    for opt in options:
        opt_id = opt["id"]
        sim = sim_results[opt_id]
        outcome = classify_outcome(sim)

        timeline = []
        for y in years:
            income = sim[y]["income"]["p50"]
            happiness = sim[y]["happiness"]["p50"]
            fallback_text = get_narrative(
                option_id=opt_id,
                value_dim=dom_value,
                outcome=outcome,
                year=y,
                user_tokens=user_tokens,
                income=income,
                age=age,
            )

            # 有 LLM Key 时调用真实 DeepSeek，失败自动回退模板
            if USE_LLM():
                text = _llm_narrative(
                    option_name=opt["name"],
                    option_emoji=opt["emoji"],
                    year=y,
                    age=age,
                    income=income,
                    happiness=happiness,
                    outcome=outcome,
                    dominant_value=VALUE_DIMENSIONS.get(dom_value, {}).get("name", dom_value),
                    user_raw_text=user_context.get("raw_text", ""),
                    user_value_keyword=user_tokens.get("user_value_keyword", ""),
                    user_concern_keyword=user_tokens.get("user_raw_concern", ""),
                    fallback_text=fallback_text,
                )
            else:
                text = fallback_text

            timeline.append({
                "year": y,
                "year_label": YEAR_LABELS[y],
                "emoji": YEAR_EMOJIS[y],
                "text": text,
                "income_p50": income,
                "happiness_p50": happiness,
            })

        # 扎心总结：LLM 或模板
        template_punch = get_punchline(opt_id, outcome, user_tokens)
        if USE_LLM():
            punchline = _llm_punchline(
                option_name=opt["name"],
                outcome=outcome,
                user_raw_text=user_context.get("raw_text", ""),
                user_value_keyword=user_tokens.get("user_value_keyword", ""),
                fallback_text=template_punch,
            )
        else:
            punchline = template_punch

        narratives[opt_id] = {
            "option_name": opt["name"],
            "option_emoji": opt["emoji"],
            "color": opt["color"],
            "outcome": outcome,
            "timeline": timeline,
            "punchline": punchline,
        }
    return narratives


# ============================================================
# 汇总：一键跑通全流程
# ============================================================
def run_full_pipeline(scenario_id: str = "career_transition",
                      user_context: Optional[Dict] = None,
                      pk_results: Optional[Dict] = None,
                      hard_constraints: Optional[List[str]] = None) -> Dict:
    """
    从上下文→选项→价值→约束→模拟→叙事的完整流程。
    适合 Demo 一键体验。
    """
    if user_context is None:
        user_context = dict(DEFAULT_SEED_CONTEXT)
    if hard_constraints is None:
        hard_constraints = []

    # 1. 选项建模
    options = model_options(scenario_id, user_context)

    # 2. 价值量化（若无 PK 结果，用默认权重）
    if pk_results:
        value_weights = quantify_values(pk_results)
    else:
        value_weights = user_context.get("value_weights", {dim: 1/6 for dim in VALUE_DIMENSIONS})
    user_context["value_weights"] = value_weights

    # 3. 约束求解
    constraint_report = solve_constraints(options, hard_constraints, user_context)

    # 4. 蒙特卡洛
    sim_results = {opt["id"]: monte_carlo_simulate(opt) for opt in options}

    # 5. 时间折现（以收入 P50 为例）
    discounts = {}
    for opt in options:
        nominal = {y: sim_results[opt["id"]][y]["income"]["p50"] for y in [1, 3, 5, 10]}
        discounts[opt["id"]] = time_discount(nominal)

    # 6. 偏差检测
    biases = detect_biases(user_context)

    # 7. 叙事生成
    narratives = generate_parallel_narratives(options, sim_results, value_weights, user_context)

    # 汇总效用分（价值加权）
    utilities = {}
    for opt in options:
        p = opt["params"]
        u = (
            value_weights.get("wealth", 0) * min(sim_results[opt["id"]][10]["income"]["p50"] / 100, 1.0) +
            value_weights.get("freedom", 0) * p["autonomy_score"] +
            value_weights.get("achievement", 0) * p["achievement_ceiling"] +
            value_weights.get("relation", 0) * p["family_time_score"] +
            value_weights.get("health", 0) * (1 - p["risk_factor"]) +
            value_weights.get("meaning", 0) * p["meaning_score"]
        )
        utilities[opt["id"]] = round(u, 4)

    return {
        "scenario": SCENARIOS[scenario_id],
        "user_context": user_context,
        "options": options,
        "value_weights": value_weights,
        "constraint_report": constraint_report,
        "sim_results": sim_results,
        "discounts": discounts,
        "biases": biases,
        "narratives": narratives,
        "utilities": utilities,
    }


# 简易自测
if __name__ == "__main__":
    result = run_full_pipeline()
    print("=" * 60)
    print(f"场景: {result['scenario']['name']}")
    print(f"价值权重: {result['value_weights']}")
    print(f"效用分: {result['utilities']}")
    print(f"偏差检测: {[b['name'] for b in result['biases']]}")
    print("=" * 60)
    for opt_id, narr in result["narratives"].items():
        print(f"\n【{narr['option_name']}】结局: {narr['outcome']}")
        for tl in narr["timeline"]:
            print(f"  {tl['emoji']} {tl['year_label']}: {tl['text'][:80]}...")
        print(f"  💬 {narr['punchline']}")
