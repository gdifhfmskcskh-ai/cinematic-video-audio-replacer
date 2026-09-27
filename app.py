import os
import subprocess
import tempfile
from pathlib import Path

import streamlit as st
import imageio_ffmpeg

st.set_page_config(
    page_title="Cinematic Video Audio Replacer",
    page_icon="✨",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(rgba(3, 7, 18, 0.65), rgba(3, 7, 18, 0.65)),
            url("https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?q=80&w=1920&auto=format&fit=crop")
            center center / cover fixed no-repeat;
        min-height: 100vh;
    }
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(3, 7, 18, 0.15);
        pointer-events: none;
        z-index: 0;
    }
    .main .block-container {
        position: relative;
        z-index: 1;
        max-width: 1100px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }
    .glass-card {
        background: rgba(11, 15, 25, 0.65);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 22px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.28),
                    inset 0 1px 0 rgba(255, 255, 255, 0.06);
    }
    .hero {
        text-align: center;
        padding: 2rem 1rem 1.5rem;
    }
    .hero-title {
        font-size: clamp(2.2rem, 6vw, 4.5rem);
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #ffffff;
        margin: 0;
        line-height: 1.05;
        text-shadow: 0 8px 35px rgba(0, 0, 0, 0.5);
    }
    .hero-gradient {
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #e879f9 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.78);
        font-size: 1.05rem;
        margin-top: 0.9rem;
    }
    .section-title {
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.035);
        border: 1px dashed rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 0.5rem;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.025);
        border-radius: 14px;
    }
    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        min-height: 3.2rem;
        border: none !important;
        border-radius: 14px !important;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.28);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 38px rgba(168, 85, 247, 0.38);
        color: #ffffff !important;
    }
    .stButton > button *,
    .stDownloadButton > button * {
        color: #ffffff !important;
    }
    .stButton > button:disabled {
        background: rgba(99, 102, 241, 0.35) !important;
        color: rgba(255, 255, 255, 0.6) !important;
    }
    .success-card {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(52, 211, 153, 0.25);
        border-radius: 16px;
        padding: 1rem;
        color: #d1fae5;
    }
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.45);
        font-size: 0.85rem;
        padding-top: 1rem;
    }
    #MainMenu, footer {
        visibility: hidden;
    }
    header {
        background: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

VIDEO_EXTENSIONS = {"mp4", "mov", "mkv", "avi"}
AUDIO_EXTENSIONS = {"mp3", "wav", "m4a", "aac"}


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower().replace(".", "")


def save_uploaded_file(uploaded_file, destination: str) -> None:
    with open(destination, "wb") as file:
        file.write(uploaded_file.getbuffer())


def process_video(video_path: str, audio_path: str, output_path: str) -> None:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg_exe,
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr[-5000:])


st.markdown(
    """
    <div class="hero">
        <h1 class="hero-title">
            Cinematic <span class="hero-gradient">Audio Replacer</span>
        </h1>
        <p class="hero-subtitle">
            Replace your video's soundtrack with a new cinematic audio track.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🎬 Upload Your Media</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("#### 🎥 Video")
    video_file = st.file_uploader(
        "Choose a video file",
        type=list(VIDEO_EXTENSIONS),
        key="video_uploader",
        help="Supported formats: MP4, MOV, MKV, AVI",
    )
    if video_file is not None:
        if get_extension(video_file.name) not in VIDEO_EXTENSIONS:
            st.error("Unsupported video format.")
        else:
            st.success(f"Selected: {video_file.name}")
            st.video(video_file)

with col2:
    st.markdown("#### 🎵 New Audio")
    audio_file = st.file_uploader(
        "Choose an audio file",
        type=list(AUDIO_EXTENSIONS),
        key="audio_uploader",
        help="Supported formats: MP3, WAV, M4A, AAC",
    )
    if audio_file is not None:
        if get_extension(audio_file.name) not in AUDIO_EXTENSIONS:
            st.error("Unsupported audio format.")
        else:
            st.success(f"Selected: {audio_file.name}")
            st.audio(audio_file)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">✨ Create Your Cinematic Video</div>', unsafe_allow_html=True)

can_process = video_file is not None and audio_file is not None

process_clicked = st.button(
    "✨ Process & Generate Video Now",
    disabled=not can_process,
    use_container_width=True,
)

if not can_process:
    st.info("Please upload both a video and an audio file to continue.")

if process_clicked:
    video_extension = get_extension(video_file.name)
    audio_extension = get_extension(audio_file.name)

    if video_extension not in VIDEO_EXTENSIONS:
        st.error("Please select a supported video format.")
        st.stop()

    if audio_extension not in AUDIO_EXTENSIONS:
        st.error("Please select a supported audio format.")
        st.stop()

    with st.spinner("🎬 Processing your cinematic video..."):
        temp_dir = tempfile.mkdtemp(prefix="cinematic_audio_")
        video_path = os.path.join(temp_dir, f"input_video.{video_extension}")
        audio_path = os.path.join(temp_dir, f"input_audio.{audio_extension}")
        output_path = os.path.join(temp_dir, "cinematic_audio_replaced.mp4")

        try:
            save_uploaded_file(video_file, video_path)
            save_uploaded_file(audio_file, audio_path)

            process_video(video_path, audio_path, output_path)

            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise RuntimeError("FFmpeg completed but no valid output video was created.")

            st.session_state["processed_video"] = output_path
            st.success("🎉 Your cinematic video has been generated successfully!")

        except Exception as error:
            st.error("❌ Video processing failed.")
            with st.expander("Technical details"):
                st.code(str(error))

st.markdown("</div>", unsafe_allow_html=True)

if "processed_video" in st.session_state:
    output_path = st.session_state["processed_video"]

    if os.path.exists(output_path):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎞️ Final Cinematic Video</div>', unsafe_allow_html=True)

        st.video(output_path)

        with open(output_path, "rb") as output_file:
            output_data = output_file.read()

        st.download_button(
            label="⬇️ Download Final Cinematic Video",
            data=output_data,
            file_name="cinematic_audio_replaced.mp4",
            mime="video/mp4",
            use_container_width=True,
        )

        st.markdown(
            """
            <div class="success-card" style="margin-top: 1rem;">
                ✅ Your final MP4 is ready. The original video stream
                has been preserved while the new audio track has been added.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer">
        Cinematic Video Audio Replacer • Powered by Streamlit + FFmpeg
    </div>
    """,
    unsafe_allow_html=True,
)
