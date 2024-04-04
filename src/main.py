import glob
import sys
import os
import datetime
# 自作モジュールインポート
import my_logger
import img_editor

""" ログ設定 """
dt_now = datetime.datetime.now()
log_file_name = 'log/' + dt_now.strftime('%Y%m%d%H%M%S') + '.log'
logger = my_logger.set_logger(__name__, log_file_name)


def main():
    print('start')
    # モジュール宣言
    img = img_editor.ImgEditor(log_file_name)

    # コマンドライン引数1：元データのあるフォルダのパス(.env.CARD_IMAGE_PATHからの相対パス)
    # コマンドライン引数2：加工後データを保存するフォルダ名
    args = sys.argv
    if len(args) < 2:
        print('引数を入力してください')
        return
    org_path = f'/images/{args[1]}'
    save_path = f'{org_path}/{args[2]}'
    os.makedirs(save_path, exist_ok=True)

    # フォルダから画像の一覧を取得する
    png_list = glob.glob(f'{org_path}/*.png')
    if len(png_list) == 0:
        print('画像がありません')
        return

    for img_path in png_list:
        # ファイル名のみ抜き出す
        base_path, extension = os.path.splitext(img_path)
        img_name = base_path[base_path.rfind('/')+1:]

        # 輪郭検出してトリミング
        img.save_trimed_card(img_name, org_path, save_path)

    print('end')


if __name__ == '__main__':
    main()
    
