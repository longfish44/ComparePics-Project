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


# Azure API Key And Endpoint
subscription_key = "14d28b46fc8441169aaa75b30d8fe119"
endpoint = "https://picturecompare1.cognitiveservices.azure.com/vision/v3.2/analyze"

# Azure AI Vision のヘッダーとパラメタ設置
headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type': 'application/octet-stream'
}
params = {'visualFeatures': 'Categories,Description,Color,Tags,Objects,ImageType'}

# 直方図を計算するメソッド
def compute_histogram(image):
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist

# 画像の特徴を取得する関数
def get_image_features(image_path):
    with open(image_path, 'rb') as image_file:
        response = requests.post(endpoint, headers=headers, params=params, data=image_file, verify=False)
        response.raise_for_status()
        return response.json()

# タグの類似度を計算する関数
def calculate_similarity(tags_1, tags_2):
    tags_1_set = set(tags_1)
    tags_2_set = set(tags_2)
    common_tags = tags_1_set.intersection(tags_2_set)
    similarity_score = len(common_tags) / max(len(tags_1_set), len(tags_2_set))
    return similarity_score

# 説明を比較する関数
def compare_descriptions(desc_1, desc_2):
    return desc_1['captions'][0]['text'] == desc_2['captions'][0]['text']

# カテゴリを比較する関数
def compare_categories(cat_1, cat_2):
    cat_1_set = set(cat['name'] for cat in cat_1)
    cat_2_set = set(cat['name'] for cat in cat_2)
    common_cats = cat_1_set.intersection(cat_2_set)
    return len(common_cats) / max(len(cat_1_set), len(cat_2_set))

# 色を比較する関数
def compare_colors(color_1, color_2):
    return color_1['dominantColorForeground'] == color_2['dominantColorForeground'] and \
           color_1['dominantColorBackground'] == color_2['dominantColorBackground']

# オブジェクトを比較する関数
def compare_objects(obj_1, obj_2):
    obj_1_set = set(obj['object'] for obj in obj_1)
    obj_2_set = set(obj['object'] for obj in obj_2)
    common_objs = obj_1_set.intersection(obj_2_set)
    return len(common_objs) / max(len(obj_1_set), len(obj_2_set))

# 画像タイプを比較する関数
def compare_image_types(type_1, type_2):
    return type_1['clipArtType'] == type_2['clipArtType'] and type_1['lineDrawingType'] == type_2['lineDrawingType']

# フォルダー内の画像ファイルを読み込む関数
def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
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
    writer.writerow(["画像名", "タグの類似度スコア", "説明が一致", "カテゴリの類似度スコア", "色が一致", "オブジェクトの類似度スコア", "画像タイプが一致","OpenCVでの画像コンペア結果","相関係数（Correlation）", "カイ二乗検定（Chi-Square）", "保存先"])

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

                # Azure AI Visonでの画像コンペア
                features_1 = get_image_features(path1)
                features_2 = get_image_features(path2)

                tags_similarity = calculate_similarity(features_1['description']['tags'], features_2['description']['tags'])
                descriptions_similarity = compare_descriptions(features_1['description'], features_2['description'])
                categories_similarity = compare_categories(features_1['categories'], features_2['categories'])
                colors_similarity = compare_colors(features_1['color'], features_2['color'])
                max_len = max(len(features_1['objects']), len(features_2['objects']))
                objects_similarity = 0 if max_len == 0 else compare_objects(features_1['objects'], features_2['objects'])
                image_types_similarity = compare_image_types(features_1['imageType'], features_2['imageType'])

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
                #save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
                #if save_path:
                #    cv2.imwrite(save_path, difference)

                save_path = os.path.join(os.getcwd(), f"{name1}_difference.png")
                cv2.imwrite(save_path, difference)
                   

                writer.writerow([name1, tags_similarity, descriptions_similarity, categories_similarity, colors_similarity, objects_similarity, image_types_similarity, image_diff, score_corr, score_chi_square, save_path])

print(f"比較結果を{csv_file_path}に保存しました")