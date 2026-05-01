import streamlit as st
import json
import urllib.request
import urllib.parse

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

st.markdown("# \U0001f3b5 \uac00\uc0ac \uc378\ub124\uc77c & \uc720\ud29c\ube0c \uc0dd\uc131\uae30")
st.markdown("\uac00\uc0ac\ub97c \uc785\ub825\ud558\uba74 AI\uac00 \uc378\ub124\uc77c \ud504\ub86c\ud504\ud2b8\uc640 \uc720\ud29c\ube0c \uc815\ubcf4\ub97c \ub9cc\ub4e4\uc5b4 \ub4dc\ub824\uc694.")
st.divider()

# Secrets에서 API 키 로드
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Streamlit Secrets에 OPENAI_API_KEY를 등록해주세요.")
    st.stop()

lyrics = st.text_area(
    label="lyrics",
    placeholder="\uac00\uc0ac\ub97c \uc5ec\uae30\uc5d0 \ubd99\uc5ec\ub123\uae30 \ud558\uc138\uc694...",
    height=220,
    label_visibility="collapsed"
)

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox(
        "genre",
        ["\uc790\ub3d9 \uac10\uc9c0", "\ubc1c\ub77c\ub4dc", "K-POP", "\ud78d\ud569", "R&B", "\ub85d", "\uc7ac\uc988", "\ud3ec\ud06c", "OST"],
        label_visibility="collapsed"
    )
with col2:
    concept = st.text_input(
        "concept",
        placeholder="\ucc44\ub110 \ucf58\uc14b\ud2b8 (\uc120\ud0dd)",
        label_visibility="collapsed"
    )

def call_openai(api_key, lyrics, genre, concept):
    url = "https://api.openai.com/v1/chat/completions"
    
    system_msg = "You are a Korean music content creator. Always respond in Korean language."
    
    user_msg = (
        "Please analyze the following song lyrics and provide 4 sections.\n\n"
        "LYRICS:\n" + lyrics + "\n\n"
        "GENRE: " + genre + "\n"
        "CHANNEL CONCEPT: " + concept + "\n\n"
        "Please write in Korean:\n\n"
        "[SECTION1: emotional-analysis]\n"
        "Describe the emotion and mood in 3-5 lines using visual imagery like colors, seasons, time of day.\n\n"
        "[SECTION2: image-prompt]\n"
        "Write an English image generation prompt for Midjourney/DALL-E3. 100-150 words. Include scene, mood, color palette, art style, camera angle, resolution.\n\n"
        "[SECTION3: youtube-titles]\n"
        "Write 3 YouTube titles in Korean: emotional style / informational style / curiosity style. Include emojis. Under 40 characters each.\n\n"
        "[SECTION4: youtube-description]\n"
        "Write in Korean: 2-3 philosophical paragraphs connecting lyrics to life wisdom, then 15 hashtags (Korean+English mix), then 1 line encouraging subscribe/like."
    )

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.8,
        "max_tokens": 2000
    }, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer " + api_key
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
    
    return result["choices"][0]["message"]["content"]

def parse_sections(text):
    sections = {
        "emotional-analysis": "",
        "image-prompt": "",
        "youtube-titles": "",
        "youtube-description": ""
    }
    current = None
    for line in text.split("\n"):
        for key in sections:
            if key in line.lower() or key.replace("-", "") in line.lower():
                current = key
                break
        else:
            if current is not None:
                sections[current] += line + "\n"
    return sections

if st.button("\U0001f680 AI \ubd84\uc11d \uc2dc\uc791!", use_container_width=True):
    if not lyrics.strip():
        st.error("\uac00\uc0ac\ub97c \uc785\ub825\ud574\uc8fc\uc138\uc694!")
        st.stop()

    with st.spinner("AI\uac00 \ubd84\uc11d \uc911\uc774\uc5d8\uc694... 10~20\ucd08 \uc18c\uc694"):
        try:
            raw = call_openai(api_key, lyrics, genre, concept if concept else "general music channel")
            st.success("\u2728 \ubd84\uc11d \uc644\ub8cc!")
            st.divider()

            sections = parse_sections(raw)
            has_content = any(v.strip() for v in sections.values())

            if not has_content:
                # 섹션 파싱 실패시 전체 출력
                st.markdown('<div class="hd">\U0001f4cb \ubd84\uc11d \uacb0\uacfc</div>', unsafe_allow_html=True)
                st.text_area("result", value=raw, height=600, label_visibility="collapsed")
            else:
                display = [
                    ("emotional-analysis", "\U0001f3ad \uac10\uc131 \ubd84\uc11d", "\uac00\uc0ac\uc758 \uac10\uc131\uacfc \ubd84\uc704\uae30"),
                    ("image-prompt",       "\U0001f3a8 \uc774\ubbf8\uc9c0 \uc0dd\uc131 \ud504\ub86c\ud504\ud2b8", "Midjourney / DALL-E 3 \uc6a9"),
                    ("youtube-titles",     "\U0001f4fa \uc720\ud29c\ube0c \uc81c\ubaa9 3\uac00\uc9c0", "\ub9c8\uc74c\uc5d0 \ub4dc\ub294 \uac83 \uc120\ud0dd"),
                    ("youtube-description","\U0001f4dd \uc720\ud29c\ube0c \uc124\uba85\uae00 & \ud574\uc2dc\ud0dc\uadf8", "\uc124\uba85\ub780\uc5d0 \ubd99\uc5ec\ub123\uae30"),
                ]
                for key, title, tip in display:
                    content = sections[key].strip()
                    if not content:
                        continue
                    st.markdown(f'<div class="hd">{title}</div>', unsafe_allow_html=True)
                    st.caption(tip)
                    st.markdown(f'<div class="box">{content}</div>', unsafe_allow_html=True)
                    st.text_area(
                        "copy",
                        value=content,
                        height=100,
                        label_visibility="collapsed",
                        key="ta_" + key
                    )

            st.info("\U0001f4a1 \ud14d\uc2a4\ud2b8 \ubc15\uc2a4\ub97c \uae38\uac8c \ub20c\ub7ec \uc804\uccb4 \uc120\ud0dd \ud6c4 \ubcf5\uc0ac\ud558\uc138\uc694!")

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if "invalid_api_key" in body or "Unauthorized" in str(e.code):
                st.error("API \ud0a4\uac00 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc544\uc694.")
            elif "quota" in body or "billing" in body:
                st.error("API \ud06c\ub808\ub527\uc774 \ubd80\uc871\ud574\uc694. OpenAI\uc5d0\uc11c \ucda9\uc804\ud574\uc8fc\uc138\uc694.")
            else:
                st.error("HTTP \uc624\ub958 " + str(e.code) + ": " + body[:200])
        except Exception as e:
            st.error("\uc624\ub958: " + str(e))

st.divider()
st.caption("\U0001f3b5 \uac00\uc0ac \uc378\ub124\uc77c & \uc720\ud29c\ube0c \uc815\ubcf4 \uc0dd\uc131\uae30 | Powered by OpenAI GPT-4o mini")
