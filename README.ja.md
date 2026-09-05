# swe-agent-skills

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/green-tea-stalk/swe-agent-skills)](https://github.com/green-tea-stalk/swe-agent-skills/releases)
[![Release Please](https://github.com/green-tea-stalk/swe-agent-skills/actions/workflows/release-please.yml/badge.svg)](https://github.com/green-tea-stalk/swe-agent-skills/actions/workflows/release-please.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
> モダンな AI コーディングエージェントのための、再利用可能なソフトウェアエンジニアリング（SWE）実践スキル＆サブエージェント集。

[English](./README.md)

---

## 概要

`swe-agent-skills` は、AI コーディングエージェント（Google Antigravity、Claude Code、Codex CLI）に向けた、再利用可能なソフトウェアエンジニアリング（SWE）プラクティス、ワークフロー定義、およびサブエージェント集をプラグインとしてパッケージ化して提供するリポジトリです。

### 対応 AI コーディングエージェント

以下のモダンな AI コーディングエージェントにおいて、プラグインとして直接導入・利用できます。

- **Google Antigravity (AGY)**: `plugins/<name>/plugin.json` による自動プラグイン認識

- **Claude Code**: `.claude-plugin/plugin.json` によるプラグイン導入・Marketplace 対応
- **Codex CLI**: `.codex-plugin/plugin.json` によるプラグイン認識、`/plugins` コマンドによるプラグイン管理

### 前提要件

- **Git**
- **GitHub CLI (`gh`)**
- **Python 3**（標準ライブラリのみ使用。追加の `pip` パッケージのインストールは不要です）

---

## 収録プラグイン一覧

### `swe-workflow`

包括的なソフトウェアエンジニアリング（SWE）および仕様駆動開発（SDD: Spec-Driven Development）のワークフロー自動化、品質ゲートウェイ、および Git ライフサイクル管理を提供します。

| スキル | カテゴリ・役割 | 概要 |
| :--- | :--- | :--- |
| [`planning-and-designing`](./plugins/swe-workflow/skills/planning-and-designing/README.ja.md) | SDD 計画・設計 | インクリメンタルな要件ヒアリング、契約による設計（DbC）、および複数エージェント監査を通じて、検証可能かつバイリンガルな仕様資産（`requirements.md`, `design.md`, `tasks.md`）を策定。 |
| [`implementing-tasks`](./plugins/swe-workflow/skills/implementing-tasks/README.ja.md) | SDD 実装 | DbC 契約に基づく厳格な TDD（Red-Green-Refactor）、コードおよびセキュリティの二重監査、リファクタリング再検証、および Stacked PR の段階的構築を推進。 |
| [`committing-changes`](./plugins/swe-workflow/skills/committing-changes/README.ja.md) | Git 自動化 | ブランチ保護やシークレット混入などのコミット前安全検査を自動実行し、共同作成者情報を付与したコンテキスト豊かな Conventional Commit を作成。 |
| [`drafting-pull-request`](./plugins/swe-workflow/skills/drafting-pull-request/README.ja.md) | GitHub PR 管理 | リモート同期とブランチ安全性を検証し、`decision-analyst` による客観的な設計判断・トレードオフ抽出を経て release-please 互換のドラフト PR を作成・更新。 |

---

## クイックスタート（インストール・導入方法）

本リポジトリで提供するプラグインは特定のプロジェクトに依存しない汎用的な SWE プラクティスであるため、**ユーザースコープ（グローバル環境）にインストールして、作業するすべてのプロジェクトで横断的に利用**することを前提としています。


利用するエージェントに応じて、以下の手順で最短で導入してください。


### ① Google Antigravity (AGY)
リポジトリをローカルにクローンし、グローバル設定に登録します。

```bash
# 1. 任意の作業ディレクトリにクローン
git clone https://github.com/green-tea-stalk/swe-agent-skills.git ~/git/swe-agent-skills
```

**設定方法（推奨）**: グローバル設定ファイル `~/.gemini/config/plugins.json` にパスを登録します。
```json
{
  "entries": [
    { "path": "~/git/swe-agent-skills/plugins" }
  ]
}
```
*(または `ln -s ~/git/swe-agent-skills/plugins/<plugin-name> ~/.gemini/config/plugins/<plugin-name>` でシンボリックリンクを作成)*

### ② Claude Code
マーケットプレイスを追加し、必要なプラグインをグローバルにインストールします。

```bash
# マーケットプレイスの追加
/plugin marketplace add https://github.com/green-tea-stalk/swe-agent-skills

# プラグインのインストール（例: general-swe）
/plugin install <plugin-name>@swe-agent-skills
```

### ③ Codex CLI
Codex CLI 内でプラグインを追加します（グローバルに有効化されます）。
```bash
# プラグインの追加
/plugins add https://github.com/green-tea-stalk/swe-agent-skills
```

---

## コントリビューション・開発方針

本リポジトリは **Agent-First（AI コーディングエージェントによる自律開発・編集）** を前提として設計されています。人手による直接編集ではなく、AI コーディングエージェントを利用してプラグインやスキルを作成・改善することを前提としています。

### エージェント向け開発仕様（Single Source of Truth）
プラグインの内部アーキテクチャ、スキル作成標準、環境分離原則、エージェント運用ルールなどのすべての詳細は、以下に一元管理されています。

👉 **[AGENTS.md](./AGENTS.md)**

### 自律的なルール準拠と品質検証
AI エージェントが本リポジトリのスキルやプラグインを編集する際、ワークスペースルール（[`.agents/rules/`](./.agents/rules/)）が自動適用され、プロジェクトローカルの自己検証スキル（[`.agents/skills/validating-skills`](./.agents/skills/validating-skills/)）によって最新のオープン標準仕様への準拠が自律的に検証・保証されます。
