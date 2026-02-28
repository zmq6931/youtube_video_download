# YouTube Video / Playlist Downloader

A Streamlit web app to download a single YouTube video or an entire playlist. Upload cookies (optional), paste a URL, and download. Files are saved with safe, sanitized titles.

## Features

- **Single video or playlist**: Paste any YouTube video or playlist URL.
- **Upload cookies (optional)**: Use a `cookies.txt` file to avoid “Sign in to confirm you’re not a bot” and 403 errors.
- **Safe filenames**: Strips invalid characters (`\`, `/`, `?`, `|`, `:`, `*`, `"`, `<`, `>`) and collapses extra spaces.
- **Per-video download buttons**: After processing, download each file from the browser.
- **Playlist support**: Download all videos from a playlist in one go.
- **Format handling**: Prefers best available format (mp4 when possible); falls back automatically if a format is unavailable.

## Requirements

- Python 3.9+
- **ffmpeg** in your `PATH` (recommended for merging to mp4; optional for single-stream “best” downloads)

## Installation

```bash
cd youtube_video_download
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

**ffmpeg** (if needed):

- Windows: `choco install ffmpeg` (Chocolatey), or add a static build’s `bin` folder to `PATH`.
- macOS: `brew install ffmpeg`
- Linux: install via your package manager.

For **Streamlit Cloud**, `packages.txt` in the repo lists `ffmpeg` so the cloud environment installs it automatically.

## Run the app

Activate the venv, then:

```bash
streamlit run app.py
```

If `streamlit` is not on your PATH:

```bash
.venv\Scripts\streamlit run app.py    # Windows
.venv/bin/streamlit run app.py        # macOS / Linux
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## How to use

1. Open the app in your browser.
2. **(Optional)** In **1. Upload cookies file**: upload a `cookies.txt` (see below) if you need to sign in to YouTube. You can skip this for public videos.
3. In **2. Paste URL and download**: paste a YouTube **video** or **playlist** URL and click **Download**.
4. Use the **Download \<filename\>** buttons to save files to your computer.

## Exporting cookies.txt

When YouTube shows “Sign in to confirm you’re not a bot” or you get **403 Forbidden**, use cookies:

1. Install a cookies exporter (e.g. **Get cookies.txt** in Chrome).
2. Log in at `https://www.youtube.com` in that browser.
3. Export cookies for `youtube.com` as `cookies.txt` (Netscape format).
4. In the app: **1. Upload cookies file** → choose `cookies.txt`.
5. Paste your URL and click **Download**.

Tip: Export in a **private/incognito** window and upload soon; cookies can expire or rotate.

## Project layout

- `app.py` – Streamlit app (uses **yt-dlp** for downloads).
- `requirements.txt` – Python deps (streamlit, yt-dlp).
- `packages.txt` – System deps for Streamlit Cloud (e.g. ffmpeg).
- `downloads/` – Folder for downloaded videos (created on first run).
- `.gitignore` – Excludes `downloads/`, `.venv/`, etc.

## Deploy on Streamlit Cloud

1. Push the repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo, and deploy.
3. Only **Upload cookies file** works on the cloud (no local browser). Use `cookies.txt` as above.

## Troubleshooting

- **“streamlit” not found**: Use **streamlit** (with a **t**). Run from the project folder with the venv activated: `.venv\Scripts\streamlit run app.py` (Windows).
- **“Sign in to confirm you’re not a bot” / 403 Forbidden**: Upload a fresh `cookies.txt` (export from browser while logged in to youtube.com). On Streamlit Cloud, only the cookies file option is available.
- **“Requested format is not available”**: The app retries with other formats automatically. If it still fails, the video may be restricted, private, or region-locked.
- **“ffmpeg is not installed”**: Install ffmpeg and add it to `PATH`, or rely on the app’s “best” single-format fallback (no merge). On Streamlit Cloud, `packages.txt` should install ffmpeg.
- Downloaded files are in `downloads/` and renamed with a sanitized video title (extension may be .mp4 or .webm depending on what YouTube offers).
