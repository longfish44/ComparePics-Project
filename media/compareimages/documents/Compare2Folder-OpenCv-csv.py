import cv2
import numpy as np
import sys
import os
import requests
import json
from tkinter import Tk, filedialog
import csv
import re


def replace_tilde(directory):
  """
  指定されたディレクトリ内のファイル名で「～」を「-」に置き換えます。

  Args:
    directory: ファイルを検索するディレクトリ  """
  for filename in os.listdir(directory):
    # ファイル名に「～」が含まれている場合のみ処理
    if "～" in filename:
      old_path = os.path.join(directory, filename)
      new_filename = re.sub("～", "-", filename)
      new_path = os.path.join(directory, new_filename)
      os.rename(old_path, new_path)
      print(f"{filename} を {new_filename} にリネームしました。")

# 直方図を計算するメソッド
def compute_histogram(image):
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist

# フォルダー内の画像ファイルを読み込む関数
def load_images_from_folder(folder):
    images = []

    for entry in os.scandir(folder):
        if entry.is_file() and entry.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename = entry.name
            img_path = entry.path

            # 画像を読み込む
            img = cv2.imread(img_path)
   
        if img is not None:
            images.append((filename, img_path, img))
    return images

# 比較結果を保存するCSVファイルのパス
csv_file_path = 'comparison_results.csv'

# フォルダーのパス
folder1 = sys.argv[1]
folder2 = sys.argv[2]

# リネーム対象のディレクトリ
target_directory = folder1  # 自分のディレクトリパスに置き換えてください
replace_tilde(target_directory)

target_directory = folder2  # 自分のディレクトリパスに置き換えてください
replace_tilde(target_directory)


# フォルダー内の画像を読み込む
images1 = load_images_from_folder(folder1)
images2 = load_images_from_folder(folder2)

# 比較結果をCSVファイルに保存
with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:  # UTF-8 BOM付き
    writer = csv.writer(file)
    writer.writerow(["画像名", "OpenCVでの画像コンペア結果","相関係数（Correlation）", "カイ二乗検定（Chi-Square）", "差異イメージ保存先"])

    for (name1, path1, image1) in images1:
        for (name2, path2, image2) in images2:

            # 画像読み取り成功かどうかのチェック
            if image1 is None:
                print("エラー：画像１読み取り失敗")
                continue
            if image2 is None:
                print("エラー：画像２読み取り失敗")
                continue

            # 同じファイル名の画像をコンペア
            if name1 == name2:

                # OpenCVでの画像コンペア
                if image1.shape != image2.shape:
                    image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

                difference = cv2.subtract(image1, image2)
                b, g, r = cv2.split(difference)
                image_diff = "画像完全一致" if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0 else "画像差異あり"

                # 直方図を計算
                hist1 = compute_histogram(image1)
                hist2 = compute_histogram(image2)

                # 直方図を比較
                score_corr, score_chi_square = 0, 0
                methods = ['相関係数（Correlation）', 'カイ二乗検定（Chi-Square）']
                for method in methods:
                    if method == '相関係数（Correlation）':
                        score_corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                    elif method == 'カイ二乗検定（Chi-Square）':
                        score_chi_square = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)

                root = Tk()
                root.withdraw()  # メインウィンドウを表示しない

                save_path = os.path.join(os.getcwd(), f"{name1}_difference.png")
                cv2.imwrite(save_path, difference)
                   

                writer.writerow([name1, image_diff, score_corr, score_chi_square, save_path])

print(f"比較結果を{csv_file_path}のに保存しました")