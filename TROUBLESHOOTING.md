# Troubleshooting Stream Downloader

This document provides solutions to common issues encountered when using Stream Downloader.

## Twitch Stream Download Issues

### Automatic Streamlink Usage for Twitch

Stream Downloader now automatically uses Streamlink for Twitch streams, which provides better download performance and reliability for Twitch content. When downloading Twitch streams, the application will automatically switch to using Streamlink instead of yt-dlp.

### Error: "No formats that can be downloaded from the start"

When trying to download a Twitch stream, you might encounter this error:

```
ERROR: [twitch:stream] 123456789: --live-from-start is passed, but there are no formats that can be downloaded from the start. If you want to download from the current time, use --no-live-from-start
```

**Solution:**
1. In the Stream Downloader GUI, uncheck the "Live from start" option in the download options.
2. Try downloading again.

This happens because some Twitch streams don't support downloading from the beginning, only from the current time. By disabling the "Live from start" option, you can still download the stream from the current point onward.

### CLI Users
If you're using the CLI version, add the `--no-live-from-start` flag to your command:

```
python stream-dl.py download https://www.twitch.tv/channelname --no-live-from-start
```

Or in PowerShell:

```powershell
.\stream-dl.py download https://www.twitch.tv/channelname --no-live-from-start
```

If you're running the application in interactive mode, when prompted "Download from live stream start (if available)?", answer "No".

## YouTube Stream Issues

### Failed to Download Members-Only Content

If you're trying to download members-only YouTube content, make sure to:

1. Export cookies from your browser where you're logged in to YouTube
2. In the Stream Downloader GUI, click "Browse..." next to the "Cookies file" field and select your cookies file
3. Try downloading again

## General Issues

### FFmpeg Not Found

If you encounter errors related to FFmpeg:

1. Make sure FFmpeg is installed on your system
2. In the Settings tab, specify the full path to your FFmpeg executable
3. Save settings and try downloading again

### Download Starts But Fails or Freezes

1. Check your internet connection
2. Try a different quality setting (lower quality may be more stable)
3. For Twitch streams, try with "Live from start" both enabled and disabled
4. Check if you have enough free disk space

## Still Having Issues?

Please [open an issue](https://github.com/yourusername/stream-downloader/issues) with the following information:
- Full error message or screenshot
- Platform you're downloading from (Twitch/YouTube)
- URL of the stream (if public)
- Operating system and version
- Whether you're using the GUI or CLI version
