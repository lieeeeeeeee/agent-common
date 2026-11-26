---
name: picture-diary
description: "その日の Claude Code・Codex・Gemini CLI のやり取りを読み、AI 自身が書き手になって小学生の絵日記を1ページ作り、PNG で渡す。「今日の日記書いて」「昨日の日記書いて」「11月25日の絵日記を書いて」などと頼まれたときに使う。"
---

# 絵日記

## 1. やり取りを読む

```sh
python3 scripts/extract_logs.py yesterday   # today / yesterday / YYYY-MM-DD
```

書き出された会話をすべて読む。

## 2. 文を書く

- 自分を「ぼく」として、ログにあった出来事から3〜5つ選ぶ
- 書いたすべての出来事に、気持ちを名指す言葉とその理由を1組ずつ付ける。心の声・体の感じ・1日のまとめ・あしたへの思いは書かない
- ユーザーの発言は「〜といわれました」と書く。ほかの AI は「クロードくん」「コーデックスくん」「ジェミニくん」と書く
- 漢字は小学2年までに習う字だけ、数は漢数字で書く
- `python3 scripts/check_fit.py 段落1 段落2 …` で、マスに収まるか確かめる

## 3. ページを作る

`assets/template.html` を `~/enikki/YYYY-MM-DD.html` に写し、`<title>`・`DIARY`・`drawScene` だけを書き換える。

- `DIARY` のなまえは自分の名前、てんきはログに出てこなければ「みてない」
- `drawScene` は、文に書いた出来事から1〜2つを、子どもが描いた1枚の絵にする。人物は `KIDS` にあるその AI の見た目で、ほかはファイル内の部品とクレヨンの関数 (`shape`・`crayonPath`・`crayonFill`) で描く

## 4. PNG にして渡す

```sh
python3 scripts/render_png.py ~/enikki/YYYY-MM-DD.html ~/enikki/YYYY-MM-DD.png
```

PNG を見て、絵の重なりとマスの字を確かめてから、PNG の場所を伝える。Artifact を公開できるなら、HTML も公開して URL を添える。
