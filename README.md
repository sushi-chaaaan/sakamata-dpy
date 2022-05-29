
# sakamata-bot

![Discord](https://img.shields.io/discord/915910043461890078?color=blueviolet&label=Discord&logo=Discord&logoColor=white&style=flat-square)

## このリポジトリは？

ホロライブ所属VTuber沙花叉クロヱさんの非公式ファンDiscordサーバー  
[「クロヱ水族館」](https://discord.gg/EqfjtNBf2M)の運営/管理補助を行うBotのコードです。  
現在ライブラリをdiscord.pyへ変更しフルリファクタリングを行っています。  

## 開発環および使用ライブラリ

Python 3.10.4  
[discord.py](https://github.com/Rapptz/discord.py)
[dispander](https://github.com/sushi-chaaaan/dispander/tree/for2.0)([DiscordBotPortalJP様のライブラリ](https://github.com/DiscordBotPortalJP/dispander)をforkさせていただきました)  

## 機能追加履歴

> v2.0.0β(2022.05.29)
discord.pyによる書き直し  
現在進捗60%前後  
> v1.5.1(2022.02.21)

メッセージ送信機能の改善  
細かいバグ修正や最適化  
不要な機能の廃止  
歌枠データベース提供準備  

> v1.5.0(2022.02.11)

```python
await hogehoge()
```

ファイル構造の見直し  

> v1.3.4(2022.02.09)

Modalのリリースに伴い配信登録コマンドをModalへ移行  
Modalを利用したサーバー内問い合わせ/目安箱機能を実装  
その他細かいバグ修正  

> v1.3.3(2022.01.28)

ミニゲーム「Concept」が遊べるように  
メンバーシップ認証のフローがわかりやすくなった  
その他細かい最適化・修正  

> v.1.3.2(2022.01.25)

/userコマンドのデザイン変更  
スレッド一覧生成コマンド  
配信通知機能を停止

> v1.3.1(2022.01.24)

MessageCommandの上限に達したため翻訳をTransCordへ移行

> v1.3.0(2022.01.23)

配信通知機能のアップデート  
右クリックによる翻訳・ピン留めに対応  
投票機能の更新  
StarBoard機能のテスト  
濁点を付けて自慢する機能の追加  
スローモードの右クリックON/OFF  

> v1.2.1(2022.01.14)

Discordによる破壊的変更に対応するためBotのPrefixを`//`へ変更  

> v1.2.0(2022.01.10)

[holodex](https://pypi.org/project/holodex/0.9.7/) 0.9.7を利用した配信枠検知  
メンバーシップの継続や継続停止の際のメンバーシップコマンド  
timeoutへの対応  
配信のイベント登録の簡略化  
投票機能  

> v1.1.1(2022.01.03)

[pycord](https://github.com/Pycord-Development/pycord)へ移行  
[discord-ext-ui](https://pypi.org/project/discord-ext-ui/)を導入  
メッセージ展開の処理を改善  
メンバーシップ認証機能をブラッシュアップ  
ユーザー情報取得機能をブラッシュアップ  

> v1.1.0(2022.01.02)

確認を必要とするコマンドの処理の最適化  
メンバーシップ認証用コマンドを追加  
メッセージ展開の処理を改善

> v1.0.7(2021.12.31)

NGワード検知機能を強化  
自身のサーバー以外の招待URLを検知可能に  

> v1.0.6(2021.12.27)

NGワード検知機能を追加  

> v.1.0.5(2021.12.26)

コマンドごとの承認機能を追加  
コマンドを権限ごとにコントロール  
メッセージリンク展開の仕様変更  

> v1.0.4(2021.12.25)

不要な部分の最適化  
メッセージ送信/編集機能の追加  
エラー転送機能の実装  
実行ログ機能の実装  
VCログ機能のアップデート  

> v1.0.3(2021.12.19)

DM送受信機能/ping機能/user情報取得機能の追加  

> v1.0.2(2021.12.7)

メッセージ展開の処理を改善  

> v1.0.1(2021.12.5)

VCログの成形を改善  

> v1.0.0(2021.12.5)

Dispanderによるメッセージリンク展開に対応  
VCのログをユーザーID形式で保存する機能を追加  
