#!/usr/bin/env python3
"""指定した日の Claude Code と Codex の会話 (発言と返答の文だけ) を、セッションごとのテキストに書き出す。

使い方: extract_logs.py [today | yesterday | YYYY-MM-DD] [出力先ディレクトリ]
1日は朝5時から翌朝5時まで (この PC のタイムゾーン)。ツールの実行結果と、会話を圧縮したときの要約は含めない。
"""
import datetime as dt
import glob
import json
import os
import sys
import tempfile

DAY_START = 5
SKIP_PREFIX = ('<command-', '<local-command', '<task-notification', '<system-reminder', '<artifact-content',
               'This session is being continued')


def day_range(arg):
    now = dt.datetime.now().astimezone()
    base = (now - dt.timedelta(hours=DAY_START)).date()
    if arg in (None, 'today'):
        day = base
    elif arg == 'yesterday':
        day = base - dt.timedelta(days=1)
    else:
        day = dt.date.fromisoformat(arg)
    lo = dt.datetime.combine(day, dt.time(DAY_START)).astimezone()
    return day, lo, lo + dt.timedelta(days=1)


def local(ts):
    return dt.datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone()


def text_of(content):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ''
    return '\n'.join(x.get('text', '') for x in content
                     if isinstance(x, dict) and x.get('type') in ('text', 'Text', 'input_text', 'output_text'))


def claude_sessions(lo, hi):
    for path in glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl')):
        if os.path.getmtime(path) < lo.timestamp():
            continue
        cwd, lines = None, []
        with open(path, encoding='utf-8', errors='replace') as f:
            for raw in f:
                try:
                    d = json.loads(raw)
                except ValueError:
                    continue
                cwd = cwd or d.get('cwd')
                if d.get('type') not in ('user', 'assistant') or d.get('isSidechain') or d.get('isMeta') or d.get('isCompactSummary'):
                    continue
                if not d.get('timestamp'):
                    continue
                t = local(d['timestamp'])
                if not lo <= t < hi:
                    continue
                s = text_of((d.get('message') or {}).get('content')).strip()
                if not s or s.startswith(SKIP_PREFIX):
                    continue
                lines.append((t, 'USER' if d['type'] == 'user' else 'CLAUDE', s))
        if lines:
            yield 'claude', os.path.basename(path)[:8], cwd, lines


def codex_sessions(lo, hi):
    for path in glob.glob(os.path.expanduser('~/.codex/sessions/*/*/*/*.jsonl')):
        if os.path.getmtime(path) < lo.timestamp():
            continue
        cwd, lines = None, []
        with open(path, encoding='utf-8', errors='replace') as f:
            for raw in f:
                if '"session_meta"' not in raw and '"item_completed"' not in raw:
                    continue
                try:
                    d = json.loads(raw)
                except ValueError:
                    continue
                p = d.get('payload') or {}
                if d.get('type') == 'session_meta':
                    cwd = p.get('cwd')
                    continue
                item = (p.get('item') or {}) if p.get('type') == 'item_completed' else {}
                role = {'UserMessage': 'USER', 'AgentMessage': 'CODEX'}.get(item.get('type'))
                if not role or not d.get('timestamp'):
                    continue
                t = local(d['timestamp'])
                s = text_of(item.get('content')).strip()
                if lo <= t < hi and s:
                    lines.append((t, role, s))
        if lines:
            yield 'codex', os.path.basename(path)[-14:-6], cwd, lines


def main():
    day, lo, hi = day_range(sys.argv[1] if len(sys.argv) > 1 else None)
    out = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp(prefix=f'diary-{day}-')
    os.makedirs(out, exist_ok=True)
    print(f'{day} ({lo:%m/%d %H:%M} - {hi:%m/%d %H:%M})  出力先: {out}')
    rows = []
    for tool, sid, cwd, lines in [*claude_sessions(lo, hi), *codex_sessions(lo, hi)]:
        lines.sort(key=lambda x: x[0])
        name = f'{lines[0][0]:%H%M}_{tool}_{sid}.txt'
        body = '\n\n'.join(f'[{t:%H:%M}] {who}: {s}' for t, who, s in lines)
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            f.write(f'cwd: {cwd}\n\n{body}\n')
        rows.append((lines[0][0], lines[-1][0], name, len(lines), len(body), cwd))
    if not rows:
        print('この日の会話はない')
        return
    rows.sort()
    for a, b, name, n, size, cwd in rows:
        print(f'{a:%H:%M}-{b:%H:%M}  {name}  {n}件 {size}字  {cwd}')
    print(f'{len(rows)}セッション、合計 {sum(r[4] for r in rows)}字')


if __name__ == '__main__':
    main()
