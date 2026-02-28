import os
import re
from pathlib import Path
from typing import List

import streamlit as st
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


INVALID_CHARS_PATTERN = r'[\\/*?:"<>|]'


def sanitize_filename(name: str, max_length: int = 150) -> str:
    """Remove characters that are not allowed in filenames on common OSes."""
    if not name:
        return "video"
    # Remove invalid characters
    cleaned = re.sub(INVALID_CHARS_PATTERN, "", name)
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Fallback if everything was removed
    if not cleaned:
        cleaned = "video"
    # Limit very long names
    return cleaned[:max_length]


def ensure_download_dir() -> Path:
    downloads = Path("downloads")
    downloads.mkdir(exist_ok=True)
    return downloads


def _rename_to_sanitized(info: dict, download_dir: Path) -> Path:
    """
    Given a yt-dlp info dict and the directory where the file was saved,
    rename id.mp4 to a sanitized title.mp4. Only .mp4 files are considered.
    """
    video_id = info.get("id")
    title = info.get("title") or video_id or "video"
    sanitized_title = sanitize_filename(title)
    final_path = download_dir / f"{sanitized_title}.mp4"

    if video_id:
        original_path = download_dir / f"{video_id}.mp4"
        if original_path.exists():
            if original_path != final_path:
                original_path.replace(final_path)
            return final_path

    return final_path


def download_videos(
    url: str,
    download_dir: Path,
    *,
    browser: str | None = None,
    cookiefile: str | Path | None = None,
) -> List[Path]:
    """
    Download a single YouTube video or a playlist.
    Returns a list of Paths to the downloaded files (renamed & sanitized).
    """
    ydl_opts = {
        # Download initially as <id>.<ext>, then we'll rename with sanitized title.
        "outtmpl": str(download_dir / "%(id)s.%(ext)s"),
        "noplaylist": False,  # let yt-dlp handle playlists too
        "quiet": True,
        "no_warnings": True,
        # Ignore any global yt-dlp.conf on the system that might request
        # an unavailable format (e.g. fixed itag like 22).
        "ignoreconfig": True,
        # Only download .mp4 (merge with ffmpeg if needed).
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "merge_output_format": "mp4",
    }

    if cookiefile and Path(cookiefile).exists():
        ydl_opts["cookiefile"] = str(cookiefile)
    elif browser:
        # Use cookies from browser to avoid "Sign in to confirm you're not a bot"
        ydl_opts["cookiesfrombrowser"] = (browser.lower(),)

    files: List[Path] = []

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except DownloadError as e:
        # Some videos/playlists fail with "Requested format is not available".
        # Retry once with a very simple, generic format selection.
        if "Requested format is not available" not in str(e):
            raise

        fallback_opts = dict(ydl_opts)
        fallback_opts["format"] = "best[ext=mp4]"  # only mp4, no other formats

        with YoutubeDL(fallback_opts) as ydl:
            info = ydl.extract_info(url, download=True)

    if "entries" in info:  # playlist or multi-video URL
        for entry in info.get("entries") or []:
            if not entry:
                continue
            final_path = _rename_to_sanitized(entry, download_dir)
            if final_path.exists():
                files.append(final_path)
    else:  # single video
        final_path = _rename_to_sanitized(info, download_dir)
        if final_path.exists():
            files.append(final_path)

    return files


def main() -> None:
    st.set_page_config(page_title="YouTube Downloader", page_icon="🎬", layout="centered")

    st.title("YouTube Video / Playlist Downloader")
    st.write(
        "Paste a **YouTube video** or **playlist** URL below. "
        "Click **Download** to fetch the video files. "
        "Filenames will be cleaned of characters that cannot be used on your system."
    )

    with st.expander("Authentication (if YouTube says \"Sign in to confirm you're not a bot\")"):
        st.caption("Use cookies from a browser where you're logged into YouTube, or upload a cookies file.")
        auth_method = st.radio(
            "Cookie source",
            ["None", "Chrome", "Edge", "Firefox", "Brave", "Opera", "Upload cookies file"],
            horizontal=True,
            label_visibility="collapsed",
        )
        cookiefile_path: str | Path | None = None
        browser: str | None = None
        if auth_method == "Upload cookies file":
            cookie_file = st.file_uploader(
                "Upload cookies.txt (Netscape format)",
                type=["txt"],
                label_visibility="collapsed",
            )
            if cookie_file:
                # Save to temp file; yt-dlp needs a path
                cookiefile_path = Path("downloads") / "_cookies.txt"
                ensure_download_dir()
                cookiefile_path.write_bytes(cookie_file.getvalue())
        elif auth_method != "None":
            browser = auth_method

    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=... or playlist URL")
    download_clicked = st.button("Download")

    if download_clicked:
        if not url.strip():
            st.error("Please enter a YouTube URL.")
            return

        download_dir = ensure_download_dir()

        with st.spinner("Downloading video(s). This may take a while..."):
            try:
                files = download_videos(
                    url.strip(),
                    download_dir,
                    browser=browser,
                    cookiefile=cookiefile_path,
                )
            except Exception as e:  # noqa: BLE001
                st.error(f"Download failed: {e}")
                return

        if not files:
            st.warning("No videos were downloaded. Please check the URL.")
            return

        st.success(f"Downloaded {len(files)} video(s).")

        st.write("Click below to download the files to your computer:")
        for path in files:
            file_name = path.name
            ext = path.suffix.lower().lstrip(".")
            # Simple MIME guess
            if ext in {"mp4", "m4v"}:
                mime = "video/mp4"
            elif ext in {"webm"}:
                mime = "video/webm"
            elif ext in {"mkv"}:
                mime = "video/x-matroska"
            else:
                mime = "application/octet-stream"

            with open(path, "rb") as f:
                st.download_button(
                    label=f"Download {file_name}",
                    data=f,
                    file_name=file_name,
                    mime=mime,
                    key=str(path),
                )


if __name__ == "__main__":
    main()

