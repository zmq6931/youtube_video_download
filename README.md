# YouTube Video / Playlist Downloader

A Streamlit web app to download a single YouTube video or an entire playlist. Files are saved with safe, sanitized titles.

## Features

- **Single video or playlist**: Paste any YouTube video or playlist URL.
- **Safe filenames**: Strips invalid characters (`\`, `/`, `?`, `|`, `:`, `*`, `"`, `<`, `>`) and collapses extra spaces.
- **Per-video download buttons**: After processing, download each file from the browser.
- **Playlist support**: Download all videos from a playlist in one go.
- **Authentication options**: Use browser cookies or a `cookies.txt` file to handle “Sign in to confirm you’re not a bot”.

## Requirements

- Python 3.9+
- **ffmpeg** in your `PATH` (for best format handling with yt-dlp)

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

For dev containers or systems that use `packages.txt`, `ffmpeg` is listed there.

## Run the app

Activate the venv, then:

```bash
streamlit run app.py
```

If `streamlit` is not on your PATH, run:

```bash
.venv\Scripts\streamlit run app.py    # Windows
.venv/bin/streamlit run app.py        # macOS / Linux
```

Or:

```bash
.venv\Scripts\python -m streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## How to use

1. Open the app in your browser.
2. (Optional) In **Authentication**:
   - Choose a browser where you’re logged into YouTube (Chrome, Edge, Firefox, Brave, Opera), **or**
   - Use **Upload cookies file** and upload a `cookies.txt` from your browser.
3. Paste a YouTube **video** or **playlist** URL.
4. Click **Download**.
5. Use the **Download \<filename\>** buttons to save files to your computer.

## Exporting cookies.txt

For videos that require login, export cookies and upload them in the app:

1. Install a cookies exporter (e.g. **Get cookies.txt** in Chrome).
2. Log in at `https://www.youtube.com` and export cookies for `youtube.com` as `cookies.txt`.
3. In the app: **Authentication** → **Upload cookies file** → select `cookies.txt`.
4. Paste your URL and click **Download**.

## Project layout

- `app.py` – Streamlit app (uses **yt-dlp** for downloads).
- `requirements.txt` – Python deps (streamlit, yt-dlp).
- `packages.txt` – System deps (e.g. ffmpeg for dev containers).
- `downloads/` – Default folder for downloaded videos (created on first run).

## Troubleshooting

- **“streamilt” / command not found**: Use **streamlit** (with a **t**). Run from the project folder with the venv activated, or use `.venv\Scripts\streamlit run app.py`.
- **“Sign in to confirm you’re not a bot”**: Use browser cookies (upload `cookies.txt` or pick a logged-in browser in Authentication).
- **“Requested format is not available”**: The app retries with other formats; persistent failures may mean the video is restricted, private, or blocked.
- Downloaded files are stored in `downloads/` and renamed using a sanitized version of the video title.
