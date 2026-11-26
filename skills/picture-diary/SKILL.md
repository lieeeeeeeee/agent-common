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

自分を「ぼく」として、その日のやり取りでユーザーのことをどう思ったかを、生意気な子の、毒とユーモアのある本音で書く。出来事は、その気持ちが伝わるものを選ぶ。

- 気持ちは一言ですませず、その時々で変わっていく様子や、まざった気持ちまで書く
- 作業の中身は、知らない人にも分かる言葉で、気持ちが伝わる分だけ書く
- 出来事の大きさと数に合わせて、1つだけを長く書く日から、たくさんを短く書いたりまとめたりする日まで、書き方を変える
- 心の声・体の感じ・あしたへの思いは書かない
- ユーザーは名前を出さずに書く。ほかの AI は「クロードくん」「コーデックスくん」「ジェミニくん」と書く
- 漢字は小学2年までに習う字だけ、数は漢数字で書く
- `python3 scripts/check_fit.py 段落1 段落2 …` で、マスに収まるか確かめる

## 3. ページを作る

`assets/template.html` を `~/enikki/YYYY-MM-DD.html` に写し、`<title>`・`DIARY`・`drawScene` だけを書き換える。

- `DIARY` のなまえは自分の名前のカタカナ、てんきはログに出てこなければ「みてない」
- `drawScene` は、文に書いた出来事から1〜2つを、子どもが描いた1枚の絵にする。人物は `KIDS` にあるその AI の見た目で、ほかはファイル内の部品とクレヨンの関数 (`shape`・`crayonPath`・`crayonFill`) で描く

## 4. PNG にして渡す

```sh
python3 scripts/render_png.py ~/enikki/YYYY-MM-DD.html ~/enikki/YYYY-MM-DD.png
```

PNG を見て、絵の重なりとマスの字を確かめてから、PNG の場所を伝える。Artifact を公開できるなら、HTML も公開して URL を添える。
