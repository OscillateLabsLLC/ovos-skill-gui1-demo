"""Images built in memory and delivered as ``data:`` URIs (OVOS-GUI-1 3.5: never a filesystem path)."""

import base64
import struct
import zlib

Color = tuple[int, int, int]

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_COLOR_TYPE_RGB = 2
STRIPE_WIDTH = 6
GIF_MIN_CODE_SIZE = 2
GIF_CLEAR_CODE = 4
GIF_END_CODE = 5
GIF_CODE_BITS = 3
GIF_PIXELS_PER_CLEAR = 2
GIF_SUB_BLOCK = 255
GIF_FRAME_DELAY_CS = 40


def _data_uri(mime: str, payload: bytes) -> str:
    return f"data:{mime};base64,{base64.b64encode(payload).decode('ascii')}"


def _png_chunk(kind: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))


def _striped_rows(size: int, base: Color, accent: Color) -> bytes:
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            rows.extend(accent if ((x + y) // STRIPE_WIDTH) % 2 else base)
    return bytes(rows)


def png(base: Color, accent: Color, size: int = 48) -> str:
    """A square PNG with diagonal stripes of two colours."""
    header = struct.pack(">IIBBBBB", size, size, 8, PNG_COLOR_TYPE_RGB, 0, 0, 0)
    body = zlib.compress(_striped_rows(size, base, accent))
    payload = PNG_SIGNATURE + _png_chunk(b"IHDR", header) + _png_chunk(b"IDAT", body) + _png_chunk(b"IEND", b"")
    return _data_uri("image/png", payload)


def _lzw_uncompressed(indices: list[int]) -> bytes:
    """LZW stream that resets the table every two pixels, so every code stays three bits wide."""
    codes = []
    for start in range(0, len(indices), GIF_PIXELS_PER_CLEAR):
        codes.append(GIF_CLEAR_CODE)
        codes.extend(indices[start : start + GIF_PIXELS_PER_CLEAR])
    codes.append(GIF_END_CODE)
    out, buffer, bits = bytearray(), 0, 0
    for code in codes:
        buffer |= code << bits
        bits += GIF_CODE_BITS
        while bits >= 8:
            out.append(buffer & 0xFF)
            buffer >>= 8
            bits -= 8
    if bits:
        out.append(buffer & 0xFF)
    return bytes(out)


def _sub_blocks(data: bytes) -> bytes:
    blocks = b"".join(
        bytes([len(data[i : i + GIF_SUB_BLOCK])]) + data[i : i + GIF_SUB_BLOCK] for i in range(0, len(data), GIF_SUB_BLOCK)
    )
    return blocks + b"\x00"


def _gif_frame(size: int, phase: int) -> bytes:
    indices = [((x // STRIPE_WIDTH + y // STRIPE_WIDTH + phase) % 2) for y in range(size) for x in range(size)]
    control = b"\x21\xf9\x04\x04" + struct.pack("<H", GIF_FRAME_DELAY_CS) + b"\x00\x00"
    descriptor = b"\x2c" + struct.pack("<HHHHB", 0, 0, size, size, 0)
    return control + descriptor + bytes([GIF_MIN_CODE_SIZE]) + _sub_blocks(_lzw_uncompressed(indices))


def animated_gif(first: Color, second: Color, size: int = 48, frames: int = 2) -> str:
    """A looping GIF whose checkerboard swaps colours on every frame."""
    palette = bytes(first) + bytes(second) + bytes(first) + bytes(second)
    screen = struct.pack("<HHBBB", size, size, 0xF1, 0, 0)
    loop = b"\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00"
    body = b"".join(_gif_frame(size, phase) for phase in range(frames))
    return _data_uri("image/gif", b"GIF89a" + screen + palette + loop + body + b"\x3b")
