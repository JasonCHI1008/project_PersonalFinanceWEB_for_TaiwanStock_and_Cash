# 💰 個人理財管理 WEB アプリ / Personal Finance Management Web App

Flask と SQLite を使って作成した個人向けの資産管理 WEB アプリです。  
台幣・米ドルの現金資産、株式購入履歴、為替情報などを一元管理し、円グラフで可視化します。

A personal finance tracker built with **Flask**, **SQLite3**, and **matplotlib**.  
Track your cash balances (TWD/USD), stock investments, and visualize everything with interactive pie charts.

---

## 🚀 デモ / Demo

> ※（Renderでサイトをデプロイします）  
> [👉 サイトを見る / View the Site](https://project-personalfinanceweb-for.onrender.com)

---

## 🔧 使用技術 / Technologies Used

| 種類               | ツール                                                         |
| ------------------ | -------------------------------------------------------------- |
| Web フレームワーク | Flask                                                          |
| データベース       | SQLite3                                                        |
| グラフ描画         | matplotlib                                                     |
| 為替 API           | [https://tw.rter.info/capi.php](https://tw.rter.info/capi.php) |
| 株価取得           | TWSE（https://www.twse.com.tw）                                |
| フロントエンド     | HTML / CSS (Jinja2 templating)                                 |

---

## 🧩 機能 / Features

- ✅ 台幣・米ドルの現金入力・削除
- ✅ 株式取引履歴（コード・株数・単価・手数料・税金・日付）を保存
- ✅ 現在の為替レートを自動取得
- ✅ TWSE API から当月株価を取得し、市価・損益（ROE）を計算
- ✅ 円グラフで以下を可視化：
  - 株式ごとの保有割合
  - 現金 + 株式 全体の資産割合
