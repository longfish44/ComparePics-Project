import requests
import json
import cv2
import sys

# 設定APIキーとエンドポイント
subscription_key = "14d28b46fc8441169aaa75b30d8fe119"
endpoint = "https://picturecompare1.cognitiveservices.azure.com/vision/v3.2/analyze"

# 本地图片文件路径
image_path_1 = sys.argv[1]

# リクエストヘッダーとパラメーターの設定
headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type': 'application/octet-stream'
}
params = {'visualFeatures': 'Categories,Description,Color,Tags,Objects,ImageType'}


# 画像の特徴を取得する関数
def get_image_features(image_path):
    with open(image_path, 'rb') as image_file:
        response = requests.post(endpoint, headers=headers, params=params, data=image_file, verify=False)
        response.raise_for_status()
        return response.json()

# 画像の特徴を取得
features_1 = get_image_features(image_path_1)

# タグ
tags = features_1['description']['tags']
print(f"画像のタグ: {tags}")

# 説明
descriptions = features_1['description']
print(f"説明: {descriptions}")

# カテゴリ
categories = features_1['categories']
print(f"画像のカテゴリ: {categories}")

# 色
colors = features_1['color']
print(f"色: {colors}")

# オブジェクト
objects = features_1['objects']
print(f"画像のオブジェクト: {objects}")

# 画像タイプ
image_types = features_1['imageType']
print(f"画像タイプ: {image_types}")

