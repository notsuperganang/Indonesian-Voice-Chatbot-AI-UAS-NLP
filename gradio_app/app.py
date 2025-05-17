import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile
import time
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('voice_chatbot_frontend')

# Path to store chat history
HISTORY_PATH = os.path.join(tempfile.gettempdir(), "voice_chat_history.json")
API_URL = "http://localhost:8000/voice-chat"
REQUEST_TIMEOUT = 60  # Increased timeout to 60 seconds

# Load existing chat history or create empty one
def load_chat_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load chat history: {e}")
            return []
    return []

# Save chat history
def save_chat_history(history):
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save chat history: {e}")

# Voice chat function with improved error handling and debugging
def voice_chat(audio, history, progress=gr.Progress()):
    if audio is None:
        return None, history, "⚠️ Mohon rekam suara terlebih dahulu"
    
    # Update timestamp
    timestamp = datetime.now().strftime("%H:%M:%S")
    logger.info(f"Processing voice request at {timestamp}")
    
    # Add progress updates
    progress(0, desc="Memproses suara Anda...")
    
    try:
        sr, audio_data = audio
        
        # Log audio details for debugging
        logger.info(f"Audio sample rate: {sr}, shape: {audio_data.shape}")
        
        # Save as .wav with unique filename
        audio_filename = f"input_{int(time.time())}.wav"
        audio_path = os.path.join(tempfile.gettempdir(), audio_filename)
        
        scipy.io.wavfile.write(audio_path, sr, audio_data)
        logger.info(f"Saved input audio to: {audio_path}")
        
        if not os.path.exists(audio_path):
            logger.error(f"Failed to save audio file at {audio_path}")
            return None, history, "⚠️ Gagal menyimpan file audio"
            
        progress(0.3, desc="Mengirim ke server...")
        
        # Send to FastAPI endpoint with increased timeout
        try:
            logger.info(f"Sending request to {API_URL}")
            with open(audio_path, "rb") as f:
                files = {"file": (audio_filename, f, "audio/wav")}
                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=REQUEST_TIMEOUT
                )
            
            logger.info(f"Response status: {response.status_code}, Content length: {len(response.content) if response.content else 0}")
            
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            error_msg = "🕒 Waktu permintaan habis. Server membutuhkan waktu terlalu lama untuk merespons."
            return None, history + [[error_msg, None, timestamp]], error_msg
            
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            error_msg = "🔌 Tidak dapat terhubung ke server. Pastikan server berjalan di http://localhost:8000"
            return None, history + [[error_msg, None, timestamp]], error_msg
            
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            error_msg = f"🔴 Error: {str(e)}"
            return None, history + [[error_msg, None, timestamp]], error_msg
        
        progress(0.7, desc="Mendapatkan balasan...")
        
        if response.status_code == 200:
            logger.info("Request successful, processing response")
            
            # Verify content type and length
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"Response Content-Type: {content_type}")
            
            if not response.content:
                logger.error("Response content is empty")
                error_msg = "⚠️ Server mengembalikan respons kosong"
                return None, history + [[error_msg, None, timestamp]], error_msg
            
            # Save response audio with unique timestamp to avoid caching issues
            output_audio_path = os.path.join(tempfile.gettempdir(), f"tts_output_{int(time.time())}.wav")
            
            try:
                with open(output_audio_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Saved response audio to: {output_audio_path}")
                
                # Verify if file exists and has content
                if not os.path.exists(output_audio_path) or os.path.getsize(output_audio_path) == 0:
                    logger.error(f"Output file doesn't exist or is empty: {output_audio_path}")
                    error_msg = "⚠️ File audio respons kosong atau tidak valid"
                    return None, history + [[error_msg, None, timestamp]], error_msg
                
            except Exception as e:
                logger.error(f"Failed to save response audio: {e}")
                error_msg = f"⚠️ Gagal menyimpan file audio respons: {str(e)}"
                return None, history + [[error_msg, None, timestamp]], error_msg
            
            # Add successful interaction to history
            user_message = "🎤 Pesan Suara"
            ai_message = "🔊 Balasan Suara"
            new_history = history + [[user_message, ai_message, timestamp]]
            save_chat_history(new_history)
            
            progress(1.0, desc="Selesai!")
            return output_audio_path, new_history, "✅ Berhasil mendapatkan respons"
        else:
            logger.error(f"Server returned error status: {response.status_code}")
            try:
                error_content = response.json() if response.content else {}
                error_detail = error_content.get('message', f"Kode status: {response.status_code}")
            except:
                error_detail = f"Kode status: {response.status_code}"
                
            error_msg = f"⚠️ Server Error: {error_detail}"
            return None, history + [[error_msg, None, timestamp]], error_msg
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        error_msg = f"⚠️ Terjadi kesalahan: {str(e)}"
        return None, history + [[error_msg, None, timestamp]], error_msg

# Clear history function
def clear_history():
    if os.path.exists(HISTORY_PATH):
        os.remove(HISTORY_PATH)
    return [], "🗑️ Riwayat percakapan telah dihapus"

# Format chat history for display with improved styling
def format_chat_history(history):
    if not history:
        return "<div class='empty-history'>Belum ada percakapan. Mulai dengan merekam suara Anda.</div>"
        
    html = "<div class='chat-container'>"
    for entry in history:
        user_msg, ai_msg, timestamp = entry
        
        # User message
        html += f"""
        <div class="chat-row">
            <div class="chat-bubble user-bubble">
                <div class="chat-content">
                    <div class="chat-icon">👤</div>
                    <div class="chat-message">{user_msg}</div>
                </div>
                <div class="timestamp">{timestamp}</div>
            </div>
        </div>
        """
        
        # AI message if exists
        if ai_msg:
            html += f"""
            <div class="chat-row">
                <div class="chat-bubble assistant-bubble">
                    <div class="chat-content">
                        <div class="chat-icon">🤖</div>
                        <div class="chat-message">{ai_msg}</div>
                    </div>
                    <div class="timestamp">{timestamp}</div>
                </div>
            </div>
            """
    
    html += "</div>"
    return html

# Custom CSS with improved aesthetics and animations
custom_css = """
:root {
    --bg-primary: #1a1b26;
    --bg-secondary: #24283b;
    --bg-tertiary: #2e3347;
    --accent-blue: #7aa2f7;
    --accent-green: #9ece6a;
    --accent-purple: #bb9af7;
    --accent-orange: #ff9e64;
    --text-primary: #c0caf5;
    --text-secondary: #a9b1d6;
    --text-muted: #565f89;
    --border-color: #414868;
    --error-color: #f7768e;
    --success-color: #73daca;
    --warning-color: #e0af68;
    --shadow-color: rgba(0, 0, 0, 0.4);
}

body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto;
}

.main-header {
    text-align: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: linear-gradient(90deg, var(--bg-secondary), var(--bg-tertiary));
    border-radius: 12px;
    box-shadow: 0 4px 6px var(--shadow-color);
    border-bottom: 3px solid var(--accent-blue);
}

.title-gradient {
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: bold;
}

.subtitle {
    color: var(--text-secondary);
    font-size: 1.2rem;
    margin-top: 0.5rem;
}

.app-title-icon {
    font-size: 2.5rem;
    margin-right: 0.5rem;
    text-shadow: 0 0 10px var(--accent-blue);
}

.container {
    background-color: var(--bg-secondary);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 8px var(--shadow-color);
    border: 1px solid var(--border-color);
}

.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--accent-blue);
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 0.5rem;
}

/* Chat bubbles */
.chat-container {
    max-height: 400px;
    overflow-y: auto;
    padding-right: 0.5rem;
    scrollbar-width: thin;
    scrollbar-color: var(--border-color) var(--bg-secondary);
}

.chat-container::-webkit-scrollbar {
    width: 6px;
}

.chat-container::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

.chat-container::-webkit-scrollbar-thumb {
    background-color: var(--border-color);
    border-radius: 3px;
}

.chat-row {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}

.chat-bubble {
    border-radius: 14px;
    padding: 12px 16px;
    max-width: 95%;
    box-shadow: 0 2px 4px var(--shadow-color);
    transition: all 0.2s ease;
}

.chat-bubble:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px var(--shadow-color);
}

.user-bubble {
    background-color: var(--bg-tertiary);
    border-left: 4px solid var(--accent-blue);
    align-self: flex-end;
}

.assistant-bubble {
    background-color: var(--bg-tertiary);
    border-left: 4px solid var(--accent-green);
    align-self: flex-start;
}

.chat-content {
    display: flex;
    align-items: flex-start;
}

.chat-icon {
    margin-right: 8px;
    font-size: 1.2rem;
}

.chat-message {
    word-break: break-word;
}

.timestamp {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-align: right;
    margin-top: 4px;
}

.empty-history {
    text-align: center;
    color: var(--text-muted);
    padding: 2rem;
    font-style: italic;
}

/* Recording animations */
.recording-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    margin: 10px 0;
    border-radius: 8px;
    background-color: var(--bg-tertiary);
}

.pulse-recording {
    display: flex;
    align-items: center;
    animation: pulse 1.5s infinite;
    color: var(--error-color);
}

.record-icon {
    margin-right: 8px;
    font-size: 1.2rem;
}

@keyframes pulse {
    0% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
    100% {
        opacity: 1;
    }
}

/* Button styles */
.action-btn {
    transition: all 0.2s ease;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 4px var(--shadow-color) !important;
}

.action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px var(--shadow-color) !important;
}

.send-btn {
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple)) !important;
    color: white !important;
}

.clear-btn {
    background-color: var(--bg-tertiary) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-color) !important;
}

/* Status message */
.status-message {
    margin-top: 0.5rem;
    padding: 0.5rem;
    border-radius: 8px;
    text-align: center;
    font-size: 0.9rem;
}

.status-error {
    background-color: rgba(247, 118, 142, 0.2);
    color: var(--error-color);
}

.status-success {
    background-color: rgba(115, 218, 202, 0.2);
    color: var(--success-color);
}

.status-warning {
    background-color: rgba(224, 175, 104, 0.2);
    color: var(--warning-color);
}

/* Footer */
.footer {
    text-align: center;
    margin-top: 2rem;
    padding: 1rem;
    font-size: 0.9rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border-color);
}

/* Responsive audio input */
.audio-recorder {
    border: 2px solid var(--border-color) !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}

.audio-recorder:hover, .audio-recorder:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 2px rgba(122, 162, 247, 0.2) !important;
}

/* Audio player */
.audio-player {
    background-color: var(--bg-tertiary) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border-color) !important;
    margin-top: 1rem !important;
}

/* Animation for new messages */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.chat-row {
    animation: fadeIn 0.3s ease-out;
}

/* Custom styles for better audio visualization */
.audio-waveform {
    background-color: var(--bg-tertiary) !important;
    border-radius: 8px !important;
    padding: 10px !important;
}

.waveform-container .waveform {
    background-color: rgba(122, 162, 247, 0.2) !important;
}
"""

# Create a custom theme
theme = gr.themes.Base().set(
    body_background_fill="#1a1b26",
    body_text_color="#c0caf5",
    block_background_fill="#24283b",
    block_border_color="#414868",
    input_background_fill="#2e3347",
    button_primary_background_fill="#7aa2f7",
    button_primary_background_fill_hover="#bb9af7",
    button_primary_text_color="#1a1b26"
)

# Custom voice recording indicator
def recording_state(recording=False):
    if recording:
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)

# UI with Gradio Blocks
with gr.Blocks(theme=theme, css=custom_css) as demo:
    # Initialize state
    history_state = gr.State(load_chat_history())
    
    # Header with animated logo
    gr.HTML("""
    <style>
        .main-header {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-top: 40px;
        }

        .app-title-icon {
            font-size: 48px;
            display: block;
            margin-bottom: 10px;
        }

        .title-gradient {
            font-size: 32px;
            font-weight: bold;
            background: linear-gradient(to right, #ff5f6d, #ffc371);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            margin-top: 10px;
            font-size: 18px;
            color: #555;
        }
    </style>

    <div class="main-header">
        <h1>
            <span class="app-title-icon">🎙️</span>
            <span class="title-gradient">Voice Chatbot AI</span>
        </h1>
        <div class="subtitle">Asisten Suara Pintar Berbahasa Indonesia</div>
    </div>
    """)
    
    # Main content area
    with gr.Row(equal_height=True):
        # Left column for input and controls
        with gr.Column(scale=1, elem_classes="container"):
            gr.Markdown('<div class="section-title">🎤 Rekam Pertanyaan Anda</div>')
            
            # Recording indicators
            with gr.Group(elem_classes="recording-indicator"):
                ready_indicator = gr.HTML("""
                <div>
                    <span class="record-icon">⚪</span> Siap merekam
                </div>
                """, visible=True)
                
                recording_active = gr.HTML("""
                <div class="pulse-recording">
                    <span class="record-icon">🔴</span> Sedang merekam...
                </div>
                """, visible=False)
            
            # Audio input with microphone
            audio_input = gr.Audio(
                sources="microphone",
                type="numpy",
                elem_id="voice-input",
                elem_classes="audio-recorder",
                streaming=False
            )
            
            # Status message display
            status_msg = gr.HTML(
                """<div class="status-message">Siap menerima pertanyaan</div>""",
                elem_classes="status-area"
            )
            
            # Button for submission
            with gr.Row():
                clear_btn = gr.Button(
                    "🗑️ Hapus Riwayat", 
                    variant="secondary",
                    elem_classes="action-btn clear-btn"
                )
                submit_btn = gr.Button(
                    "🚀 Kirim", 
                    variant="primary",
                    elem_classes="action-btn send-btn"
                )
        
        # Right column for output and chat history
        with gr.Column(scale=1):
            # Audio output box
            with gr.Group(elem_classes="container"):
                gr.Markdown('<div class="section-title">🔊 Balasan dari Asisten</div>')
                
                # Audio output
                audio_output = gr.Audio(
                    type="filepath",
                    elem_id="voice-output",
                    elem_classes="audio-player",
                    show_label=False
                )
            
            # Chat history display
            with gr.Group(elem_classes="container"):
                gr.Markdown('<div class="section-title">💬 Riwayat Percakapan</div>')
                chat_display = gr.HTML(elem_classes="chat-history")
    
    # Footer
    gr.HTML("""
    <div class="footer">
        <p>Voice Chatbot menggunakan API Speech-to-Text, LLM, dan Text-to-Speech</p>
        <p>© 2025 - Dibuat dengan ❤️ menggunakan Gradio dan FastAPI</p>
    </div>
    """)
    
    # Define event handlers
    def update_status(message, is_error=False, is_warning=False):
        if is_error:
            return f'<div class="status-message status-error">{message}</div>'
        elif is_warning:
            return f'<div class="status-message status-warning">{message}</div>'
        else:
            return f'<div class="status-message status-success">{message}</div>'
    
    # Recording start event
    audio_input.start_recording(
        fn=lambda: recording_state(True),
        outputs=[recording_active, ready_indicator]
    )
    
    # Recording stop event
    audio_input.stop_recording(
        fn=lambda: recording_state(False),
        outputs=[recording_active, ready_indicator]
    )
    
    # Submit button click
    submit_btn.click(
        fn=voice_chat,
        inputs=[audio_input, history_state],
        outputs=[audio_output, history_state, status_msg]
    ).then(
        fn=format_chat_history,
        inputs=[history_state],
        outputs=[chat_display]
    )
    
    # Clear history button
    clear_btn.click(
        fn=clear_history,
        outputs=[history_state, status_msg]
    ).then(
        fn=format_chat_history,
        inputs=[history_state],
        outputs=[chat_display]
    )
    
    # Load history on start
    demo.load(
        fn=format_chat_history,
        inputs=[history_state],
        outputs=[chat_display]
    )

# Launch the app
if __name__ == "__main__":
    logger.info("Starting Voice Chatbot Frontend")
    demo.launch()