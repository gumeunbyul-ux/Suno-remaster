import streamlit as st
import requests

st.set_page_config(page_title="Lyrics AI", page_icon="🎵", layout="centered")

st.markdown("""
<style>
.block-container{padding:1rem !important;max-width:720px}
.box{background:#1e1e2e;color:#cdd6f4;border:1px solid #45475a;
border-radius:12px;padding:16px;font-size:14px;line-height:1.8;
white-space:pre-wrap;word-break:break-word;margin-bottom:12px}
.hd{font-size:15px;font-weight:700;color:#cba6f7;margin:16px 0 6px 0;
border-left:4px solid #cba6f7;padding-left:8px}
div.stButton>button{width:100%;background:linear-gradient(135deg,#cba6f7,#89b4fa);
color:#1e1e2e;font-weight:700;font-size:16px;border:none;border-radius:10px;padding:12px}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🎵 가사 썸네일 & 유튜브 생성기")
st.markdown("가사를 입력하면 AI가 분석해 드려요.")
st.divider()

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Streamlit Secrets에 OPENAI_API_KEY를 등록해주세요.")
    st.stop()

lyrics = st.text_area(
    "가사",
    placeholder="가사를 여기에 붙여넣기 하세요...",
    height=220,
    label_visibility="collapsed"
)

col1, col2 = st.columns(2)
with col1:
    genre_list = ["자동감지", "발라드", "KPOP", "힙합", "RnB", "록", "재즈", "포크", "OST"]
    genre = st.selectbox("장르", genre_list, label_visibility="collapsed")
with col2:
    concept = st.text_input("채널콘셉트", placeholder="예: 감성 힐링 채널", label_visibility="collapsed")

if st.button("🚀 AI 분석 시작!", use_container_width=True):
    if not lyrics.strip():
        st.error("가사를 입력해주세요!")
        st.stop()

    with st.spinner("AI가 분석 중이에요... 잠시만요"):
        try:
            # 모든 텍스트를 영어 기반 프롬프트로 감싸서 인코딩 문제 방지
            safe_lyrics = lyrics.encode("utf-8").decode("utf-8")
            safe_genre = genre.encode("utf-8").decode("utf-8")
            safe_concept = concept.encode("utf-8").decode("utf-8") if concept else "general"

            prompt = f"""Analyze these song lyrics and respond ONLY in Korean language.

LYRICS:
{safe_lyrics}

GENRE: {safe_genre}
CHANNEL: {safe_concept}

Write these 4 sections in Korean:

[SECTION1-감성분석]
Describe emotions and mood using visual imagery (colors, seasons, weather, time). 3-5 lines.

[SECTION2-이미지프롬프트]
English prompt for Midjourney/DALL-E3. 100-150 words. Include: scene, mood, colors, art style, lighting, resolution.

[SECTION3-유튜브제목]
3 YouTube titles in Korean with emojis. Under 40 chars each.
Title 1 (emotional):
Title 2 (informational):
Title 3 (curiosity):

[SECTION4-유튜브설명]
2-3 philosophical paragraphs in Korean connecting lyrics to life wisdom.
Then 15 hashtags (Korean + English mix).
Then 1 line encouraging subscribe and like."""

            # requests 라이브러리로 직접 호출 (인코딩 자동 처리)
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a professional Korean music content creator. Always respond in Korean."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 2000
                },
                timeout=60
            )

            if response.status_code != 200:
                err = response.json().get("error", {}).get("message", "알 수 없는 오류")
                st.error(f"API 오류: {err}")
                st.stop()

            result = response.json()["choices"][0]["message"]["content"]

            st.success("✨ 분석 완료!")
            st.divider()

            # 섹션 파싱
            sections = {
                "감성분석": "",
                "이미지프롬프트": "",
                "유튜브제목": "",
                "유튜브설명": ""
            }
            current = None
            for line in result.split("\n"):
                low = line.lower()
                if "section1" in low or "감성분석" in low:
                    current = "감성분석"
                elif "section2" in low or "이미지프롬프트" in low:
                    current = "이미지프롬프트"
                elif "section3" in low or "유튜브제목" in low:
                    current = "유튜브제목"
                elif "section4" in low or "유튜브설명" in low:
                    current = "유튜브설명"
                elif current:
                    sections[current] += line + "\n"

            # 섹션 파싱 실패하면 전체 출력
            if all(v.strip() == "" for v in sections.values()):
                st.markdown('<div class="hd">📋 분석 결과 전체</div>', unsafe_allow_html=True)
                st.text_area("전체결과", value=result, height=600, label_visibility="collapsed")
            else:
                items = [
                    ("감성분석",    "🎭 감성 분석",              "가사의 감성과 분위기"),
                    ("이미지프롬프트","🎨 이미지 생성 프롬프트", "Midjourney / DALL-E 3 용"),
                    ("유튜브제목",  "📺 유튜브 제목 3가지",      "마음에 드는 것 선택"),
                    ("유튜브설명",  "📝 유튜브 설명글 & 해시태그","설명란에 붙여넣기"),
                ]
                for key, title, tip in items:
                    content = sections[key].strip()
                    if content:
                        st.markdown(f'<div class="hd">{title}</div>', unsafe_allow_html=True)
                        st.caption(tip)
                        st.markdown(f'<div class="box">{content}</div>', unsafe_allow_html=True)
                        st.text_area(
                            "복사",
                            value=content,
                            height=100,
                            label_visibility="collapsed",
                            key=f"copy_{key}"
                        )

            st.info("💡 텍스트 박스를 길게 눌러 전체선택 후 복사하세요!")

        except requests.exceptions.Timeout:
            st.error("시간이 너무 오래 걸려요. 다시 시도해주세요.")
        except requests.exceptions.ConnectionError:
            st.error("인터넷 연결을 확인해주세요.")
        except Exception as e:
            st.error(f"오류: {str(e)}")

st.divider()
st.caption("🎵 가사 썸네일 & 유튜브 정보 생성기 | Powered by OpenAI GPT-4o mini")
