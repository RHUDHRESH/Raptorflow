with open("conductor/tracks.md", "rb") as f:
    content = f.read()
    print(content[-500:])  # Just the last part where our track is
