"""
🎵 가사 기반 썸네일 & 유튜브 정보 생성기
Streamlit 앱 - 스마트폰 브라우저에서 실행 가능
"""

import streamlit as st
from openai import OpenAI

# ─────────────────────────────────────────
# 페이지 기본 설정 (반드시 첫 번째 Streamlit 명령)
# ─────────────────────────────────────────
st.set_page_config(
    page_title="🎵 가사 썸네일 생성기",
    page_icon="🎵",
    layout="centered",  # 스마트폰 화면에 맞게 중앙 정렬
)

# ─────────────────────────────────────────
# 커스텀 CSS - 스마트폰 최적화 디자인
# ─────────────────────────────────────────
st.markdown("""
<style>
    /* 전체 폰트 및 배경 */
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
    }

    /* 메인 컨테이너 여백 조정 (모바일 최적화) */
    .block-container {
        padding: 1rem 1rem 2rem 1rem !important;
        max-width: 720px;
    }

    /* 결과 텍스트 박스 스타일 */
    .result-box {
        background: #1e1e2e;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 12px;
        padding: 16px;
        font-size: 14px;
        line-height: 1.7;
        white-space: pre-wrap;
        word-break: break-word;
        margin-bottom: 8px;
        font-family: monospace;
    }

    /* 섹션 헤더 */
    .section-header {
        font-size: 16px;
        font-weight: 700;
        color: #cba6f7;
        margin: 20px 0 8px 0;
        border-left: 4px solid #cba6f7;
        padding-left: 10px;
    }

    /* 복사 안내 텍스트 */
    .copy-tip {
        font-size: 12px;
        color: #6c7086;
        margin-bottom: 16px;
    }

    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #cba6f7, #89b4fa);
        color: #1e1e2e;
        font-weight: 700;
        font-size: 16px;
        border: none;
        border-radius: 10px;
        padding: 12px;
        cursor: pointer;
    }

    /* 텍스트 입력창 */
    .stTextArea textarea {
        font-size: 15px;
        border-radius: 10px;
    }
    .stTextInput input {
        font-size: 14px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────
st.markdown("# 🎵 가사 썸네일 & 유튜브 생성기")
st.markdown("가사를 입력하면 AI가 썸네일 프롬프트와 유튜브 정보를 자동으로 만들어 드려요.")
st.divider()


# ─────────────────────────────────────────
# API 키 입력 (보안: password 타입으로 숨김)
# ─────────────────────────────────────────
with st.expander("🔑 OpenAI API 키 설정 (처음 한 번만)", expanded=True):
    api_key = st.text_input(
        "OpenAI API 키를 입력하세요",
        type="password",  # 입력 내용이 보이지 않도록 설정
        placeholder="sk-...",
        help="https://platform.openai.com 에서 발급받을 수 있어요."
    )
    st.caption("🔒 API 키는 이 세션에서만 사용되며 저장되지 않습니다.")


# ─────────────────────────────────────────
# 가사 입력
# ─────────────────────────────────────────
st.markdown("### ✍️ 가사 입력")
lyrics = st.text_area(
    label="가사를 여기에 붙여넣기 하세요",
    placeholder="예시:\n그대의 미소가 나를 부르는 밤\n별빛 아래 우리 둘이 걷던 그 길\n이제 모든 것이 달라져도\n기억 속에 넌 언제나 빛나고 있어...",
    height=220,  # 스마트폰에서 입력하기 적당한 높이
    label_visibility="collapsed"
)

# 추가 옵션 (접이식)
with st.expander("⚙️ 추가 옵션"):
    genre = st.selectbox(
        "음악 장르",
        ["자동 감지", "발라드", "K-POP", "힙합", "R&B", "록", "재즈", "포크", "OST"],
    )
    channel_concept = st.text_input(
        "채널 콘셉트 (선택사항)",
        placeholder="예: 감성 피아노, 힐링 음악 채널, 커버곡 채널..."
    )


# ─────────────────────────────────────────
# AI 분석 함수
# ─────────────────────────────────────────
def analyze_lyrics(api_key: str, lyrics: str, genre: str, channel_concept: str) -> dict:
    """
    가사를 분석하여 썸네일 프롬프트, 유튜브 제목/설명을 생성하는 함수.
    반환값: 딕셔너리 형태의 결과물
    """

    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=api_key)

    # 장르 정보 처리
    genre_text = f"장르: {genre}" if genre != "자동 감지" else "장르는 가사에서 자동 판단해주세요."
    concept_text = f"채널 콘셉트: {channel_concept}" if channel_concept.strip() else ""

    # ── AI에게 보내는 지시문 (프롬프트) ──
    prompt = f"""
당신은 음악 콘텐츠 전문 AI 크리에이터입니다.
아래 가사를 분석하고, 요청된 형식으로 정확하게 결과를 작성해주세요.

[가사]
{lyrics}

[추가 정보]
{genre_text}
{concept_text}

━━━━━━━━━━━━━━━━━━━━━
다음 4가지를 순서대로 작성해주세요:

【1. 감성 분석】
- 가사의 핵심 감정과 분위기를 3~5줄로 설명하세요.
- 색깔, 시간대, 계절, 날씨 등 시각적 이미지로 표현하세요.

【2. 이미지 생성 AI 프롬프트 (영문)】
- Midjourney / DALL-E 3에 바로 사용할 수 있는 영문 프롬프트를 작성하세요.
- 형식: [장면 묘사], [분위기], [색감], [화풍], [카메라/조명], [해상도]
- 반드시 영어로만 작성하세요. 길이: 100~150 단어.

【3. 유튜브 제목 3가지】
- 각각 다른 스타일로 (감성형 / 정보형 / 궁금증 유발형)
- 이모지 포함, 40자 이내, 검색이 잘 되도록 작성하세요.
- 번호를 붙여 한 줄씩 작성하세요.

【4. 유튜브 영상 설명글】
- 지혜롭고 깊이 있는 문체로 작성하세요. (철학적이고 성찰적인 느낌)
- 가사의 의미와 삶의 통찰을 연결하는 2~3문단의 소개글
- 그 다음에 이어서: 해시태그 15개 (관련성 높은 한국어+영어 혼합)
- 마지막에: 구독/좋아요 유도 문구 1줄

모든 답변은 위의 【】 헤더를 그대로 사용하여 구분해주세요.
"""

    # GPT-4o에게 요청 전송
    response = client.chat.completions.create(
        model="gpt-4o",          # 가장 뛰어난 분석 능력
        messages=[
            {
                "role": "system",
                "content": "당신은 음악 감성 분석과 유튜브 콘텐츠 제작에 전문화된 AI 크리에이터입니다. 한국어로 정확하고 창의적으로 답변합니다."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.8,        # 창의성 수준 (0~1, 높을수록 다양한 표현)
        max_tokens=2000,        # 최대 출력 길이
    )

    # 응답 텍스트 추출
    full_text = response.choices[0].message.content

    # ── 결과를 섹션별로 분리 ──
    sections = {
        "emotion": "",
        "prompt": "",
        "titles": "",
        "description": ""
    }

    # 각 섹션 키워드로 텍스트 분리
    markers = {
        "emotion":      "【1. 감성 분석】",
        "prompt":       "【2. 이미지 생성 AI 프롬프트",
        "titles":       "【3. 유튜브 제목",
        "description":  "【4. 유튜브 영상 설명글】"
    }

    lines = full_text.split("\n")
    current_key = None

    for line in lines:
        # 어느 섹션에 해당하는지 판별
        for key, marker in markers.items():
            if marker in line:
                current_key = key
                break
        else:
            # 섹션 내용 추가
            if current_key:
                sections[current_key] += line + "\n"

    return sections


# ─────────────────────────────────────────
# 복사 버튼 헬퍼 함수 (JavaScript 클립보드 복사)
# ─────────────────────────────────────────
def copy_button(text: str, button_id: str, label: str = "📋 복사하기"):
    """
    텍스트를 클립보드에 복사하는 버튼 생성.
    JavaScript를 사용하여 모바일 브라우저에서도 동작함.
    """
    # 텍스트 내 특수문자 이스케이프 처리
    escaped = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

    st.markdown(f"""
    <button
        onclick="navigator.clipboard.writeText(`{escaped}`).then(() => {{
            this.textContent = '✅ 복사됨!';
            setTimeout(() => this.textContent = '{label}', 2000);
        }})"
        style="
            background: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 13px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 20px;
        "
        id="{button_id}"
    >{label}</button>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 메인 실행 버튼
# ─────────────────────────────────────────
st.markdown("")  # 여백
generate_btn = st.button("🚀 AI 분석 시작!", use_container_width=True)


# ─────────────────────────────────────────
# 결과 출력
# ─────────────────────────────────────────
if generate_btn:

    # 입력값 검증
    if not api_key.strip():
        st.error("⚠️ OpenAI API 키를 먼저 입력해주세요!")
        st.stop()

    if not lyrics.strip():
        st.error("⚠️ 가사를 입력해주세요!")
        st.stop()

    if len(lyrics.strip()) < 20:
        st.warning("💡 가사가 너무 짧아요. 더 입력하면 결과가 좋아져요.")

    # 로딩 스피너 표시
    with st.spinner("🎵 AI가 가사를 분석하고 있어요... (10~20초 소요)"):
        try:
            # AI 분석 실행
            results = analyze_lyrics(api_key, lyrics, genre, channel_concept)

            st.success("✨ 분석 완료! 결과를 확인하세요.")
            st.divider()

            # ── 1. 감성 분석 ──
            st.markdown('<div class="section-header">🎭 감성 분석</div>', unsafe_allow_html=True)
            st.markdown('<p class="copy-tip">길게 눌러서 텍스트를 선택하거나 아래 버튼으로 복사하세요</p>', unsafe_allow_html=True)
            emotion_text = results["emotion"].strip()
            st.markdown(f'<div class="result-box">{emotion_text}</div>', unsafe_allow_html=True)
            copy_button(emotion_text, "btn_emotion", "📋 감성 분석 복사")

            # ── 2. 이미지 프롬프트 ──
            st.markdown('<div class="section-header">🎨 이미지 생성 AI 프롬프트</div>', unsafe_allow_html=True)
            st.markdown('<p class="copy-tip">Midjourney, DALL-E 3, Stable Diffusion에 바로 사용 가능</p>', unsafe_allow_html=True)
            prompt_text = results["prompt"].strip()
            st.markdown(f'<div class="result-box">{prompt_text}</div>', unsafe_allow_html=True)
            copy_button(prompt_text, "btn_prompt", "📋 이미지 프롬프트 복사")

            # ── 3. 유튜브 제목 ──
            st.markdown('<div class="section-header">📺 유튜브 제목 3가지</div>', unsafe_allow_html=True)
            st.markdown('<p class="copy-tip">마음에 드는 제목을 선택해서 사용하세요</p>', unsafe_allow_html=True)
            titles_text = results["titles"].strip()
            st.markdown(f'<div class="result-box">{titles_text}</div>', unsafe_allow_html=True)
            copy_button(titles_text, "btn_titles", "📋 유튜브 제목 복사")

            # ── 4. 유튜브 설명글 ──
            st.markdown('<div class="section-header">📝 유튜브 영상 설명글 & 해시태그</div>', unsafe_allow_html=True)
            st.markdown('<p class="copy-tip">유튜브 영상 설명란에 그대로 붙여넣기 하세요</p>', unsafe_allow_html=True)
            desc_text = results["description"].strip()
            st.markdown(f'<div class="result-box">{desc_text}</div>', unsafe_allow_html=True)
            copy_button(desc_text, "btn_desc", "📋 설명글 전체 복사")

            st.divider()
            st.caption("💡 결과가 마음에 들지 않으면 버튼을 다시 눌러 새로운 버전을 생성하세요!")

        except Exception as e:
            # 에러 처리 - 초보자가 이해할 수 있는 메시지로 표시
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "incorrect api key" in error_msg.lower():
                st.error("❌ API 키가 올바르지 않아요. 다시 확인해주세요.\n\nhttps://platform.openai.com/api-keys 에서 확인하세요.")
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                st.error("❌ API 사용 한도를 초과했어요. OpenAI 계정의 크레딧을 충전해주세요.")
            elif "rate_limit" in error_msg.lower():
                st.error("❌ 요청이 너무 많아요. 잠시 후 다시 시도해주세요.")
            else:
                st.error(f"❌ 오류가 발생했어요:\n{error_msg}")


# ─────────────────────────────────────────
# 하단 안내
# ─────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; color:#6c7086; font-size:13px; line-height:1.8;">
🎵 가사 썸네일 & 유튜브 정보 생성기<br>
Powered by OpenAI GPT-4o<br>
스마트폰에서도 편하게 사용하세요 📱
</div>
""", unsafe_allow_html=True)
