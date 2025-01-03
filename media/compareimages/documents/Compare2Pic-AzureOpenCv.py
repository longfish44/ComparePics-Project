import os
import cv2
import numpy as np
import sys
import requests
import json
from tkinter import Tk, filedialog

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
    ##########################################################################################################
    # Azure AI Visonでの画像コンペア
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

    # 各画像の特徴を取得
    features_1 = get_image_features(sys.argv[1])
    features_2 = get_image_features(sys.argv[2])

    # タグの類似度を計算
    tags_similarity = calculate_similarity(features_1['description']['tags'], features_2['description']['tags'])
    print(f"画像間のタグの類似度スコア: {tags_similarity}")

    # 説明を比較
    descriptions_similarity = compare_descriptions(features_1['description'], features_2['description'])
    print(f"説明が一致していますか: {descriptions_similarity}")

    # カテゴリを比較
    categories_similarity = compare_categories(features_1['categories'], features_2['categories'])
    print(f"画像間のカテゴリの類似度スコア: {categories_similarity}")

    # 色を比較
    colors_similarity = compare_colors(features_1['color'], features_2['color'])
    print(f"色が一致していますか: {colors_similarity}")

    # オブジェクトを比較
    max_len = max(len(features_1['objects']), len(features_2['objects']))
    if max_len == 0:
        print(f"画像間のオブジェクトの類似度スコア: 0")
        objects_similarity = 0
    else:
        objects_similarity = compare_objects(features_1['objects'], features_2['objects'])
        print(f"画像間のオブジェクトの類似度スコア: {objects_similarity}")

    # 画像タイプを比較
    image_types_similarity = compare_image_types(features_1['imageType'], features_2['imageType'])
    print(f"画像タイプが一致していますか: {image_types_similarity}")

    ##########################################################################################################
    # OpenCVでの画像コンペア
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

        f.write(f"画像間のタグの類似度スコア: {tags_similarity}\n")
        f.write(f"説明が一致していますか: {descriptions_similarity}\n")
        f.write(f"画像間のカテゴリの類似度スコア: {categories_similarity}\n")
        f.write(f"色が一致していますか: {colors_similarity}\n")
        f.write(f"画像間のオブジェクトの類似度スコア: {objects_similarity}\n")
        f.write(f"画像タイプが一致していますか: {image_types_similarity}\n")

        f.write(f"OpenCVコンペア結果: {result}\n")
        for method, score in scores.items():
            f.write(f"Method: {method}, Score: {score}\n")
        f.write(f"差異画像の保存先: {save_path}\n")
    print(f"比較結果を{txt_path}に保存しました")
       

else:
    print("画像のサイズとチャンネル数が一致しません")