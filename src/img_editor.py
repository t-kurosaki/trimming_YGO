import cv2
import numpy as np
import my_logger


class ImgEditor:
    save_path = '/images'  # カード画像保存先
    save_cnt = 0  # 途中経過コピーに連番を振る用
    img_name = ''

    def __init__(self, log_file_name):
        """ ログ設定 """
        self.logger = my_logger.set_logger(__name__, log_file_name)
        self.logger.debug('__init__')

    def save_trimed_card(self, img_name, org_path, save_path):
        """ カードを輪郭で切り抜き、台形補正、リサイズして保存
        Returns:
            Bool: 成功/失敗
            string: 保存画像のフルパス
        """
        self.logger.debug(f'edge_trim_and_crop STRAT:{img_name}')
        self.save_path = save_path
        self.save_cnt = 0

        # エッジ検出
        result, edges, img = self.__find_edges_by_Canny(img_name, org_path)

        if result:
            # エッジを切り抜く
            img_cropped = self.__transform_by4(img, edges)
            # img_cropped = self.rotate_cut(img, edges[0], edges[1], edges[2])

            # 画像を保存する
            filename = f'{self.save_path}/{img_name}.png'
            cv2.imwrite(filename, img_cropped)
            self.logger.debug(f'edge_trim_and_crop END_SUCCESS:{img_name}')
            return True, filename

        else:
            # 検出失敗時
            self.logger.debug(f'edge_trim_and_crop END_FAILED:{img_name}')
            return False, None

    def __find_edges_by_Canny(self, img_name, org_path):
        """ エッジ検出 
        Returns:
            Bool: 成功/失敗
            list: [4,2] 
            list: img
        """
        self.logger.debug('find_edges_by_Canny STRAT:' + img_name)

        # 画像を読み込む
        filename = f'{org_path}/{img_name}.png'
        img = cv2.imread(filename)
        self.__tagging_img(img,self.save_path,img_name,'無加工')

        # 元画像に白縁を追加（はみ出た部分を輪郭検出するため）
        num_insert = 50  # 追加枠ピクセル数
        # 枠作成
        blank1 = np.zeros((num_insert, img.shape[1], 3))
        blank2 = np.zeros((img.shape[0] + num_insert * 2, num_insert, 3))
        # 全ゼロデータに255を足してホワイトにする
        blank1 += 255
        blank2 += 255
        # 挿入
        img = np.insert(img, 0, blank1, axis=0)
        img = np.insert(img, img.shape[0], blank1, axis=0)
        img = np.insert(img, [0], blank2, axis=1)
        img = np.insert(img, [img.shape[1]], blank2, axis=1)
        self.__tagging_img(img,self.save_path,img_name,'白縁追加')

        # グレースケール変換
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.__tagging_img(img_gray,self.save_path,img_name,'グレースケール変換')

        # # 2値化
        # th, img_gray_th_binary = cv2.threshold(img_gray,210,255,cv2.THRESH_BINARY)
        # self.__tagging_img(img_gray_th_binary,self.save_path,img_name,'2値化')

        # Cannyフィルタ
        edges = cv2.Canny(image=img_gray, threshold1=100, threshold2=200)
        self.__tagging_img(edges,self.save_path,img_name,'Cannyフィルタ')

        # 輪郭取得
        contours, hierarchy = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 輪郭が見つかったか
        if len(contours) == 0:
            self.logger.debug('find_edges_by_Canny END_FAILED:' + img_name)
            return False, None, img

        else:
            # 最大矩形
            box_2d_max = None
            # 暫定の最大矩形面積
            box_2d_max_temp = 0

            # # [DEBUG]輪郭の点の描画
            img_disp = img.copy()
            img_disp2 = img.copy()
            img_disp3 = img.copy()

            for i, contour in enumerate(contours):
                self.logger.debug(i)
                # 傾いた外接する矩形領域
                box_2d = cv2.minAreaRect(contour)  # 輪郭情報（contour）を囲む最小面積の矩形
                
                # より面積の大きい矩形を採用
                if self.__get_area_by_box_2d(box_2d) > box_2d_max_temp:
                    box_2d_max_temp = self.__get_area_by_box_2d(box_2d)
                    box_2d_max = box_2d

                # # [DEBUG]輪郭を描画
                box_points = cv2.boxPoints(box_2d)  # 矩形の4つの頂点座標
                box_points = np.intp(box_points)  # 整数値に変換

                cv2.drawContours(img_disp, contours, i, (255, 0, 0), 2)
                cv2.drawContours(img_disp2, [box_points], 0, (0, 255, 0), 2)

            # # [DEBUG]輪郭を描画
            box_points = cv2.boxPoints(box_2d_max)  # 矩形の4つの頂点座標
            box_points = np.intp(box_points)  # 整数値に変換
            cv2.drawContours(img_disp3, [box_points], 0, (0, 0, 255), 2)

            # [DEBUG]保存
            self.__tagging_img(img_disp,self.save_path,img_name,'輪郭情報')
            self.__tagging_img(img_disp2,self.save_path,img_name,'輪郭矩形変換')
            self.__tagging_img(img_disp3,self.save_path,img_name,'最大輪郭')
            
            self.logger.debug('find_edges_by_Canny END_SUCCESS:' + img_name)
            return True, box_2d_max, img

    def __transform_by4(self, img, box_2d):
        """ 4点を指定してトリミングする。 """
        self.logger.debug('transform_by4 STRAT')

        # 矩形の4つの頂点座標
        box_points = cv2.boxPoints(box_2d)

        # 　幅/高さ取得
        height = box_2d[1][0]
        width = box_2d[1][1]

        # 変換後の4点 (白い部分が入らないように1ピクセル内側に調整)
        dst = np.float32([[-2, -2], [width+1, -2], [width+1, height+1], [-2, height+1]])
    
        # 変換行列
        trans = cv2.getPerspectiveTransform(box_points, dst)

        # 射影変換・透視変換する
        img_warp = cv2.warpPerspective(img, trans, (int(width), int(height)))
        self.__tagging_img(img_warp,self.save_path,self.img_name,'射影変換')

        # 必要に応じて回転
        if width > height:
            img_warp = cv2.rotate(img_warp, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.__tagging_img(img_warp,self.save_path,self.img_name,'回転')

        # 遊戯王サイズにリサイズ
        img_warp = cv2.resize(img_warp, dsize=(590, 860))
        self.__tagging_img(img_warp,self.save_path,self.img_name,'リサイズ')

        self.logger.debug('transform_by4 END_SUCCESS')
        return img_warp

    def __rotate_cut(self, img, center, size, deg):
        """射影変換と比較して画質が変わらないため使用していない"""
        self.logger.debug('STRAT')

        # 回転行列
        rot_mat = cv2.getRotationMatrix2D(center, -(90.0 - deg), 1.0)

        # 回転中心画像の中心へ　-(元画像内での中心位置)+(切り抜きたいサイズの中心)-(ちょい内側を切り取る)
        rot_mat[0][2] += -center[0]+size[1]/2 - 1.5  # Y
        rot_mat[1][2] += -center[1]+size[0]/2 - 1.5  # X

        # 回転・切り取り
        height = int(size[0]) - 2
        width = int(size[1]) - 2

        self.logger.debug('END_SUCCESS')
        return cv2.warpAffine(img, rot_mat, dsize=(width, height))

    def __get_area_by_box_2d(self, box_2d):
        """ 矩形情報から面積を取得 """
        # 　幅/高さ取得
        height = box_2d[1][0]
        width = box_2d[1][1]
        return height * width
    
    def __tagging_img(self,img,save_path,img_name,tag=""):
        if tag == "":
            filename = f'{save_path}/{img_name}_{self.save_cnt}.png'
        else:
            filename = f'{save_path}/{img_name}_{self.save_cnt}_{tag}.png'
        self.save_cnt += 1
        cv2.imwrite(filename, img)
        self.logger.debug('tagging img:' + filename)
