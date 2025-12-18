from pathlib import Path

p = Path(r"c:\Users\hp\OneDrive\Desktop\Raptorflow\src\pages\app\MuseChatPage.jsx")
lines = p.read_text(encoding="utf-8").splitlines(True)

# Replace broken block lines 1361-1369 (1-based) with normalized JSX
start = 1361
end = 1369

new_block = [
    '                <div className="fixed bottom-32 left-[calc(50%)] -translate-x-1/2 z-30">\n',
    '                  <button\n',
    '                    type="button"\n',
    "                    onClick={() => scrollToBottom('smooth')}\n",
    '                    className="px-4 py-2 rounded-2xl bg-white/90 border border-paper-100 shadow-lg text-sm text-ink flex items-center gap-2 hover:bg-white transition-editorial font-medium"\n',
    '                  >\n',
    '                    <CornerDownLeft className="w-4 h-4" strokeWidth={1.5} />\n',
    '                    Jump to latest\n',
    '                  </button>\n',
    '                </div>\n',
]

lines[start - 1 : end] = new_block
p.write_text(''.join(lines), encoding="utf-8")
print('rewrote jump-to-latest block')
