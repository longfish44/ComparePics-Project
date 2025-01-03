# 画像の特徴を取得する関数
import csv
import os
import cv2
import requests
from CompareImages.models import apiModels
from CompareImages.models import CompareImageModels
from django.utils import timezone 
import pytz



def get_image_features(image_field):
  try:
      # 設定APIキーとエンドポイント
      lastapi = apiModels.objects.last()
      if (lastapi):
          subscription_key = lastapi.subscription_key
          endpoint = lastapi.endpoint
      else: 
          return {'error': 'Error reading api'}
      
      # リクエストヘッダーとパラメーターの設定
      headers = {
          'Ocp-Apim-Subscription-Key': subscription_key,
          'Content-Type': 'application/octet-stream'
      }
      params = {'visualFeatures': 'Categories,Description,Color,Tags,Objects,ImageType'}

      image_data = image_field.read() 
      
      # ファイルオブジェクトの場合
      if hasattr(image_data, 'seek') and hasattr(image_data, 'tell'):
          image_data.seek(0, os.SEEK_END)
          file_size = image_data.tell()
          image_data.seek(0)  # ファイルポインタを先頭に戻す
      elif isinstance(image_data, bytes):
          file_size = len(image_data)
      else:
          # その他のケースに対応
          raise TypeError("Unsupported image data type")

      if file_size > 4 * 1024 * 1024:
         return {'error': 'Error:Azure使用制限のため、分析対象のサイズが４Mを超えません。'}

  except Exception as e:
      return {'error': f'Error reading image: {str(e)}'}

  # Send the image data (or preprocessed image) to your analysis endpoint
  # (replace 'endpoint' with the actual URL)
  response = requests.post(endpoint, headers=headers, params=params, data=image_data, verify=False)

  if 'error' in response.json():
      return {'error': response.json()['error']['message']}
  else:    
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

# 直方図を計算するメソッド
def compute_histogram(image):
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist

#コンペア結果をCSVに保存
def compareResult_to_csv(compareResult):
    try:
        tokyo_tz = pytz.timezone('Asia/Tokyo')
        timestamp = timezone.now().astimezone(tokyo_tz).strftime("%Y%m%d_%H%M%S")

        csv_name = f"compareResult_{timestamp}.csv"

        with open(csv_name, mode='w', newline='', encoding='utf-8-sig') as file:  # UTF-8 BOM付き
            writer = csv.writer(file)
            writer.writerow(["画像名", 
                             "タグの類似度スコア", 
                             "説明が一致", 
                             "カテゴリの類似度スコア", 
                             "色が一致", 
                             "オブジェクトの類似度スコア", 
                             "画像タイプが一致",
                             "OpenCVでの画像コンペア結果",
                             "相関係数（Correlation）", 
                             "カイ二乗検定（Chi-Square）"])
            writer.writerow([compareResult.image_title1, 
                             compareResult.tags_similarity, 
                             compareResult.descriptions_similarity, 
                             compareResult.categories_similarity, 
                             compareResult.colors_similarity, 
                             compareResult.image_objects_similarity, 
                             compareResult.image_types_similarity, 
                             compareResult.result, 
                             compareResult.score_corr, 
                             compareResult.score_chi_square])

            compareResult.csv = csv_name
            compareResult.completed = timezone.now()
            return compareResult
    except Exception as e:
        return {'error': f' CSV File に書き込みエラー: {str(e)}'}
