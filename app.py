import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="가사 썸네일 생성기", page_icon="🎵", layout="centered")

st.markdown("""
<style>
.block-container{padding:1rem 1rem 2rem 1rem !important;max-width:720px}
.result-box{background:#1e1e2e;color:#cdd6f4;border:1px solid #45475a;border-radius:12px;
padding:16px;font-size:14px;line-height:1.7;white-space:pre-wrap;word-break:break-word;margin-bottom:8px}
.sec-hd{font-size:16px;font-weight:700;color:#cba6f7;margin:20px 0 8px 0;
border-left:4px solid #cba6f7;padding-left:10px}
.stButton>button{width:100%;background:linear-gradient(135deg,#cba6f7,#89b4fa);
color:#1e1e2e;font-weight:700;font-size:16px;border:none;border-radius:10px;padding:12px}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🎵 가사 썸네일 & 유튜브 생성기")
st.markdown("가사를 입력하면 AI가 썸네일 프롬프트와 유튜브 정보를 만들어 드려요.")
st.divider()

# Secrets에서 API 키 불러오기 (입력창 없음)
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("API 키가 설정되지 않았어요. Streamlit Cloud > Settings > Secrets 에서 OPENAI_API_KEY를 추가해주세요.")
    st.stop()

# 가사 입력
st.markdown("### ✍️ 가사 입력")
lyrics = st.text_area(
    "가사",
    placeholder="가사를 여기에 붙여넣기 하세요...",
    height=220,
    label_visibility="collapsed"
)

with st.expander("⚙️ 추가 옵션"):
    genre = st.selectbox("장르", ["자동 감지", "발라드", "K-POP", "힙합", "R&B", "록", "재즈", "포크", "OST"])
    concept = st.text_input("채널 콘셉트 (선택)", placeholder="예: 감성 피아노, 힐링 채널...")

def run_ai(key, lyr, gnr, con):
    client = OpenAI(api_key=key)
    g = ("장르: " + gnr) if gnr != "자동 감지" else "장르는 가사에서 판단"
    c = ("채널: " + con) if con.strip() else ""

    p = "아래 가사를 분석해서 4가지를 작성하세요.\n\n"
    p += "[가사]\n" + lyr + "\n\n"
    p += "[정보]\n" + g + "\n" + c + "\n\n"
    p += "1. [감성분석] 가사의 감정과 분위기를 시각적으로 3~5줄\n\n"
    p += "2. [이미지프롬프트] Midjourney용 영문 프롬프트 100~150단어\n\n"
    p += "3. [유튜브제목] 감성형/정보형/궁금증형 3가지, 이모지 포함\n\n"
    p += "4. [유튜브설명] 지혜롭고 철학적인 2~3문단 + 해시태그 15개 + 구독유도 1줄"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Korean music content creator. Respond in Korean."},
            {"role": "user", "content": p}
        ],
        temperature=0.8,
        max_tokens=2000,
    )
    return res.choices[0].message.content

def show_section(title, tip, content):
    st.markdown(f'<div class="sec-hd">{title}</div>', unsafe_allow_html=True)
    st.caption(tip)
    st.markdown(f'<div class="result-box">{content}</div>', unsafe_allow_html=True)
    st.text_area("복사용", value=content, height=120, label_visibility="collapsed", key=title)

if st.button("🚀 AI 분석 시작!", use_container_width=True):
    if not lyrics.strip():
        st.error("가사를 입력해주세요!")
        st.stop()

    with st.spinner("AI가 분석 중이에요... 10~20초 소요"):
        try:
            result = run_ai(api_key, lyrics, genre, concept)
            st.success("✨ 분석 완료!")
            st.divider()

            parts = {"감성분석": "", "이미지프롬프트": "", "유튜브제목": "", "유튜브설명": ""}
            cur = None
            for line in result.split("\n"):
                for k in parts:
                    if k in line and any(m in line for m in ["1.", "2.", "3.", "4.", "[", "【"]):
                        cur = k
                        break
                else:
                    if cur:
                        parts[cur] += line + "\n"

            if all(v.strip() == "" for v in parts.values()):
                st.markdown('<div class="sec-hd">📋 분석 결과</div>', unsafe_allow_html=True)
                st.text_area("결과 전체", value=result, height=500, label_visibility="collapsed")
            else:
                labels = [
                    ("감성분석",      "🎭 감성 분석",               "가사의 감성과 분위기"),
                    ("이미지프롬프트", "🎨 이미지 생성 프롬프트",    "Midjourney / DALL-E 3 용"),
                    ("유튜브제목",    "📺 유튜브 제목 3가지",        "마음에 드는 것 선택"),
                    ("유튜브설명",    "📝 유튜브 설명글 & 해시태그", "설명란에 붙여넣기"),
                ]
                for k, title, tip in labels:
                    if parts[k].strip():
                        show_section(title, tip, parts[k].strip())

            st.info("💡 텍스트 박스를 길게 눌러 전체 선택 후 복사하세요!")

        except Exception as e:
            err = str(e)
            if "auth" in err.lower() or "invalid" in err.lower():
                st.error("API 키가 올바르지 않아요.")
            elif "quota" in err.lower() or "billing" in err.lower():
                st.error("API 크레딧이 부족해요. OpenAI에서 충전해주세요.")
            else:
                st.error("오류: " + err)

st.divider()
st.caption("🎵 가사 썸네일 & 유튜브 정보 생성기 | Powered by OpenAI GPT-4o mini")
