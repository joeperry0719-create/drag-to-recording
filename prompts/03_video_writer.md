# 03_video_writer.md

```text
Read AGENTS.md and models.py.

Implement screen_region_recorder/video_writer.py.

Requirements:
- Use imageio_ffmpeg.write_frames.
- Create class VideoWriter.
- Constructor takes output_path, width, height, fps, crf.
- Start the writer generator safely.
- Expose write_frame(frame) and close().
- Accept RGB uint8 numpy arrays shaped exactly (height, width, 3).
- Reject frames with wrong shape or dtype using clear exceptions.
- Ensure frame is C-contiguous before sending.
- Use pix_fmt_in="rgb24".
- Use pix_fmt_out="yuv420p".
- Prefer codec="libx264" for MP4.
- Use reasonable FFmpeg output parameters for CRF when supported by imageio-ffmpeg.
- Close the writer safely and idempotently.
- Use try/finally where appropriate.

Testing:
- Add lightweight tests where possible.
- It is acceptable to mock the imageio_ffmpeg writer if real FFmpeg video output would make tests slow or brittle.
- Do not create long video files in tests.

Run:
python -m pytest -q
python -m compileall screen_region_recorder

Return:
1. changed files
2. test result
3. VideoWriter API summary
```
