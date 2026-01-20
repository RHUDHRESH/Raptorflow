import os

file_path = "conductor/tracks.md"
with open(file_path, "rb") as f:
    raw = f.read()

# Try to decode from UTF-16 LE first if it seems to be that
try:
    content = raw.decode("utf-16-le")
except UnicodeDecodeError:
    # If not, maybe it's mixed or already partially UTF-8 but with null bytes
    content = raw.replace(b"\x00", b"").decode("utf-8", errors="ignore")

# Clean up any remaining nulls if decoded from utf-16 but still has some junk
content = content.replace("\x00", "")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Cleaned and converted to UTF-8")
