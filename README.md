# illustpedia

#画面
 - I000_ホーム画面
 - I001_ログイン画面
 - I002_アカウント登録画面
 - I003_ホーム画面（最新記事、あなたへのおすすめ）
 - I004_アカウント画面
 - I005_作者ページ作成画面
 - I006_作者ページ詳細画面
 - I007_作者ページ編集画面（編集、削除兼）
 - I008_タグ検索画面
 - I009_新規作者ページ（ランキングから）追加画面
 - I010_新規作者ページ（pixivのフォローから）追加画面
 - I011_すべての作者リスト画面
 
#更新について
 - 更新ボタン
 - ランキングから、またはユーザのpixivアカウントのフォローから作者の情報をクロールして更新
 - タグ（自分で設定）を更新
 - 更新したら追加、変更した結果ページを表示

#データベース
 - ユーザ
 - 作者ページ
 - タグ
 
#サーバー起動
 - pip install pillow
 - python manage.py runserver 0.0.0.0:8080
 - http://localhost:8080/
