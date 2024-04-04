# 環境構築
1. `docker compose up -d --build`

# Python の実行
1. `docker compose up -d`
2. `docker compose exec python bash`
3. `python main.py`

# 導入ライブラリ一覧
requirements.txtに一覧がある。
- pycodestyle==2.11.1,autopep8==2.0.4 
   Pythonコードをコーディング規約(PEP)準拠に自動修正するフォーマッター  
   使用例：`autopep8 -i main.py`
- Pillow==9.3.0
   画像処理ライブラリその1 リサイズやトリミングといった画像の変換処理に特化したライブラリ  

- opencv-python
   画像処理ライブラリその2 AI分野にも活用される高機能な画像処理ソフトウェア

- libgl1-mesa-dev
    dockerでopencv-pythonを使おうとしたときにセットでインストール
