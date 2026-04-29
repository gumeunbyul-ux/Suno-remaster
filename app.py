# ============================================================
# 🎵 Suno AI 음악 리마스터링 웹 앱
# 작성자: 시니어 파이썬 오디오 엔지니어
# 설명: Streamlit 기반 모바일 최적화 음악 리마스터링 도구
# ============================================================

# --- 필요한 라이브러리 불러오기 ---
import streamlit as st          # 웹 앱 프레임워크
import numpy as np              # 수치 계산 라이브러리
from scipy import signal        # 디지털 신호처리 (필터 적용)
from pydub import AudioSegment  # 오디오 파일 읽기/쓰기
import io                       # 메모리 내 파일 처리
import tempfile                 # 임시 파일 생성
import os                       # 운영체제 파일 경로 처리

# ============================================================
# 🎨 페이지 기본 설정 (반드시 가장 먼저 호출해야 함)
# ============================================================
st.set_page_config(
    page_title="🎵 AI 음악 리마스터",   # 브라우저 탭 제목
    page_icon="🎵",                      # 탭 아이콘
    layout="centered",                   # 중앙 정렬 레이아웃
    initial_sidebar_state="collapsed"    # 사이드바 숨기기 (모바일 최적화)
)

# ============================================================
# 🎨 커스텀 CSS 스타일 (스마트폰 화면에 맞게 디자인)
# ============================================================
st.markdown("""
<style>
    /* 구글 폰트 불러오기 */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    /* 전체 배경 - 딥 다크 그라디언트 */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 40%, #0a0e1a 100%);
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* 메인 컨테이너 최대 너비 (모바일 최적화) */
    .main .block-container {
        max-width: 480px;
        padding: 1rem 1.2rem 3rem 1.2rem;
        margin: 0 auto;
    }

    /* 헤더 제목 스타일 */
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

    /* 섹션 카드 스타일 */
    .section-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(99,202,183,0.15);
        border-radius: 14px;
        padding: 1.4rem 1.2rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(10px);
    }

    .section-title {
        color: #63CAB7;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* 파일 업로더 스타일 개선 */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(99,202,183,0.3) !important;
        border-radius: 12px !important;
        background: rgba(99,202,183,0.04) !important;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99,202,183,0.6) !important;
        background: rgba(99,202,183,0.08) !important;
    }

    /* 슬라이더 스타일 */
    [data-testid="stSlider"] > div > div {
        background: rgba(99,202,183,0.15) !important;
    }

    [data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: #63CAB7 !important;
    }

    /* 버튼 스타일 - 메인 처리 버튼 */
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
        transition: all 0.2s ease;
        text-transform: uppercase;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #21877a 0%, #115954 100%);
        border-color: rgba(99,202,183,0.7);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(99,202,183,0.2);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* 다운로드 버튼 스타일 */
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

    [data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, #3a7050 0%, #234d36 100%);
        border-color: rgba(126,221,155,0.7);
        color: #ffffff;
    }

    /* 성공 메시지 박스 */
    .success-box {
        background: rgba(99,202,183,0.08);
        border: 1px solid rgba(99,202,183,0.3);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
        color: #a8edea;
        font-size: 0.9rem;
    }

    /* 경고/정보 메시지 */
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

    /* Streamlit 기본 텍스트 색상 오버라이드 */
    p, .stMarkdown, label {
        color: rgba(200,220,218,0.85) !important;
    }

    h1, h2, h3 {
        color: #a8edea !important;
    }

    /* 구분선 */
    hr {
        border-color: rgba(99,202,183,0.15) !important;
        margin: 1.5rem 0 !important;
    }

    /* 체크박스 */
    [data-testid="stCheckbox"] label {
        color: rgba(200,220,218,0.85) !important;
        font-size: 0.9rem !important;
    }

    /* 오디오 플레이어 */
    audio {
        width: 100%;
        border-radius: 10px;
        filter: invert(0.85) hue-rotate(155deg);
    }

    /* 프로그레스바 */
    [data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, #63CAB7, #a8edea) !important;
    }

    /* 하단 여백 */
    footer { display: none; }
    #MainMenu { display: none; }
    header { display: none; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 🔧 오디오 처리 함수들 정의
# ============================================================

def pydub_to_numpy(audio_segment):
    """
    pydub AudioSegment 객체를 numpy 배열로 변환하는 함수
    - audio_segment: pydub로 읽어들인 오디오 객체
    - 반환값: numpy 배열, 샘플레이트(Hz), 채널 수
    """
    # 샘플레이트(음악 주파수 샘플링 속도) 가져오기
    sample_rate = audio_segment.frame_rate
    # 채널 수 가져오기 (1: 모노, 2: 스테레오)
    channels = audio_segment.channels
    # 오디오 데이터를 byte 배열로 변환 후 numpy 배열로 변환
    samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)

    # 스테레오인 경우 [샘플수, 2] 형태의 2차원 배열로 변환
    if channels == 2:
        samples = samples.reshape((-1, 2))

    return samples, sample_rate, channels


def numpy_to_pydub(samples, sample_rate, channels, sample_width=2):
    """
    numpy 배열을 다시 pydub AudioSegment 객체로 변환하는 함수
    - samples: numpy 오디오 배열
    - sample_rate: 샘플레이트 (예: 44100)
    - channels: 채널 수 (1 또는 2)
    - sample_width: 비트 깊이 (2 = 16bit)
    """
    # 값 범위를 16비트 정수 범위(-32768 ~ 32767)로 클리핑(잘라내기)
    samples_clipped = np.clip(samples, -32768, 32767)
    # numpy 배열을 16비트 정수(int16)로 변환
    samples_int16 = samples_clipped.astype(np.int16)
    # 1차원 배열로 평탄화 (pydub에서 요구하는 형식)
    samples_flat = samples_int16.flatten()
    # pydub AudioSegment 객체 생성 및 반환
    return AudioSegment(
        data=samples_flat.tobytes(),        # 바이트 데이터
        sample_width=sample_width,          # 샘플 너비 (2 = 16bit)
        frame_rate=sample_rate,             # 샘플레이트
        channels=channels                   # 채널 수
    )


def apply_normalization(samples, target_db=-1.0):
    """
    🔊 Normalization: 음압(볼륨)을 목표 dB 수준으로 표준화하는 함수
    - samples: 오디오 numpy 배열
    - target_db: 목표 최대 음압 (기본값 -1.0 dBFS)
    - 효과: 너무 조용하거나 시끄러운 음악을 적절한 음량으로 맞춤
    """
    # 현재 오디오의 최대 절대값 구하기 (피크 레벨)
    peak = np.max(np.abs(samples))

    # 소리가 거의 없는 경우 (무음) 그대로 반환
    if peak < 1e-6:
        return samples

    # 목표 dB를 선형 배수(gain)로 변환
    # 공식: target_linear = 10^(target_db / 20)
    target_linear = 10 ** (target_db / 20)

    # 16비트 오디오 최대값(32767)에 대한 비율로 계산
    target_amplitude = target_linear * 32767.0

    # 전체 배율(gain) 계산
    gain = target_amplitude / peak

    # 배율 적용하여 정규화된 오디오 반환
    return samples * gain


def apply_bass_boost(samples, sample_rate, gain_db=6.0, freq=150.0):
    """
    🎸 Bass Boost: 저음부(베이스)를 강화하는 함수
    - samples: 오디오 numpy 배열
    - sample_rate: 샘플레이트
    - gain_db: 베이스 증폭량 (기본값 6 dB)
    - freq: 저역 통과 차단 주파수 (기본값 150Hz)
    - 효과: 킥드럼, 베이스 기타 등 저음을 풍성하게 만듦
    """
    # 나이퀴스트 주파수 (샘플레이트의 절반 = 최대 표현 가능 주파수)
    nyquist = sample_rate / 2.0

    # 정규화된 차단 주파수 계산 (0~1 사이 값으로 변환)
    cutoff_normalized = freq / nyquist

    # Butterworth 저역통과 필터 설계 (2차 필터)
    # - btype='low': 저역통과 필터 (낮은 주파수만 통과)
    b, a = signal.butter(2, cutoff_normalized, btype='low')

    # dB 증폭량을 선형 배수로 변환
    gain_linear = 10 ** (gain_db / 20)

    # 스테레오/모노 처리 분기
    if samples.ndim == 2:
        # 스테레오: 왼쪽/오른쪽 채널 각각 필터 적용
        boosted = np.zeros_like(samples)
        for ch in range(samples.shape[1]):
            # 저역통과 필터로 베이스 성분만 추출
            bass_component = signal.filtfilt(b, a, samples[:, ch])
            # 원본 + (추출된 베이스 × 증폭량)
            boosted[:, ch] = samples[:, ch] + bass_component * (gain_linear - 1.0)
    else:
        # 모노: 단일 채널 처리
        bass_component = signal.filtfilt(b, a, samples)
        boosted = samples + bass_component * (gain_linear - 1.0)

    return boosted


def apply_treble_clarity(samples, sample_rate, noise_reduction_db=4.0, clarity_gain_db=3.0, cutoff_freq=8000.0):
    """
    ✨ Treble Clarity: 고음부 선명도 향상 및 노이즈 억제 함수
    - samples: 오디오 numpy 배열
    - sample_rate: 샘플레이트
    - noise_reduction_db: 고음 노이즈 감쇠량 (기본값 4 dB)
    - clarity_gain_db: 고음 선명도 증폭량 (기본값 3 dB)
    - cutoff_freq: 고역 처리 시작 주파수 (기본값 8000Hz)
    - 효과: 보컬, 기타 피킹 등 고음을 선명하게, 하이스 노이즈 억제
    """
    nyquist = sample_rate / 2.0
    # 고역 처리 주파수가 나이퀴스트를 넘지 않도록 보정
    cutoff_normalized = min(cutoff_freq / nyquist, 0.95)

    # 단계 1: 고역통과 필터로 고음 성분만 추출
    b_high, a_high = signal.butter(2, cutoff_normalized, btype='high')

    # 단계 2: 낮은 차단 주파수의 저역통과 필터로 노이즈 성분 추출
    noise_cutoff = min(12000.0 / nyquist, 0.98)
    b_noise, a_noise = signal.butter(3, noise_cutoff, btype='low')

    # dB 값들을 선형 배수로 변환
    noise_reduction = 10 ** (-noise_reduction_db / 20)  # 감쇠 (1보다 작은 값)
    clarity_gain = 10 ** (clarity_gain_db / 20)          # 증폭 (1보다 큰 값)

    if samples.ndim == 2:
        # 스테레오 처리
        result = np.zeros_like(samples)
        for ch in range(samples.shape[1]):
            # 고음 성분 추출
            high_freq = signal.filtfilt(b_high, a_high, samples[:, ch])
            # 고음 노이즈 성분 추출 (초고주파 노이즈)
            noise_component = samples[:, ch] - signal.filtfilt(b_noise, a_noise, samples[:, ch])
            # 원본 - 노이즈(억제) + 고음(선명도 증폭)
            result[:, ch] = (samples[:, ch]
                             - noise_component * (1 - noise_reduction)
                             + high_freq * (clarity_gain - 1.0))
    else:
        # 모노 처리
        high_freq = signal.filtfilt(b_high, a_high, samples)
        noise_component = samples - signal.filtfilt(b_noise, a_noise, samples)
        result = (samples
                  - noise_component * (1 - noise_reduction)
                  + high_freq * (clarity_gain - 1.0))

    return result


def apply_limiter(samples, threshold_db=-0.5):
    """
    🛡️ Limiter: 소리 깨짐(클리핑) 방지 리미터 함수
    - samples: 오디오 numpy 배열
    - threshold_db: 한계 임계값 (기본값 -0.5 dBFS)
    - 효과: 음량이 갑자기 폭발적으로 커지는 순간을 부드럽게 제한
    """
    # 임계값을 선형 배수로 변환 (16비트 최대값 기준)
    threshold_linear = (10 ** (threshold_db / 20)) * 32767.0

    # 각 샘플의 절대값 계산
    abs_samples = np.abs(samples)

    # 소프트 클리핑 적용 (tanh 함수 사용 - 부드러운 제한)
    # 임계값을 넘는 신호는 tanh으로 부드럽게 압축
    over_threshold = abs_samples > threshold_linear
    limited = np.where(
        over_threshold,
        # 임계값 초과 시: tanh 소프트 클리핑
        np.sign(samples) * threshold_linear * (1 + np.tanh((abs_samples - threshold_linear) / threshold_linear) * 0.1),
        # 임계값 이하 시: 원본 그대로
        samples
    )

    # 최종 안전 클리핑 (절대로 16비트 범위 초과 방지)
    return np.clip(limited, -32767, 32767)


def remaster_audio(audio_segment, settings):
    """
    🎵 메인 리마스터링 파이프라인 함수
    - audio_segment: pydub AudioSegment 오디오 객체
    - settings: 처리 옵션 딕셔너리 (각 효과 ON/OFF 및 파라미터)
    - 반환값: 리마스터링된 pydub AudioSegment 객체
    """
    # 안정적인 처리를 위해 44100Hz 스테레오로 변환
    audio_segment = audio_segment.set_frame_rate(44100).set_channels(2)

    # pydub 객체를 numpy 배열로 변환
    samples, sample_rate, channels = pydub_to_numpy(audio_segment)

    # 처리 진행 상황 표시를 위한 Streamlit 프로그레스바 초기화
    progress_bar = st.progress(0)
    status_text = st.empty()

    # ----- 단계 1: Normalization (음압 표준화) -----
    status_text.text("⚙️ 단계 1/4: 음압 표준화 중...")
    progress_bar.progress(15)
    if settings.get('normalization', True):
        samples = apply_normalization(samples, target_db=settings.get('norm_target_db', -1.0))

    # ----- 단계 2: Bass Boost (저음 강화) -----
    status_text.text("⚙️ 단계 2/4: 베이스 강화 중...")
    progress_bar.progress(40)
    if settings.get('bass_boost', True):
        samples = apply_bass_boost(
            samples, sample_rate,
            gain_db=settings.get('bass_gain_db', 6.0),
            freq=150.0
        )

    # ----- 단계 3: Treble Clarity (고음 선명도) -----
    status_text.text("⚙️ 단계 3/4: 고음 선명도 향상 중...")
    progress_bar.progress(65)
    if settings.get('treble_clarity', True):
        samples = apply_treble_clarity(
            samples, sample_rate,
            noise_reduction_db=settings.get('treble_noise_db', 4.0),
            clarity_gain_db=settings.get('treble_clarity_db', 3.0)
        )

    # ----- 단계 4: Limiter (클리핑 방지) -----
    status_text.text("⚙️ 단계 4/4: 리미터 적용 중...")
    progress_bar.progress(85)
    if settings.get('limiter', True):
        samples = apply_limiter(samples, threshold_db=-0.5)

    # 완료 표시
    progress_bar.progress(100)
    status_text.text("✅ 리마스터링 완료!")

    # numpy 배열을 다시 pydub 객체로 변환
    result_audio = numpy_to_pydub(samples, sample_rate, channels)

    return result_audio


def export_mp3_320kbps(audio_segment):
    """
    📦 오디오를 320kbps MP3로 내보내기 함수
    - audio_segment: pydub AudioSegment 객체
    - 반환값: MP3 바이트 데이터 (다운로드용)
    """
    # 메모리 버퍼에 MP3 파일 저장
    buffer = io.BytesIO()
    # 320kbps 고음질 MP3로 내보내기
    audio_segment.export(
        buffer,
        format="mp3",
        bitrate="320k",
        parameters=["-q:a", "0"]  # 최고 품질 설정
    )
    # 버퍼 처음으로 되돌리기 (읽기 위해)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# 🖥️ UI 렌더링 시작
# ============================================================

# ----- 앱 헤더 -----
st.markdown("""
<div class="app-header">
    <div class="app-title">🎵 AI REMASTER</div>
    <div class="app-subtitle">SUNO AI 음악 고음질 리마스터링</div>
</div>
""", unsafe_allow_html=True)

# ----- 안내 메시지 -----
st.markdown("""
<div class="info-box">
    💡 <strong>사용 방법</strong><br>
    MP3 또는 WAV 파일을 업로드하면, 전문 음향 처리를 통해<br>
    음질을 개선하고 320kbps MP3로 다운로드할 수 있어요.
</div>
""", unsafe_allow_html=True)

# ============================================================
# 📁 파일 업로드 섹션
# ============================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📁 파일 업로드</div>', unsafe_allow_html=True)

# 파일 업로더 위젯 (MP3, WAV 지원)
uploaded_file = st.file_uploader(
    "MP3 또는 WAV 파일을 선택하세요",
    type=["mp3", "wav"],
    help="최대 200MB까지 업로드 가능합니다"
)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ⚙️ 리마스터링 설정 섹션
# ============================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚙️ 리마스터링 설정</div>', unsafe_allow_html=True)

# --- Normalization 설정 ---
use_normalization = st.checkbox("🔊 Normalization (음압 표준화)", value=True,
    help="음악 전체 볼륨을 최적 레벨로 맞춥니다")
norm_target_db = -1.0  # 기본값 (고정)

# --- Bass Boost 설정 ---
use_bass_boost = st.checkbox("🎸 Bass Boost (저음 강화)", value=True,
    help="150Hz 이하 베이스 음역을 강화합니다")
# 베이스 부스트 강도 슬라이더 (체크박스가 켜진 경우만 표시)
if use_bass_boost:
    bass_gain = st.slider(
        "베이스 강도",
        min_value=2.0, max_value=12.0, value=6.0, step=1.0,
        format="%.0f dB",
        help="숫자가 클수록 베이스가 더 강해집니다 (권장: 4~8 dB)"
    )
else:
    bass_gain = 6.0  # 비활성화 시 기본값 (사용 안 됨)

# --- Treble Clarity 설정 ---
use_treble = st.checkbox("✨ Treble Clarity (고음 선명도)", value=True,
    help="8kHz 이상 고음역을 선명하게, 노이즈를 억제합니다")
if use_treble:
    treble_clarity_level = st.slider(
        "고음 선명도",
        min_value=1.0, max_value=6.0, value=3.0, step=0.5,
        format="%.1f dB",
        help="숫자가 클수록 고음이 더 또렷해집니다 (권장: 2~4 dB)"
    )
    treble_noise_level = st.slider(
        "노이즈 억제",
        min_value=1.0, max_value=8.0, value=4.0, step=0.5,
        format="%.1f dB",
        help="숫자가 클수록 고주파 노이즈가 더 많이 제거됩니다"
    )
else:
    treble_clarity_level = 3.0
    treble_noise_level = 4.0

# --- Limiter 설정 ---
use_limiter = st.checkbox("🛡️ Limiter (소리 깨짐 방지)", value=True,
    help="음량이 갑자기 폭발하는 것을 방지합니다")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 🚀 리마스터링 처리 버튼 & 결과
# ============================================================

# 파일이 업로드된 경우에만 처리 버튼 표시
if uploaded_file is not None:

    # 파일 정보 표시
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.markdown(f"""
    <div class="success-box">
        ✅ 파일 업로드 완료<br>
        📄 <strong>{uploaded_file.name}</strong><br>
        📦 크기: {file_size_mb:.1f} MB
    </div>
    """, unsafe_allow_html=True)

    # 리마스터링 시작 버튼
    if st.button("🎵 리마스터링 시작", use_container_width=True):

        # 처리 설정 딕셔너리 구성
        settings = {
            'normalization':    use_normalization,
            'norm_target_db':   norm_target_db,
            'bass_boost':       use_bass_boost,
            'bass_gain_db':     bass_gain if use_bass_boost else 0,
            'treble_clarity':   use_treble,
            'treble_clarity_db': treble_clarity_level if use_treble else 0,
            'treble_noise_db':  treble_noise_level if use_treble else 0,
            'limiter':          use_limiter,
        }

        try:
            # 임시 파일에 업로드된 내용 저장 후 pydub으로 읽기
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.' + uploaded_file.name.split('.')[-1]  # 확장자 유지
            ) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())  # 업로드 파일 내용 쓰기
                tmp_path = tmp_file.name

            # pydub으로 오디오 파일 읽기
            audio = AudioSegment.from_file(tmp_path)
            # 임시 파일 삭제
            os.unlink(tmp_path)

            # 🎵 리마스터링 처리 실행
            remastered_audio = remaster_audio(audio, settings)

            # ---- 원본 vs 리마스터링 비교 미리듣기 ----
            st.markdown("---")
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🎧 비교 미리듣기</div>', unsafe_allow_html=True)

            # 원본 미리듣기
            st.markdown("**원본 (Original)**")
            original_buffer = io.BytesIO()
            audio.export(original_buffer, format="mp3", bitrate="192k")
            original_buffer.seek(0)
            st.audio(original_buffer.getvalue(), format="audio/mp3")

            # 리마스터링 결과 미리듣기
            st.markdown("**리마스터링 결과 (Remastered)**")
            preview_buffer = io.BytesIO()
            remastered_audio.export(preview_buffer, format="mp3", bitrate="320k")
            preview_buffer.seek(0)
            st.audio(preview_buffer.getvalue(), format="audio/mp3")

            st.markdown('</div>', unsafe_allow_html=True)

            # ---- 320kbps MP3 다운로드 ----
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📥 고음질 다운로드</div>', unsafe_allow_html=True)

            # 다운로드용 MP3 생성
            mp3_data = export_mp3_320kbps(remastered_audio)

            # 원본 파일명에서 확장자 제거 후 '_remastered' 추가
            original_name = os.path.splitext(uploaded_file.name)[0]
            download_filename = f"{original_name}_remastered_320k.mp3"

            # 다운로드 버튼
            st.download_button(
                label="⬇️ 320kbps MP3 다운로드",
                data=mp3_data,
                file_name=download_filename,
                mime="audio/mpeg",
                use_container_width=True
            )

            # 다운로드 안내
            st.markdown("""
            <div class="info-box">
                💾 다운로드 후 스마트폰 파일 앱 또는 음악 앱에서 바로 재생 가능합니다.
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            # 오류 발생 시 사용자 친화적 메시지 표시
            st.error(f"""
            ⚠️ 처리 중 오류가 발생했습니다.

            **오류 내용:** {str(e)}

            **해결 방법:**
            - MP3 또는 WAV 파일만 지원합니다
            - 파일이 손상되지 않았는지 확인하세요
            - 파일 크기가 200MB 이하인지 확인하세요
            """)

else:
    # 파일 미업로드 상태 안내
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0; color: rgba(99,202,183,0.4);">
        <div style="font-size: 3rem;">🎵</div>
        <div style="font-size: 0.85rem; margin-top: 0.5rem;">
            위에서 음악 파일을 업로드해주세요
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 📝 하단 설명 (처리 알고리즘 정보)
# ============================================================
st.markdown("---")
st.markdown("""
<div style="font-size: 0.75rem; color: rgba(99,202,183,0.35); text-align:center; padding-bottom: 2rem; line-height: 1.8;">
    🔊 Normalization → 🎸 Bass Boost (150Hz) → ✨ Treble Clarity → 🛡️ Limiter<br>
    출력: 44.1kHz Stereo · 320kbps MP3
</div>
""", unsafe_allow_html=True)
