"""
平行人生 · LLM 客户端
接入 DeepSeek（OpenAI 兼容协议），支持：
- Streamlit Secrets / 环境变量 / UI 输入三级 API Key 读取
- 流式输出（逐字打字机效果）
- 失败自动回退到模板 fallback
- 零依赖 OpenAI SDK（纯 requests，降低部署成本）
"""
from __future__ import annotations
import os
import json
import time
from typing import Optional, Iterator, Dict, Any, List

import requests

# ------------------------------------------------------------
# 全局配置
# ------------------------------------------------------------
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"   # V3.2，通用对话 + 代码兼顾
REASONER_MODEL = "deepseek-reasoner"  # 深度推理（用于偏差反思）
REQUEST_TIMEOUT = 30
MAX_RETRY = 2


def get_api_key() -> Optional[str]:
    """
    三级查找 API Key：
    1. Streamlit session_state（UI 手动输入）
    2. Streamlit Secrets（部署环境配置）
    3. 环境变量 DEEPSEEK_API_KEY
    """
    try:
        import streamlit as st
        # 1. UI 输入优先
        key = st.session_state.get("deepseek_api_key")
        if key and key.strip():
            return key.strip()
        # 2. Streamlit Secrets
        try:
            if "DEEPSEEK_API_KEY" in st.secrets:
                return st.secrets["DEEPSEEK_API_KEY"]
        except Exception:
            pass
    except ImportError:
        pass
    # 3. 环境变量
    return os.environ.get("DEEPSEEK_API_KEY")


def is_available() -> bool:
    """是否已配置 Key（UI 里用来判断开关可用性）"""
    return bool(get_api_key())


class LLMError(Exception):
    pass


def chat_completion(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.85,
    max_tokens: int = 800,
    stream: bool = False,
) -> str:
    """
    同步调用 DeepSeek Chat Completion（OpenAI 兼容）。
    stream=True 时返回完整拼接的字符串（内部仍走流式节流）。
    """
    key = get_api_key()
    if not key:
        raise LLMError("未配置 DEEPSEEK_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
    }

    last_err = None
    for attempt in range(MAX_RETRY + 1):
        try:
            if stream:
                return _stream_chat(headers, payload)
            resp = requests.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code == 401:
                raise LLMError("API Key 无效或余额不足")
            if resp.status_code == 429:
                time.sleep(1.5 * (attempt + 1))
                last_err = LLMError("请求过于频繁")
                continue
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except LLMError:
            raise
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRY:
                time.sleep(1.2 * (attempt + 1))
    raise LLMError(f"DeepSeek 调用失败: {last_err}")


def _stream_chat(headers: Dict[str, str], payload: Dict[str, Any]) -> str:
    """流式读取并拼接为完整字符串（保留给非 UI 场景）"""
    payload = {**payload, "stream": True}
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT,
        stream=True,
    )
    resp.raise_for_status()
    full = []
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue
        chunk = line[5:].strip()
        if chunk == "[DONE]":
            break
        try:
            obj = json.loads(chunk)
            delta = obj["choices"][0]["delta"].get("content", "")
            if delta:
                full.append(delta)
        except Exception:
            continue
    return "".join(full).strip()


def stream_chat_completion(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.85,
    max_tokens: int = 800,
) -> Iterator[str]:
    """
    真正的流式生成器，供 Streamlit `st.write_stream` 直接消费。
    逐片 yield 增量文本（不是累积文本）。
    """
    key = get_api_key()
    if not key:
        raise LLMError("未配置 DEEPSEEK_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    try:
        resp = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
            stream=True,
        )
        if resp.status_code == 401:
            raise LLMError("API Key 无效或余额不足，请检查")
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            chunk = line[5:].strip()
            if chunk == "[DONE]":
                break
            try:
                obj = json.loads(chunk)
                delta = obj["choices"][0]["delta"].get("content", "")
                if delta:
                    yield delta
            except Exception:
                continue
    except LLMError:
        raise
    except Exception as e:
        raise LLMError(f"流式连接失败: {e}")


# ------------------------------------------------------------
# 业务层：平行人生叙事生成（专用 prompt）
# ------------------------------------------------------------
NARRATIVE_SYSTEM_PROMPT = """你是一个深谙行为经济学与人文叙事的"平行时空写手"。

# 任务
给定用户信息、选项参数、蒙特卡洛模拟结果，写一段**第二人称**的未来场景。

# 风格铁律
1. **具象，拒绝抽象**：不要写"你很幸福"，要写"周日傍晚你在阳台煮咖啡，女儿在客厅背单词"
2. **一个画面感场景 + 一个情绪细节**：开头永远是时间+地点+动作，结尾永远是一个扎心或余韵的细节
3. **长度**：每段 80-130 字，3-4 句话，不要凑字
4. **引用用户原词**：如果用户提到了"女儿/父母/自由/稳定"等关键词，必须在文本中自然回指
5. **绝不鸡汤**：不写"只要努力就会成功"；允许失败、允许遗憾、允许代价
6. **数字要匹配**：收入、年龄必须与输入参数一致，不要瞎编
7. **输出纯文本**：不加任何前缀如"第 N 年："，不加 emoji，不加引号

# 绝对禁忌
- 不要说"这只是模拟"之类的元对话
- 不要给建议、不要劝说、不要站队
- 不要用"亲爱的/朋友"等虚假亲密称呼
"""


def generate_timeline_narrative(
    option_name: str,
    option_emoji: str,
    year: int,
    age: int,
    income: float,
    happiness: float,
    outcome: str,
    dominant_value: str,
    user_raw_text: str,
    user_value_keyword: str,
    user_concern_keyword: str,
    fallback_text: str,
) -> str:
    """
    为单个时间节点生成叙事文本。
    - 失败时返回 fallback_text（模板叙事）
    """
    if not is_available():
        return fallback_text

    outcome_zh = {"optimistic": "顺境", "baseline": "常态", "pessimistic": "逆境"}[outcome]

    user_msg = f"""# 场景参数
- 用户年龄：{age + year} 岁（当前 {age} 岁，快进 {year} 年后）
- 选择的路径：{option_emoji} {option_name}
- 结局判定：{outcome_zh}（蒙特卡洛 1000 次模拟得出）
- 预期年收入（P50 中位数）：{income:.1f} 万元
- 幸福指数：{happiness:.2f}（0-1 区间）
- 用户主导价值观：{dominant_value}
- 用户原话片段：「{user_raw_text[:100]}」
- 用户最在乎的关键词：{user_value_keyword}
- 用户提到的关心对象：{user_concern_keyword}

# 要求
写第 {year} 年后的一个具体生活场景。严格 80-130 字，3-4 句话。
不要写"第 {year} 年"这样的时间前缀。直接从画面开始。
"""
    try:
        text = chat_completion(
            messages=[
                {"role": "system", "content": NARRATIVE_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.88,
            max_tokens=300,
        )
        # 清洗：去除可能的引号、前缀
        text = text.strip().strip('"').strip("'").strip("「").strip("」")
        if len(text) < 20:
            return fallback_text
        return text
    except Exception:
        return fallback_text


PUNCHLINE_SYSTEM_PROMPT = """你是一个锋利而温柔的"命运观察者"。
用户刚刚看完一条平行时空的人生。请你写一句/一段扎心但不刻薄的总结。

# 要求
- 长度：40-80 字，1-2 句
- 语气：冷静、克制、像老朋友深夜的一句话
- 不给建议、不鸡汤、不劝说
- 可以引用用户原词，形成"你说过..."的回指
- 输出纯文本，不加引号
"""


def generate_punchline(
    option_name: str,
    outcome: str,
    user_raw_text: str,
    user_value_keyword: str,
    fallback_text: str,
) -> str:
    """生成扎心总结"""
    if not is_available():
        return fallback_text

    outcome_zh = {"optimistic": "顺境结局", "baseline": "常态结局", "pessimistic": "逆境结局"}[outcome]
    user_msg = f"""用户选择：{option_name}
结局：{outcome_zh}
用户原话：{user_raw_text[:120]}
用户最在乎的词：{user_value_keyword}

请写一句扎心总结。"""
    try:
        text = chat_completion(
            messages=[
                {"role": "system", "content": PUNCHLINE_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.9,
            max_tokens=180,
        )
        text = text.strip().strip('"').strip("'").strip("「").strip("」")
        if len(text) < 15:
            return fallback_text
        return text
    except Exception:
        return fallback_text


# ------------------------------------------------------------
# 诊断接口：UI 里"测试连接"按钮使用
# ------------------------------------------------------------
def ping(api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    快速连通性测试。
    返回 {"ok": bool, "model": str, "latency_ms": int, "error": str}
    """
    if api_key:
        os.environ["DEEPSEEK_API_KEY"] = api_key  # 临时写入
    if not get_api_key():
        return {"ok": False, "error": "未提供 API Key"}

    t0 = time.time()
    try:
        text = chat_completion(
            messages=[{"role": "user", "content": "回答'pong'两个字，不要任何标点。"}],
            max_tokens=10,
            temperature=0.0,
        )
        return {
            "ok": True,
            "model": DEFAULT_MODEL,
            "latency_ms": int((time.time() - t0) * 1000),
            "echo": text,
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "latency_ms": int((time.time() - t0) * 1000)}
