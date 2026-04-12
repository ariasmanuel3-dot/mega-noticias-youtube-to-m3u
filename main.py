import json
import pathlib
import yt_dlp

OUTPUT_DIR = pathlib.Path("out")
OUTPUT_FILE = OUTPUT_DIR / "mega_noticias.m3u"
CHANNELS_FILE = pathlib.Path("channels.json")


def extract_stream_url(url: str) -> tuple[str, str]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best[protocol*=m3u8]/best",
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get("title") or "YouTube Live"

    direct_url = info.get("url")
    if direct_url:
        return title, direct_url

    requested_formats = info.get("requested_formats") or []
    for fmt in requested_formats:
        fmt_url = fmt.get("url")
        if fmt_url:
            return title, fmt_url

    formats = info.get("formats") or []

    for fmt in reversed(formats):
        fmt_url = fmt.get("url")
        protocol = (fmt.get("protocol") or "").lower()
        if fmt_url and "m3u8" in protocol:
            return title, fmt_url

    for fmt in reversed(formats):
        fmt_url = fmt.get("url")
        if fmt_url:
            return title, fmt_url

    raise RuntimeError("Could not extract a playable stream URL")


def main() -> None:
    channels = json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    lines = ["#EXTM3U"]

    for channel in channels:
        name = channel["name"]
        source_url = channel["url"]
        group = channel.get("group", "YouTube")
        tvg_logo = channel.get("tvg_logo", "")
        tvg_id = channel.get("tvg_id", "")

        title, stream_url = extract_stream_url(source_url)

        lines.append(
            f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{tvg_logo}" group-title="{group}",{name}'
        )
        lines.append(stream_url)
        print(f"OK: {name} -> {title}")

    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Written: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
