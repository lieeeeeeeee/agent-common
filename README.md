# agent-common

Claude Code と Codex で使っている、日本語の Skill と共通規約です。画像生成などに使うプロンプトも置いています。

## Skill

| Skill | できること |
| --- | --- |
| [adr-writing](skills/adr-writing/SKILL.md) | 設計判断を、後から意図を読み取れる ADR にまとめる |
| [explain-before-shorten](skills/explain-before-shorten/SKILL.md) | 日本語の説明を、意味と条件を保って簡潔にする |
| [game-content-writing](skills/game-content-writing/SKILL.md) | ゲーム内の効果・能力・用語・ルールの説明文を作成・検証する |
| [goal-first-prompt-designer](skills/goal-first-prompt-designer/SKILL.md) | 目的と必須条件をすり合わせてから、AI 向けプロンプトを作る |
| [image-prompt-designer](skills/image-prompt-designer/SKILL.md) | 画像生成のプロンプトを、最小の記述から生成結果を見て1つずつ足して作る |
| [learn-from-corrections](skills/learn-from-corrections/SKILL.md) | セッションで受けた指摘から、規約に残す教訓と文案を提案する |
| [session-close](skills/session-close/SKILL.md) | 会話で確定した情報を、既存の文書や Skill へ整理する |

`session-close` は、Skill の作成・更新に skill-creator Skill を使います。

## 導入

使いたい Skill のディレクトリを、ツールごとの Skill ディレクトリへリンクします。

```sh
git clone https://github.com/lieeeeeeeee/agent-common.git
cd agent-common

# Claude Code
mkdir -p ~/.claude/skills
ln -s "$PWD/skills/adr-writing" ~/.claude/skills/adr-writing

# Codex
mkdir -p ~/.codex/skills
ln -s "$PWD/skills/adr-writing" ~/.codex/skills/adr-writing
```

## common.md

作者が全プロジェクトで使っている、AI 向けの規約です。

`~/.claude/CLAUDE.md` や `~/.codex/AGENTS.md` へそのまま置くと既存の設定を置き換えるため、必要な章だけ取り入れてください。第 8 章は作者の好みの口調、第 9 章は作者の環境のファイル配置です。

## プロンプト

| プロンプト | できること |
| --- | --- |
| [illustration](prompts/illustration/) | 画像生成のプロンプトに追加し、AI らしさを抑える |
| [illustration-local-model](prompts/illustration-local-model/) | 画像生成のプロンプトに追加し、AI らしさを抑えたうえで、ローカルモデル風の今どきの絵柄にする |
| [background-grainy-glow](prompts/background-grainy-glow/) | 場所・雰囲気・色を指定するプロンプトに追加し、ざらついた筆致で暗がりに光源が光る背景画にする |
| [figure-grainy-glow](prompts/figure-grainy-glow/) | 人物・場所・雰囲気・色を指定するプロンプトに追加し、background-grainy-glow と同じ絵柄で人物のいる場面を描く |

illustration を追加した場合の比較です。

| 追加なし | 追加あり |
| --- | --- |
| ![追加なしの動画サムネイル](prompts/illustration/examples/03-before.webp) | ![追加ありの動画サムネイル](prompts/illustration/examples/03-after.webp) |

## ライセンス

[MIT](LICENSE)
