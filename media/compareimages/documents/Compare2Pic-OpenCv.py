import cv2
import numpy as np
import sys
import os
from tkinter import Tk, filedialog

# 直方图を計算するメソッド
def compute_histogram(image):
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist

# 画像読み取り
image1 = cv2.imread(sys.argv[1])
image2 = cv2.imread(sys.argv[2])

# 画像読み取り成功かどうかのチェック
if image1 is None:
    print("エラー：画像１読み取り失敗")
if image2 is None:
    print("エラー：画像２読み取り失敗")

# 画像読み取り成功後の操作
if image1 is not None and image2 is not None:
    # 画像サイズ不一致の場合は、同じサイズに調整
    if image1.shape != image2.shape:
        image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
   
    # 画像差異を計算
    difference = cv2.subtract(image1, image2)
    b, g, r = cv2.split(difference)
   
    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
        print("画像完全一致")
        result = "画像完全一致"
    else:
        print("画像差異あり")
        result = "画像差異あり"
       
        # 直方図を計算
        hist1 = compute_histogram(image1)
        hist2 = compute_histogram(image2)
       
        # 直方図を比較
        # 相関係数（Correlation）：二つのヒストグラム間の線形関係を測定します。
        # カイ二乗検定（Chi-Square）：二つのヒストグラム間の差異を測定します。
        methods = ['相関係数（Correlation）', 'カイ二乗検定（Chi-Square）']
        scores = {}
        for method in methods:
            if method == '相関係数（Correlation）':
                scores[method] = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            elif method == 'カイ二乗検定（Chi-Square）':
                scores[method] = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
            print(f"Method: {method}, Score: {scores[method]}")        

        # 画像差異を表示
        # Tkinterを用いて保存ダイアログを表示
        root = Tk()
        root.withdraw()  # メインウィンドウを表示しない
        #save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        save_path = os.path.join(os.getcwd(), f"difference.png")
        cv2.imwrite(save_path, difference)

        if save_path:
            cv2.imwrite(save_path, difference)
            print(f"差異画像を{save_path}に保存しました")

        # 結果をTXTファイルに保存
        txt_path = os.path.join(os.getcwd(), f"comparison_results.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"画像１: {sys.argv[1]}\n")
            f.write(f"画像２: {sys.argv[2]}\n")
            f.write(f"結果: {result}\n")
            for method, score in scores.items():
                f.write(f"Method: {method}, Score: {score}\n")
            f.write(f"差異画像の保存先: {save_path}\n")
        print(f"比較結果を{txt_path}に保存しました")

else:
    print("画像のサイズとチャンネル数が一致")