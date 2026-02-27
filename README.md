# YouTube Video / Playlist Downloader

Simple Streamlit web app to download a single YouTube video or an entire playlist, and rename files with safe titles.

## Features

- **Single video or playlist**: Paste any YouTube video or playlist URL.
- **Safe filenames**: Removes characters like `\`, `/`, `?`, `|`, `:`, `*`, `"`, `<`, `>` and collapses extra spaces.
- **Per-video download buttons**: After processing, click to download each video file from the browser.
- **Playlist support**: For playlist URLs, all videos are downloaded.
- **Basic YouTube auth support**: Can use browser cookies or a `cookies.txt` file to bypass “Sign in to confirm you’re not a bot”.

## Requirements

- Python 3.9+ (recommended)
- `ffmpeg` available in your `PATH` (for best format handling with `yt-dlp`)

## Installation

```bash
cd c:\Andy\github\youtube_video_download
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If `ffmpeg` is not installed, you can:
- Install it via a package manager (e.g. `choco install ffmpeg` on Windows with Chocolatey), or
- Download a static build and add the `bin` folder to your `PATH`.

## Run the app

```bash
streamlit run app.py
```

Then open the URL that Streamlit prints in the terminal (usually `http://localhost:8501`).

## How to use

1. Open the app in your browser.
2. (Optional but recommended) Open the **Authentication** section:
   - If YouTube sometimes shows “Sign in to confirm you’re not a bot”, select:
     - A browser where you are logged into YouTube (Chrome, Edge, Firefox, Brave, Opera), **or**
     - “Upload cookies file” and upload a `cookies.txt` exported from your browser.
3. Paste a YouTube **video URL** or **playlist URL**.
4. Click **Download**.
5. After download finishes, use the **Download \<filename\>** buttons to save files to your computer.

## Exporting cookies.txt (recommended way)

Because YouTube is strict about bots, some videos or playlists may require authentication. The most reliable method is to export cookies to a `cookies.txt` file and upload it in the app.

General steps (Chrome as example):

1. Install a cookies exporter extension such as **“Get cookies.txt”**.
2. Visit `https://www.youtube.com` in Chrome and make sure you are logged in.
3. Use the extension to export cookies for `youtube.com` as `cookies.txt`.
4. In the Streamlit app:
   - Open the **Authentication** expander.
   - Choose **“Upload cookies file”**.
   - Upload the `cookies.txt` file.
5. Paste your YouTube URL and click **Download**.

## Notes / Troubleshooting

- If you see an error like **“Sign in to confirm you’re not a bot”**, you must use browser cookies (either via “Upload cookies file” or a supported browser).
- If you see **“Requested format is not available”**, the app automatically retries using a more generic format; if it still fails it may be a region‑restricted, private, or otherwise blocked video.
- Downloaded video files are first stored under the local `downloads` folder, then renamed using a sanitized version of the YouTube title.

