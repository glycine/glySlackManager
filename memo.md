# 実装方針

1. チャンネルリストをとる
2. 各チャンネルごとに，ファイルリストをとる
3. 日付でソートする
4. ファイルサイズをもとに，削除する対象のファイルを決める（古いもの順）
5. 削除実施
6. 実行結果をログチャンネルに投稿

# file情報として有用なもの

* id
* created
* timestamp
* name
* title
* minetype
* filetype
* user
* size
* is_external
* channels