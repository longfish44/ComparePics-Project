from django.db import models
from django.utils.translation import gettext_lazy as _ 

# Create your models here.
class CompareImageModels(models.Model):
    #画像名
    image_title1 = models.CharField(max_length=100, default="")
    image_title2 = models.CharField(max_length=100, default="")

    #画像
    image1 = models.ImageField(upload_to='compareimages/images/', default='')
    image2 = models.ImageField(upload_to='compareimages/images/', default='')
    
    #画像のタグ
    tags1 = models.CharField(max_length=250, default="")
    tags2 = models.CharField(max_length=250, default="")

    #画像の説明
    descriptions1 = models.CharField(max_length=250, default="")
    descriptions2 = models.CharField(max_length=250, default="")

    #画像のカテゴリ
    categories1 = models.CharField(max_length=250, default="")
    categories2 = models.CharField(max_length=250, default="")

    #色
    colors1 = models.CharField(max_length=250, default="")
    colors2 = models.CharField(max_length=250, default="")

    #画像のオブジェクト
    image_objects1 = models.CharField(max_length=250, default="")
    image_objects2 = models.CharField(max_length=250, default="")

    #画像タイプ
    image_types1 = models.CharField(max_length=250, default="")
    image_types2 = models.CharField(max_length=250, default="")

    #画像間のタグの類似度スコア
    tags_similarity = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

     #説明が一致していますか
    descriptions_similarity = models.BooleanField(default=False)

    #画像間のカテゴリの類似度スコア
    categories_similarity = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    #色が一致していますか
    colors_similarity = models.BooleanField(default=False)

    #画像間のオブジェクトの類似度スコア
    image_objects_similarity = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    #画像タイプが一致していますか
    image_types_similarity = models.BooleanField(default=False)

    #相関係数（Correlation）
    score_corr = models.DecimalField(max_digits=30, decimal_places=15, default=0.00000)

    #カイ二乗検定（Chi-Square）
    score_chi_square = models.DecimalField(max_digits=30, decimal_places=15, default=0.00000)

    #コンペア結果画像
    diffimage = models.ImageField(upload_to='compareimages/images/', default='')

    #画像コンペア結果
    result = models.CharField(max_length=250, default="")

    #画像分析ORコンペア時間
    completed = models.DateTimeField(null=True, blank=True)

    #当月Azure利用回数
    Azure_used_count = models.IntegerField(default=0) 

    #アクション区分
    actFlg = models.CharField(max_length=250, default="")

    def __str__(self):
        return self.image_title1
    
class apiModels(models.Model):    
    subscription_key = models.CharField(max_length=200, default="")
    endpoint = models.CharField(max_length=200, default="")
    created_datetime = models.CharField(max_length=200, default="")
    
class documentModels(models.Model):    
    title = models.CharField(max_length=200, default="")
    document = models.FileField(upload_to='compareimages/documents/', default='')
    created_datetime = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
class csvModels(models.Model):    
    csv = models.FileField(upload_to='compareimages/csv/', default='')
    created_datetime = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.csv.name    
    