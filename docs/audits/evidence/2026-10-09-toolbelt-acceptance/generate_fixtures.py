"""Generate original, small source fixtures for disposable native acceptance."""
import math
import struct
import sys
import wave
import zlib
from pathlib import Path


def generate(destination):
    destination.mkdir(parents=True, exist_ok=True)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    pixels = b"".join(b"\0" + bytes((60, 130, 200, 255)) * 32 for _ in range(32))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 32, 32, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")
    (destination / "T_Acceptance.png").write_bytes(png)
    samples = b"".join(struct.pack("<h", int(2000 * math.sin(2 * math.pi * 440 * i / 48000))) for i in range(4800))
    with wave.open(str(destination / "SW_Acceptance.wav"), "wb") as output:
        output.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
        output.writeframes(samples)
    assert zlib.decompress(png.split(b"IDAT", 1)[1][:-16]) == pixels
    with wave.open(str(destination / "SW_Acceptance.wav"), "rb") as check:
        assert check.getparams()[:4] == (1, 2, 48000, 4800)


if __name__ == "__main__":
    generate(Path(sys.argv[1]))
