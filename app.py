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
        # Prefer any best video+audio, merge to .mp4 (avoids "format not available" when YouTube has no mp4).
        "format": "bestvideo+bestaudio/best[ext=mp4]/best",
        "merge_output_format": "mp4",
    }

    if cookiefile and Path(cookiefile).exists():
        ydl_opts["cookiefile"] = str(cookiefile)
    elif browser:
        ydl_opts["cookiesfrombrowser"] = (browser.lower(),)

    # When using cookies, try Android client first (often avoids 403), then web.
    if cookiefile or browser:
        ydl_opts["extractor_args"] = {"youtube": {"player_client": ["android", "web"]}}

    files: List[Path] = []

    def _do_download(opts: dict):
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=True)

    try:
        info = _do_download(ydl_opts)
    except Exception as e:
        err_msg = str(e)
        # 403 Forbidden: try Android-only client (often works when web + cookies fail).
        if (cookiefile or browser) and ("403" in err_msg or "Forbidden" in err_msg):
            try:
                retry_opts = dict(ydl_opts)
                retry_opts["extractor_args"] = {"youtube": {"player_client": ["android"]}}
                info = _do_download(retry_opts)
            except Exception:
                raise e
        # Retry with single-format (no merge) when ffmpeg is missing (e.g. on Streamlit Cloud).
        elif "ffmpeg" in err_msg or "merging of multiple formats" in err_msg:
            fallback_opts = dict(ydl_opts)
            fallback_opts["format"] = "best[ext=mp4]"
            info = _do_download(fallback_opts)
        # Requested format not available: try single mp4 then any format merged to mp4.
        elif "Requested format is not available" in err_msg:
            try:
                fallback_opts = dict(ydl_opts)
                fallback_opts["format"] = "best[ext=mp4]"
                info = _do_download(fallback_opts)
            except Exception:
                fallback_opts = dict(ydl_opts)
                fallback_opts["format"] = "bestvideo+bestaudio/best"
                info = _do_download(fallback_opts)
        else:
            raise

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

    # Step 1: Sign in to YouTube account
    st.subheader("1. Sign in to your YouTube account")
    st.caption(
        "Use a browser where you're already logged in, or upload a cookies file. "
        "This avoids \"not a bot\" and region/age limits. "
        "**On Streamlit Cloud:** only **Upload cookies file** works (browser option is for local run only)."
    )
    auth_method = st.radio(
        "Sign in with",
        ["Don't sign in", "Chrome", "Edge", "Firefox", "Brave", "Opera", "Upload cookies file"],
        horizontal=True,
        label_visibility="collapsed",
    )
    cookiefile_path: str | Path | None = None
    browser: str | None = None
    if auth_method == "Upload cookies file":
        st.caption("Export cookies (e.g. \"Get cookies.txt\" extension) from youtube.com, then upload:")
        cookie_file = st.file_uploader(
            "Upload cookies.txt",
            type=["txt"],
            label_visibility="collapsed",
        )
        if cookie_file:
            cookiefile_path = Path("downloads") / "_cookies.txt"
            ensure_download_dir()
            cookiefile_path.write_bytes(cookie_file.getvalue())
    elif auth_method != "Don't sign in":
        browser = auth_method
        st.caption(f"Using **{browser}** — make sure you're logged into YouTube there.")

    signed_in = browser is not None or cookiefile_path is not None
    if signed_in:
        st.success("Signed in. Paste a URL below and click Download.")

    st.divider()

    # Step 2: Paste URL and download
    st.subheader("2. Paste URL and download")
    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=... or playlist URL",
        label_visibility="collapsed",
    )
    download_clicked = st.button("Download", type="primary")

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
                err_msg = str(e)
                st.error(f"Download failed: {err_msg}")
                if "cookies database" in err_msg or "chrome cookies" in err_msg.lower():
                    st.info(
                        "Browser sign-in does not work on Streamlit Cloud (no browser installed). "
                        "Please use **Upload cookies file** in Step 1: export cookies from your browser, then upload here."
                    )
                elif "403" in err_msg or "Forbidden" in err_msg:
                    st.info(
                        "**403 Forbidden** often means cookies are expired or YouTube is blocking the request. Try: "
                        "(1) Re-export **cookies.txt** from your browser (visit youtube.com while logged in, then export). "
                        "(2) Export in a **private/incognito** window and upload immediately. "
                        "(3) Use a VPN or try again later if your IP was rate-limited."
                    )
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

