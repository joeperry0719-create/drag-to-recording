import numpy as np
import pytest

from screen_region_recorder import video_writer
from screen_region_recorder.video_writer import VideoWriter, VideoWriterError


class FakeFrameWriter:
    def __init__(self) -> None:
        self.sent = []
        self.closed = False

    def send(self, frame):
        self.sent.append(frame)

    def close(self):
        self.closed = True


def test_video_writer_starts_generator_with_mp4_parameters(monkeypatch):
    fake_writer = FakeFrameWriter()
    captured = {}

    def fake_write_frames(path, size, **kwargs):
        captured["path"] = path
        captured["size"] = size
        captured["kwargs"] = kwargs
        return fake_writer

    monkeypatch.setattr(video_writer.imageio_ffmpeg, "write_frames", fake_write_frames)

    writer = VideoWriter("capture.mp4", width=100, height=50, fps=15, crf=23)

    assert fake_writer.sent == [None]
    assert captured["path"] == "capture.mp4"
    assert captured["size"] == (100, 50)
    assert captured["kwargs"]["pix_fmt_in"] == "rgb24"
    assert captured["kwargs"]["pix_fmt_out"] == "yuv420p"
    assert captured["kwargs"]["macro_block_size"] == 1
    assert "-crf" in captured["kwargs"]["output_params"]
    writer.close()
    assert fake_writer.closed


def test_write_frame_accepts_rgb_uint8_with_expected_shape(monkeypatch):
    fake_writer = FakeFrameWriter()
    monkeypatch.setattr(
        video_writer.imageio_ffmpeg,
        "write_frames",
        lambda *args, **kwargs: fake_writer,
    )
    writer = VideoWriter("capture.mp4", width=4, height=2, fps=15, crf=23)
    frame = np.zeros((2, 4, 3), dtype=np.uint8)

    writer.write_frame(frame)

    assert fake_writer.sent[-1].shape == (2, 4, 3)
    assert fake_writer.sent[-1].flags.c_contiguous
    writer.close()


def test_write_frame_rejects_wrong_shape(monkeypatch):
    fake_writer = FakeFrameWriter()
    monkeypatch.setattr(
        video_writer.imageio_ffmpeg,
        "write_frames",
        lambda *args, **kwargs: fake_writer,
    )
    writer = VideoWriter("capture.mp4", width=4, height=2, fps=15, crf=23)

    with pytest.raises(VideoWriterError, match="shape"):
        writer.write_frame(np.zeros((2, 4, 4), dtype=np.uint8))

    writer.close()


def test_write_frame_rejects_wrong_dtype(monkeypatch):
    fake_writer = FakeFrameWriter()
    monkeypatch.setattr(
        video_writer.imageio_ffmpeg,
        "write_frames",
        lambda *args, **kwargs: fake_writer,
    )
    writer = VideoWriter("capture.mp4", width=4, height=2, fps=15, crf=23)

    with pytest.raises(VideoWriterError, match="dtype"):
        writer.write_frame(np.zeros((2, 4, 3), dtype=np.float32))

    writer.close()


def test_close_is_idempotent(monkeypatch):
    fake_writer = FakeFrameWriter()
    monkeypatch.setattr(
        video_writer.imageio_ffmpeg,
        "write_frames",
        lambda *args, **kwargs: fake_writer,
    )
    writer = VideoWriter("capture.mp4", width=4, height=2, fps=15, crf=23)

    writer.close()
    writer.close()

    assert fake_writer.closed
