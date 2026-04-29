# ============================================================
# 🎵 Suno AI 음악 리마스터링 웹 앱 (ffmpeg 불필요 버전)
# 작성자: 시니어 파이썬 오디오 엔지니어
# 설명: Streamlit 기반 모바일 최적화 음악 리마스터링 도구
# ============================================================

# --- 필요한 라이브러리 불러오기 ---
import streamlit as st          # 웹 앱 프레임워크
import numpy as np              # 수치 계산 라이브러리
from scipy import signal        # 디지털 신호처리 (필터 적용)
from scipy.io import wavfile    # WAV 파일 읽기/쓰기
import io                       # 메모리 내 파일 처리
import struct                   # 바이너리 데이터 처리
import tempfile                 # 임시 파일 생성
import os                       # 운영체제 파일 경로 처리

# ============================================================
# 🎨 페이지 기본 설정
# ============================================================
st.set_page_config(
    page_title="🎵 AI 음악 리마스터",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 🎨 커스텀 CSS 스타일
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 40%, #0a0e1a 100%);
        font-family: 'Noto Sans KR', sans-serif;
    }
    .main .block-container {
        max-width: 480px;
        padding: 1rem 1.2rem 3rem 1.2rem;
        margin: 0 auto;
    }
    .app-header {
        text-align: center;
        padding: 2rem 0 1.5rem 0;
        background: linear-gradient(180deg, rgba(99,202,183,0.08) 0%, transparent 100%);
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(99,202,183,0.12);
    }
    .app-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #63CAB7, #a8edea, #63CAB7);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s linear infinite;
        letter-spacing: 2px;
        margin: 0;
    }
    @keyframes shimmer {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    .app-subtitle {
        color: rgba(99,202,183,0.6);
        font-size: 0.82rem;
        margin-top: 0.4rem;
        letter-spacing: 1px;
        font-weight: 300;
    }
    .section-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(99,202,183,0.15);
        border-radius: 14px;
        padding: 1.4rem 1.2rem;
        margin-bottom: 1.2rem;
    }
    .section-title {
        color: #63CAB7;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }
    .success-box {
        background: rgba(99,202,183,0.08);
        border: 1px solid rgba(99,202,183,0.3);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        color: #a8edea;
        font-size: 0.9rem;
    }
    .info-box {
        background: rgba(255,200,100,0.06);
        border: 1px solid rgba(255,200,100,0.2);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.8rem 0;
        color: rgba(255,200,100,0.8);
        font-size: 0.82rem;
        line-height: 1.5;
    }
    p, .stMarkdown, label { color: rgba(200,220,218,0.85) !important; }
    h1, h2, h3 { color: #a8edea !important; }
    hr { border-color: rgba(99,202,183,0.15) !important; margin: 1.5rem 0 !important; }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1a6b60 0%, #0d4a42 100%);
        color: #a8edea;
        border: 1px solid rgba(99,202,183,0.4);
        border-radius: 12px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 2px;
        padding: 0.75rem 1.5rem;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #21877a 0%, #115954 100%);
        color: #ffffff;
    }
    [data-testid="stDownloadButton"] > button {
        width: 100%;
        background: linear-gradient(135deg, #2d5a3d 0%, #1a3d2a 100%);
        color: #7edd9b;
        border: 1px solid rgba(126,221,155,0.4);
        border-radius: 12px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 2px;
        padding: 0.75rem 1.5rem;
        text-transform: uppercase;
    }
    footer { display: none; }
    #MainMenu { display: none; }
    header { display: none; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 🔧 MP3 디코딩 함수 (minimp3 / pydub 없이 처리)
# ============================================================

def read_audio_file(uploaded_file):
    """
    업로드된 오디오 파일을 numpy 배열로 읽는 함수
    MP3는 soundfile로, WAV는 scipy로 처리
    """
    file_bytes = uploaded_file.getvalue()  # 파일 내용을 바이트로 읽기
    file_ext = uploaded_file.name.split('.')[-1].lower()  # 확장자 추출

    if file_ext == 'wav':
        # WAV 파일: scipy로 직접 읽기
        buf = io.BytesIO(file_bytes)
        sample_rate, samples = wavfile.read(buf)

        # 데이터 타입을 float32로 변환
        if samples.dtype == np.int16:
            samples = samples.astype(np.float32)
        elif samples.dtype == np.int32:
            samples = (samples / 2147483648.0 * 32767.0).astype(np.float32)
        elif samples.dtype == np.float32 or samples.dtype == np.float64:
            samples = (samples * 32767.0).astype(np.float32)

        # 모노인 경우 스테레오로 변환
        if samples.ndim == 1:
            samples = np.stack([samples, samples], axis=1)

        return samples, sample_rate

    else:
        # MP3 파일: soundfile + pydub 없이 처리
        # soundfile은 MP3를 못 읽으므로 pydub 대신 minimp3py 시도
        try:
            import minimp3py
            buf = io.BytesIO(file_bytes)
            frames = []
            sample_rate = 44100
            while True:
                frame_info, pcm = minimp3py.decode_frame(buf)
                if frame_info is None:
                    break
                sample_rate = frame_info.hz
                frames.append(pcm)
            if frames:
                samples = np.concatenate(frames, axis=0).astype(np.float32)
                if samples.ndim == 1:
                    samples = np.stack([samples, samples], axis=1)
                return samples, sample_rate
        except Exception:
            pass

        # 최후 방법: pydub (ffmpeg 없이 pure python mp3 decoder)
        try:
            from pydub import AudioSegment
            buf = io.BytesIO(file_bytes)
            audio = AudioSegment.from_file(buf, format="mp3")
            audio = audio.set_frame_rate(44100).set_channels(2)
            samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
            samples = samples.reshape((-1, 2))
            return samples, 44100
        except Exception as e:
            raise Exception(f"MP3 읽기 실패: {str(e)}\n\nWAV 파일로 변환 후 업로드해보세요.")


def samples_to_wav_bytes(samples, sample_rate):
    """
    numpy 배열을 WAV 바이트로 변환 (다운로드용)
    """
    # 16비트 정수로 변환
    samples_clipped = np.clip(samples, -32768, 32767).astype(np.int16)
    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, samples_clipped)
    buf.seek(0)
    return buf.getvalue()


# ============================================================
# 🔧 오디오 처리 함수들
# ============================================================

def apply_normalization(samples, target_db=-1.0):
    """🔊 Normalization: 음압 표준화"""
    peak = np.max(np.abs(samples))
    if peak < 1e-6:
        return samples
    target_linear = 10 ** (target_db / 20)
    target_amplitude = target_linear * 32767.0
    gain = target_amplitude / peak
    return samples * gain


def apply_bass_boost(samples, sample_rate, gain_db=6.0, freq=150.0):
    """🎸 Bass Boost: 저음 강화"""
    nyquist = sample_rate / 2.0
    cutoff_normalized = freq / nyquist
    b, a = signal.butter(2, cutoff_normalized, btype='low')
    gain_linear = 10 ** (gain_db / 20)

    if samples.ndim == 2:
        boosted = np.zeros_like(samples)
        for ch in range(samples.shape[1]):
            bass_component = signal.filtfilt(b, a, samples[:, ch])
            boosted[:, ch] = samples[:, ch] + bass_component * (gain_linear - 1.0)
    else:
        bass_component = signal.filtfilt(b, a, samples)
        boosted = samples + bass_component * (gain_linear - 1.0)
    return boosted


def apply_treble_clarity(samples, sample_rate, noise_reduction_db=4.0, clarity_gain_db=3.0):
    """✨ Treble Clarity: 고음 선명도 향상"""
    nyquist = sample_rate / 2.0
    cutoff_normalized = min(8000.0 / nyquist, 0.95)
    b_high, a_high = signal.butter(2, cutoff_normalized, btype='high')
    noise_cutoff = min(12000.0 / nyquist, 0.98)
    b_noise, a_noise = signal.butter(3, noise_cutoff, btype='low')
    noise_reduction = 10 ** (-noise_reduction_db / 20)
    clarity_gain = 10 ** (clarity_gain_db / 20)

    if samples.ndim == 2:
        result = np.zeros_like(samples)
        for ch in range(samples.shape[1]):
            high_freq = signal.filtfilt(b_high, a_high, samples[:, ch])
            noise_component = samples[:, ch] - signal.filtfilt(b_noise, a_noise, samples[:, ch])
            result[:, ch] = (samples[:, ch]
                             - noise_component * (1 - noise_reduction)
                             + high_freq * (clarity_gain - 1.0))
    else:
        high_freq = signal.filtfilt(b_high, a_high, samples)
        noise_component = samples - signal.filtfilt(b_noise, a_noise, samples)
        result = (samples
                  - noise_component * (1 - noise_reduction)
                  + high_freq * (clarity_gain - 1.0))
    return result


def apply_limiter(samples, threshold_db=-0.5):
    """🛡️ Limiter: 소리 깨짐 방지"""
    threshold_linear = (10 ** (threshold_db / 20)) * 32767.0
    abs_samples = np.abs(samples)
    over_threshold = abs_samples > threshold_linear
    limited = np.where(
        over_threshold,
        np.sign(samples) * threshold_linear * (1 + np.tanh((abs_samples - threshold_linear) / threshold_linear) * 0.1),
        samples
    )
    return np.clip(limited, -32767, 32767)


def remaster_audio(samples, sample_rate, settings):
    """🎵 메인 리마스터링 파이프라인"""
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("⚙️ 단계 1/4: 음압 표준화 중...")
    progress_bar.progress(15)
    if settings.get('normalization', True):
        samples = apply_normalization(samples, target_db=-1.0)

    status_text.text("⚙️ 단계 2/4: 베이스 강화 중...")
    progress_bar.progress(40)
    if settings.get('bass_boost', True):
        samples = apply_bass_boost(samples, sample_rate, gain_db=settings.get('bass_gain_db', 6.0))

    status_text.text("⚙️ 단계 3/4: 고음 선명도 향상 중...")
    progress_bar.progress(65)
    if settings.get('treble_clarity', True):
        samples = apply_treble_clarity(
            samples, sample_rate,
            noise_reduction_db=settings.get('treble_noise_db', 4.0),
            clarity_gain_db=settings.get('treble_clarity_db', 3.0)
        )

    status_text.text("⚙️ 단계 4/4: 리미터 적용 중...")
    progress_bar.progress(85)
    if settings.get('limiter', True):
        samples = apply_limiter(samples)

    progress_bar.progress(100)
    status_text.text("✅ 리마스터링 완료!")
    return samples


# ============================================================
# 🖥️ UI 렌더링
# ============================================================

st.markdown("""
<div class="app-header">
    <div class="app-title">🎵 AI REMASTER</div>
    <div class="app-subtitle">SUNO AI 음악 고음질 리마스터링</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    💡 <strong>사용 방법</strong><br>
    MP3 또는 WAV 파일을 업로드하면 전문 음향 처리 후<br>
    고음질 WAV 파일로 다운로드할 수 있어요.
</div>
""", unsafe_allow_html=True)

# 파일 업로드
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📁 파일 업로드</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "MP3 또는 WAV 파일을 선택하세요",
    type=["mp3", "wav"],
    help="최대 200MB까지 업로드 가능합니다"
)
st.markdown('</div>', unsafe_allow_html=True)

# 설정
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚙️ 리마스터링 설정</div>', unsafe_allow_html=True)

use_normalization = st.checkbox("🔊 Normalization (음압 표준화)", value=True)
use_bass_boost = st.checkbox("🎸 Bass Boost (저음 강화)", value=True)
if use_bass_boost:
    bass_gain = st.slider("베이스 강도", 2.0, 12.0, 6.0, 1.0, format="%.0f dB")
else:
    bass_gain = 6.0

use_treble = st.checkbox("✨ Treble Clarity (고음 선명도)", value=True)
if use_treble:
    treble_clarity_level = st.slider("고음 선명도", 1.0, 6.0, 3.0, 0.5, format="%.1f dB")
    treble_noise_level = st.slider("노이즈 억제", 1.0, 8.0, 4.0, 0.5, format="%.1f dB")
else:
    treble_clarity_level = 3.0
    treble_noise_level = 4.0

use_limiter = st.checkbox("🛡️ Limiter (소리 깨짐 방지)", value=True)
st.markdown('</div>', unsafe_allow_html=True)

# 처리 및 결과
if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.markdown(f"""
    <div class="success-box">
        ✅ 파일 업로드 완료<br>
        📄 <strong>{uploaded_file.name}</strong><br>
        📦 크기: {file_size_mb:.1f} MB
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎵 리마스터링 시작", use_container_width=True):
        settings = {
            'normalization':     use_normalization,
            'bass_boost':        use_bass_boost,
            'bass_gain_db':      bass_gain,
            'treble_clarity':    use_treble,
            'treble_clarity_db': treble_clarity_level,
            'treble_noise_db':   treble_noise_level,
            'limiter':           use_limiter,
        }

        try:
            # 오디오 읽기
            with st.spinner("파일 읽는 중..."):
                samples, sample_rate = read_audio_file(uploaded_file)

            # 리마스터링 처리
            remastered = remaster_audio(samples, sample_rate, settings)

            # WAV로 변환
            wav_bytes = samples_to_wav_bytes(remastered, sample_rate)
            original_wav = samples_to_wav_bytes(samples, sample_rate)

            # 비교 미리듣기
            st.markdown("---")
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🎧 비교 미리듣기</div>', unsafe_allow_html=True)
            st.markdown("**원본 (Original)**")
            st.audio(original_wav, format="audio/wav")
            st.markdown("**리마스터링 결과 (Remastered)**")
            st.audio(wav_bytes, format="audio/wav")
            st.markdown('</div>', unsafe_allow_html=True)

            # 다운로드
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📥 고음질 다운로드</div>', unsafe_allow_html=True)
            original_name = os.path.splitext(uploaded_file.name)[0]
            st.download_button(
                label="⬇️ 고음질 WAV 다운로드",
                data=wav_bytes,
                file_name=f"{original_name}_remastered.wav",
                mime="audio/wav",
                use_container_width=True
            )
            st.markdown("""
            <div class="info-box">
                💾 WAV는 무손실 포맷이라 MP3보다 음질이 더 좋아요!
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"""
            ⚠️ 처리 중 오류가 발생했습니다.

            **오류 내용:** {str(e)}

            **해결 방법:**
            - WAV 파일로 변환 후 업로드해보세요
            - 파일이 손상되지 않았는지 확인하세요
            """)
else:
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0; color: rgba(99,202,183,0.4);">
        <div style="font-size: 3rem;">🎵</div>
        <div style="font-size: 0.85rem; margin-top: 0.5rem;">위에서 음악 파일을 업로드해주세요</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="font-size: 0.75rem; color: rgba(99,202,183,0.35); text-align:center; padding-bottom: 2rem;">
    🔊 Normalization → 🎸 Bass Boost → ✨ Treble Clarity → 🛡️ Limiter
</div>
""", unsafe_allow_html=True)
