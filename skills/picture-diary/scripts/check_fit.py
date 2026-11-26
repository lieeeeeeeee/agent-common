#!/usr/bin/env python3
"""日記の段落が、絵日記のマス (15マス × 20列) に収まるかを数える。

使い方: check_fit.py 段落1 段落2 ...
段落の頭は1マスあける。列の終わりに来た「。、」』」は、前のマスにぶら下げる (assets/template.html と同じ数え方)。
"""
import sys

ROWS, COLS = 15, 20
HANG = set('。、」』')


def columns(paras):
    used = 0
    for p in paras:
        row, n = 1, 1
        for ch in p:
            if row == ROWS:
                if ch in HANG:
                    continue
                n, row = n + 1, 0
            row += 1
        used += n
    return used


def main():
    paras = [p for p in sys.argv[1:] if p.strip()]
    if not paras:
        sys.exit(__doc__)
    used = columns(paras)
    print(f'{sum(map(len, paras))}字、{used} / {COLS} 列')
    if used > COLS:
        print(f'{used - COLS} 列はみ出している')
        sys.exit(1)


if __name__ == '__main__':
    main()
