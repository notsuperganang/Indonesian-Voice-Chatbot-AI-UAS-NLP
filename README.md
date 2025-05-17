# 🎙️ Indonesian Voice Chatbot AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

<img src="https://user-images.githubusercontent.com/74038190/238353480-219bcc70-f5dc-466b-9a60-29653d8e8433.gif" alt="Chatbot" width="200">

**Asisten Suara Pintar Berbahasa Indonesia**

*Proyek Ujian Akhir Semester - Mata Kuliah Pemrosesan Bahasa Alami*  
*Program Studi Informatika - Universitas Syiah Kuala*

</div>

## 📑 Daftar Isi
- [🌟 Fitur Utama](#-fitur-utama)
- [🛠️ Teknologi yang Digunakan](#️-teknologi-yang-digunakan)
- [🚀 Cara Menggunakan](#-cara-menggunakan)
- [📋 Prasyarat](#-prasyarat)
- [⚙️ Instalasi](#️-instalasi)
- [🏗️ Struktur Proyek](#️-struktur-proyek)
- [👨‍💻 Tim Pengembang](#-tim-pengembang)
- [🙏 Ucapan Terima Kasih](#-ucapan-terima-kasih)
- [📄 Lisensi](#-lisensi)

## 🌟 Fitur Utama

- 🎤 Merekam suara pengguna melalui antarmuka web yang intuitif
- 🧠 Mengkonversi suara menjadi teks menggunakan Whisper.cpp
- 💬 Memproses teks dan menghasilkan respons menggunakan Gemini API
- 🔊 Mengkonversi respons kembali menjadi suara dengan Coqui TTS dalam bahasa Indonesia
- 📱 Antarmuka pengguna yang responsif dan menarik dengan Gradio
- 🔄 Menyimpan riwayat percakapan untuk interaksi yang berkelanjutan

## 🛠️ Teknologi yang Digunakan

Proyek ini mengintegrasikan beberapa teknologi mutakhir dalam bidang pemrosesan bahasa alami:

- **Speech-to-Text (STT):** [Whisper.cpp](https://github.com/ggml-org/whisper.cpp) - Implementasi C++ dari model Whisper OpenAI untuk transkripsi audio yang cepat dan akurat
- **Natural Language Processing:** [Gemini API](https://ai.google.dev/) - Model bahasa generatif dari Google untuk pemahaman dan pengolahan teks
- **Text-to-Speech (TTS):** [Indonesian TTS](https://github.com/Wikidepia/indonesian-tts) - Model Coqui TTS yang dioptimalkan untuk bahasa Indonesia
- **Backend API:** [FastAPI](https://fastapi.tiangolo.com/) - Framework API yang modern dan berkinerja tinggi
- **Frontend UI:** [Gradio](https://www.gradio.app/) - Library untuk membuat antarmuka web yang interaktif untuk model ML

## 🚀 Cara Menggunakan

1. Buka aplikasi web Gradio
2. Klik tombol mikrofon untuk merekam pertanyaan Anda dalam bahasa Indonesia
3. Tunggu sistem memproses input suara Anda
4. Dengarkan respons audio dari asisten virtual
5. Riwayat percakapan akan tersimpan untuk referensi

## 📋 Prasyarat

- Python 3.9 atau lebih baru
- Pip (Package Installer for Python)
- Git
- CMake (untuk kompilasi Whisper.cpp)
- C++ Compiler (seperti GCC atau Visual Studio Build Tools)
- API Key Google Gemini

## ⚙️ Instalasi

> **Catatan Penting:** Repository ini tidak menyertakan folder `whisper.cpp`, `coqui_utils`, dan file `.env` karena ukurannya yang besar dan alasan keamanan. Anda perlu mengunduh dan mengonfigurasi komponen-komponen ini secara terpisah.

### 1. Clone Repository

```bash
git clone https://github.com/notsuperganang/Indonesian-Voice-Chatbot-AI-UAS-NLP.git
cd Indonesian-Voice-Chatbot-AI-UAS-NLP
```

### 2. Siapkan Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Untuk Linux/macOS
# atau
venv\Scripts\activate  # Untuk Windows
```

### 3. Instal Dependensi

```bash
pip install -r requirements.txt
```

### 4. Siapkan Whisper.cpp

```bash
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp

# Kompilasi Whisper.cpp
make

# Unduh model bahasa (ggml-large-v3-turbo.bin direkomendasikan)
bash ./models/download-ggml-model.sh large-v3-turbo

# Kembali ke direktori proyek utama
cd ..
```

### 5. Siapkan Coqui TTS (Model Bahasa Indonesia)

```bash
# Buat direktori untuk model TTS
mkdir -p coqui_utils

# Unduh model TTS Indonesia terbaru
# Dari https://github.com/Wikidepia/indonesian-tts/releases
# Versi terbaru saat ini: v1.2 (Aug 12, 2022)
```

Setelah mengunduh, ekstrak dan salin file-file berikut ke dalam folder `coqui_utils`:
- `checkpoint_1260000-inference.pth`
- `config.json`
- `speakers.pth`
- File model lainnya yang diperlukan

### 6. Konfigurasi Gemini API

1. Dapatkan API key dari [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Buat file `.env` di root direktori proyek:

```
GEMINI_API_KEY=your_api_key_here
```

## 🏗️ Struktur Proyek

```
📁 Indonesian-Voice-Chatbot-AI-UAS-NLP/
├── 📁 app/
│   ├── 📁 coqui_utils/              # ⚠️ Tidak di-push ke repo (harus dikonfigurasi)
│   ├── 📁 whisper.cpp/              # ⚠️ Tidak di-push ke repo (harus dikonfigurasi)
│   ├── 📄 chat_history.json         # Riwayat chat yang disimpan
│   ├── 📄 llm.py                    # Modul komunikasi dengan Gemini API
│   ├── 📄 main.py                   # Aplikasi utama FastAPI
│   ├── 📄 stt.py                    # Modul Speech-to-Text (Whisper)
│   └── 📄 tts.py                    # Modul Text-to-Speech (Coqui)
├── 📁 gradio_app/
│   └── 📄 app.py                    # Antarmuka Gradio
├── 📄 .env                          # ⚠️ Tidak di-push ke repo (konfigurasi API keys)
├── 📄 .gitignore                    # Daftar file yang tidak di-push ke repo
├── 📄 README.md                     # Dokumentasi proyek
└── 📄 requirements.txt              # Dependensi proyek
```

## 👨‍💻 Tim Pengembang

**Mahasiswa:**
- [Ganang Setyo Hadi](https://github.com/notsuperganang)

**Asisten Laboratorium:**
- [Furqan Al Ghifari Zulva](https://www.linkedin.com/in/furqan-al-ghifari-zulva/)
- [Diky Wahyudi](https://www.linkedin.com/in/dikywahyudi2002/)

## 🙏 Ucapan Terima Kasih

- [Wikidepia](https://github.com/Wikidepia) untuk [Indonesian TTS model](https://github.com/Wikidepia/indonesian-tts)
- [GGML.org](https://github.com/ggml-org) untuk [Whisper.cpp](https://github.com/ggml-org/whisper.cpp)
- Dosen dan asisten laboratorium mata kuliah Pemrosesan Bahasa Alami, Program Studi Informatika USK

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

---

<div align="center">
  <p>Dibuat dengan ❤️ untuk Ujian Akhir Semester - Pemrosesan Bahasa Alami</p>
  <p>Program Studi Informatika - Universitas Syiah Kuala</p>
</div>