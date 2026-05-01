# -*- coding: utf-8 -*-
"""
🎵 가사 기반 썸네일 & 유튜브 정보 생성기
Streamlit Secrets 기능으로 API 키를 안전하게 보관
"""

import sys
import io

# 한글/이모지 인코딩 오류 방지 - 반드시 필요!
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import streamlit as st
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(
    page_title="🎵 가사 썸네일 생성기",
    page_icon="🎵",
    layout="centered",
)

# 스마트폰 최적화 CSS
st.markdown("""
<style>
    .block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 720px; }
    .result-box {
        background: #1e1e2e; color: #cdd6f4;
        border: 1px solid #45475a; border-radius: 12px;
        padding: 16px; font-size: 14px; line-height: 1.7;
        white-space: pre-wrap; word-break: break-word; margin-bottom: 8px;
    }
    .section-header {
        font-size: 16px; font-weight: 700; color: #cba6f7;
        margin: 20px 0 8px 0; border-left: 4px solid #cba6f7; padding-left: 10px;
    }
    .stButton > button {
        width: 100%; background: linear-gradient(135deg, #cba6f7, #89b4fa);
        color: #1e1e2e; font-weight: 700; font-size: 16px;
        border: none; border-radius: 10px; padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("# 🎵 가사 썸네일 & 유튜브 생성기")
st.markdown("가사를 입력하면 AI가 썸네일 프롬프트와 유튜브 정보를 만들어 드려요.")
st.divider()

# ─────────────────────────────────────────
# API 키: Secrets에서 먼저 불러오고,
# 없으면 입력창 표시
# ─────────────────────────────────────────
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    with st.expander("🔑 OpenAI API 키 설정 (처음 한 번만)", expanded=True):
        api_key = st.text_input(
            "OpenAI API 키를 입력하세요",
            type="password",
            placeholder="sk-...",
            help="https://platform.openai.com 에서 발급받을 수 있어요."
        )
        st.caption("🔒 API 키는 이 세션에서만 사용되며 저장되지 않습니다.")
else:
    st.success("🔐 API 키가 안전하게 설정되어 있어요!", icon="✅")

# 가사 입력
st.markdown("### ✍️ 가사 입력")
lyrics = st.text_area(
    label="가사",
    placeholder="가사를 여기에 붙여넣기 하세요...\n\n예시:\n그대의 미소가 나를 부르는 밤\n별빛 아래 우리 둘이 걷던 그 길",
    height=220,
    label_visibility="collapsed"
)

with st.expander("⚙️ 추가 옵션"):
    genre = st.selectbox(
        "음악 장르",
        ["자동 감지", "발라드", "K-POP", "힙합", "R&B", "록", "재즈", "포크", "OST"]
    )
    channel_concept = st.text_input(
        "채널 콘셉트 (선택사항)",
        placeholder="예: 감성 피아노, 힐링 음악 채널..."
    )


def analyze_lyrics(api_key, lyrics, genre, channel_concept):
    """가사를 분석하여 썸네일 프롬프트와 유튜브 정보를 생성"""
    client = OpenAI(api_key=api_key)
    genre_text = f"장르: {genre}" if genre != "자동 감지" else "장르는 가사에서 자동 판단해주세요."
    concept_text = f"채널 콘셉트: {channel_concept}" if channel_concept.strip() else ""

    prompt = f"""
당신은 음악 콘텐츠 전문 AI 크리에이터입니다.
아래 가사를 분석하고 요청된 형식으로 작성해주세요.

[가사]
{lyrics}

[추가 정보]
{genre_text}
{concept_text}

다음 4가지를 순서대로 작성해주세요:

【1. 감성 분석】
- 가사의 핵심 감정과 분위기를 3~5줄로 설명하세요.
- 색깔, 시간대, 계절, 날씨 등 시각적 이미지로 표현하세요.

【2. 이미지 생성 AI 프롬프트 (영문)】
- Midjourney/DALL-E 3용 영문 프롬프트. 반드시 영어로만, 100~150단어.
- 형식: [장면 묘사], [분위기], [색감], [화풍], [카메라/조명], [해상도]

【3. 유튜브 제목 3가지】
- 감성형 / 정보형 / 궁금증 유발형으로 각각 다르게
- 이모지 포함, 40자 이내

【4. 유튜브 영상 설명글】
- 지혜롭고 깊이 있는 문체로. 철학적이고 성찰적인 느낌.
- 가사의 의미와 삶의 통찰을 연결하는 2~3문단
- 해시태그 15개 (한국어+영어 혼합)
- 구독/좋아요 유도 문구 1줄
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # 저렴하고 빠른 모델
        messages=[
            {"role": "system", "content": "음악 감성 분석과 유튜브 콘텐츠 제작 전문 AI입니다. 한국어로 답변합니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=2000,
    )

    full_text = response.choices[0].message.content
    sections = {"emotion": "", "prompt": "", "titles": "", "description": ""}
    markers = {
        "emotion": "【1. 감성 분석】",
        "prompt": "【2. 이미지 생성",
        "titles": "【3. 유튜브 제목",
        "description": "【4. 유튜브 영상"
    }
    current_key = None
    for line in full_text.split("\n"):
        matched = False
        for key, marker in markers.items():
            if marker in line:
                current_key = key
                matched = True
                break
        if not matched and current_key:
            sections[current_key] += line + "\n"
    return sections


def copy_button(text, button_id, label="📋 복사하기"):
    """클립보드 복사 버튼"""
    escaped = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$").replace("\n", "\\n")
    st.markdown(f"""
    <button onclick="navigator.clipboard.writeText(`{escaped}`).then(()=>{{
        this.textContent='✅ 복사됨!';
        setTimeout(()=>this.textContent='{label}',2000);
    }})"
    style="background:#313244;color:#cdd6f4;border:1px solid #45475a;
           border-radius:8px;padding:8px 16px;font-size:13px;
           cursor:pointer;width:100%;margin-bottom:20px;">
    {label}</button>
    """, unsafe_allow_html=True)


# 실행 버튼
generate_btn = st.button("🚀 AI 분석 시작!", use_container_width=True)

if generate_btn:
    if not api_key.strip():
        st.error("⚠️ OpenAI API 키를 먼저 입력해주세요!")
        st.stop()
    if not lyrics.strip():
        st.error("⚠️ 가사를 입력해주세요!")
        st.stop()

    with st.spinner("🎵 AI가 분석 중이에요... (10~20초 소요)"):
        try:
            results = analyze_lyrics(api_key, lyrics, genre, channel_concept)
            st.success("✨ 분석 완료!")
            st.divider()

            items = [
                ("emotion",     "🎭 감성 분석",              "가사의 감성과 분위기"),
                ("prompt",      "🎨 이미지 생성 AI 프롬프트", "Midjourney, DALL-E 3에 바로 사용 가능"),
                ("titles",      "📺 유튜브 제목 3가지",       "마음에 드는 제목을 선택하세요"),
                ("description", "📝 유튜브 설명글 & 해시태그", "유튜브 설명란에 그대로 붙여넣기"),
            ]
            for key, title, tip in items:
                st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
                st.caption(tip)
                content = results[key].strip()
                st.markdown(f'<div class="result-box">{content}</div>', unsafe_allow_html=True)
                copy_button(content, f"btn_{key}", f"📋 {title} 복사")

        except Exception as e:
            err = str(e)
            if "api_key" in err.lower() or "authentication" in err.lower():
                st.error("❌ API 키가 올바르지 않아요.")
            elif "quota" in err.lower():
                st.error("❌ API 사용 한도를 초과했어요. 크레딧을 충전해주세요.")
            else:
                st.error(f"❌ 오류: {err}")

st.divider()
st.caption("🎵 가사 썸네일 & 유튜브 정보 생성기 | Powered by OpenAI")
