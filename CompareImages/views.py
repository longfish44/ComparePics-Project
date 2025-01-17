from io import BytesIO
import cv2
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404 
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import CompareImageForm
from .models import CompareImageModels, csvModels 
from .forms import apisettingForm
from .forms import documentForm
from .forms import imageUploadForm
from .models import apiModels
from .models import documentModels
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.core.files.base import ContentFile
from .utils import *
from django.core.paginator import Paginator

def home(request):
    return render(request,'compareimages/home.html')

def compare1Upload(request):
    if request.method == 'GET':
        form = CompareImageForm()
        lastimage = CompareImageModels.objects.last()

        if (lastimage is None or lastimage.completed.year<timezone.now().year or lastimage.completed.month<timezone.now().month):
            azure_used_count =  0
        else:
            azure_used_count = lastimage.Azure_used_count
        
        return render(request, 'compareimages/compare1Upload.html', {'form':form,'Azure_used_count':azure_used_count})
    else:
        form = CompareImageForm(request.POST, request.FILES)

        if form.is_valid():
        	
            newImage = form.save(commit=False) 
            #Azureの無料枠の月間利用回数が5000回を超えかを判断します
            lastimage = CompareImageModels.objects.last()

            if (lastimage is None):
                azure_used_count =  1
            else:
                if lastimage.Azure_used_count > 0:
                   if lastimage.completed.year<timezone.now().year or lastimage.completed.month<timezone.now().month:
                      azure_used_count = 1  
                   else:                
                      azure_used_count = lastimage.Azure_used_count + 1
                else:
                    azure_used_count = 1  

            if azure_used_count > 5000:
                azure_used_count = azure_used_count - 1
                return render(request, 'compareimages/imageUpload.html', {'form': form, 'error': 'Azureの無料枠の月間利用回数が5000回になりましたため、誠に申し訳ございませんが、現在ご利用を一時停止させていただいております。','Azure_used_count':azure_used_count})
            
            # 画像の特徴を取得
            features_1 = get_image_features(newImage.image1)
            features_2 = get_image_features(newImage.image2)

            if 'error' in features_1:
                azure_used_count = azure_used_count - 1 
                return render(request, 'compareimages/compare1Upload.html', {'form': form, 'error': features_1['error'],'Azure_used_count':azure_used_count}) 

            if 'error' in features_2:
                azure_used_count = azure_used_count - 1 
                return render(request, 'compareimages/compare1Upload.html', {'form': form, 'error': features_2['error'],'Azure_used_count':azure_used_count}) 
    
            # タグ
            tags1 = features_1['description']['tags']
            tags2 = features_2['description']['tags']

            # 説明
            descriptions1 = features_1['description']
            descriptions2 = features_2['description']

            # カテゴリ
            categories1 = features_1['categories']
            categories2 = features_2['categories']

            # 色
            colors1 = features_1['color']
            colors2 = features_2['color']

            # オブジェクト
            if len(features_1['objects'] )== 0:
                objects1 = "No Object"
            else:
                objects1 = features_1['objects']

            if len(features_2['objects'] )== 0:
                objects2 = "No Object"
            else:
                objects2 = features_2['objects']

            # 画像タイプ
            image_types1 = features_1['imageType']
            image_types2 = features_2['imageType']

            # タグの類似度を計算
            tags_similarity = calculate_similarity(features_1['description']['tags'], features_2['description']['tags'])

            # 説明を比較
            descriptions_similarity = compare_descriptions(features_1['description'], features_2['description'])
            
            # カテゴリを比較
            categories_similarity = compare_categories(features_1['categories'], features_2['categories'])
    
            # 色を比較
            colors_similarity = compare_colors(features_1['color'], features_2['color'])

            # オブジェクトを比較
            max_len = max(len(features_1['objects']), len(features_2['objects']))
            if max_len == 0:
               image_objects_similarity = 0
            else:
               image_objects_similarity = compare_objects(features_1['objects'], features_2['objects'])

            # 画像タイプを比較
            image_types_similarity = compare_image_types(features_1['imageType'], features_2['imageType'])

            newImage.image_title1 = newImage.image1.name
            newImage.image_title2 = newImage.image2.name
            newImage.tags1 = tags1 
            newImage.descriptions1 = descriptions1
            newImage.categories1 = categories1 
            newImage.colors1 = colors1 
            newImage.image_objects1 = objects1 
            newImage.image_types1 = image_types1
            newImage.tags2 = tags2 
            newImage.descriptions2 = descriptions2
            newImage.categories2 = categories2 
            newImage.colors2 = colors2 
            newImage.image_objects2 = objects2 
            newImage.image_types2 = image_types2
            newImage.tags_similarity = tags_similarity 
            newImage.descriptions_similarity = descriptions_similarity 
            newImage.categories_similarity = categories_similarity 
            newImage.colors_similarity = colors_similarity 
            newImage.image_objects_similarity = image_objects_similarity 
            newImage.image_types_similarity = image_types_similarity
            newImage.completed = timezone.now()
            newImage.score_corr = 0
            newImage.score_chi_square = 0
            newImage.Azure_used_count = azure_used_count
            newImage.actFlg = '1対1比較'
            newImage.save() 

            
            ##########################################################################################################
            # OpenCVでの画像コンペア
            # 画像サイズ不一致の場合は、同じサイズに調整
            currentImage = CompareImageModels.objects.last()
            image1_path = currentImage.image1.path
            image2_path = currentImage.image2.path

            image1 = cv2.imread(image1_path) 
            image2 = cv2.imread(image2_path) 
            
            if image1.shape != image2.shape:
                image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

            # 画像差異を計算
            difference = cv2.subtract(image1, image2)
            b, g, r = cv2.split(difference)

            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                result = "画像完全一致"
            else:
                result = "画像差異あり"

            # 直方図を計算
            hist1 = compute_histogram(image1)
            hist2 = compute_histogram(image2)

            # 直方図を比較
            score_corr = 0
            score_chi_square = 0
            methods = ['相関係数（Correlation）', 'カイ二乗検定（Chi-Square）']
            for method in methods:
                if method == '相関係数（Correlation）':
                    score_corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                elif method == 'カイ二乗検定（Chi-Square）':
                    score_chi_square = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)

            # 画像差異を保存
            # Convert OpenCV BGR image to RGB
            difference = cv2.cvtColor(difference, cv2.COLOR_BGR2RGB) 

            # Convert OpenCV image to PIL Image
            pil_image = Image.fromarray(difference) 

            # Create an in-memory file for the image
            img_io = BytesIO()
            pil_image.save(img_io, 'JPEG') 

            # Save the image to the model field
            currentImage.diffimage.save('diff_image.jpg', ContentFile(img_io.getvalue()), save=False) 

            # 結果をmodelsに保存
            currentImage.result = result
            currentImage.score_corr = score_corr
            currentImage.score_chi_square = score_chi_square
            currentImage.save()
            return redirect('compare1Result') 

        else:
            return render(request, 'compareimages/compare1Upload.html', {'form': form, 'error': form.errors})

def compare1Result(request):
    image = CompareImageModels.objects.last()
    return render(request, 'compareimages/compare1Result.html', {'image':image})


def compareNUpload(request):
    if request.method == 'GET':
        form = CompareImageForm()
        lastimage = CompareImageModels.objects.last()

        if (lastimage is None or lastimage.completed.year<timezone.now().year or lastimage.completed.month<timezone.now().month):
            azure_used_count =  0
        else:
            azure_used_count = lastimage.Azure_used_count

        return render(request, 'compareimages/compareNUpload.html', {'form':form,'Azure_used_count':azure_used_count})
    else:
        form = CompareImageForm(request.POST, request.FILES)
        #Azureの無料枠の月間利用回数が5000回を超えかを判断します
        lastimage = CompareImageModels.objects.last()
        if (lastimage is None):
            azure_used_count =  1
        else:
            if lastimage.Azure_used_count > 0:
                if lastimage.completed.year<timezone.now().year or lastimage.completed.month<timezone.now().month:
                    azure_used_count = 1  
                else:                
                    azure_used_count = lastimage.Azure_used_count + 1
            else:
                azure_used_count = 1  

            if azure_used_count > 5000:
                azure_used_count = azure_used_count - 1 
                return render(request, 'compareimages/compareNUpload.html', {'form': form, 'error': 'Azureの無料枠の月間利用回数が5000回なりましたため、誠に申し訳ございませんが、現在ご利用を一時停止させていただいております。','Azure_used_count':azure_used_count})
        
        new_images = request.FILES.getlist('image1')
        old_images = request.FILES.getlist('image2')
        if form.is_valid():

            samename_accout = 0 

            tokyo_tz = pytz.timezone('Asia/Tokyo')
            timestamp = timezone.now().astimezone(tokyo_tz).strftime("%Y%m%d_%H%M%S")
            csv_name = f"compareResult_{timestamp}.csv"

            csv_content = [] 
            csv_content.append(["画像名", "タグの類似度スコア", "説明が一致", "カテゴリの類似度スコア", "色が一致", "オブジェクトの類似度スコア", "画像タイプが一致", "OpenCVでの画像コンペア結果", "相関係数（Correlation）", "カイ二乗検定（Chi-Square）"])

            for newimage in new_images: 
                for oldimage in old_images: 
                    if newimage.name == oldimage.name:

                        newImage = CompareImageModels()
 
                        # 画像の特徴を取得
                        features_1 = get_image_features(newimage)
                        features_2 = get_image_features(oldimage)

                        if 'error' in features_1:
                            azure_used_count = azure_used_count - 1 
                            return render(request, 'compareimages/compareNUpload.html', {'form': form, 'error': features_1['error'],'Azure_used_count':azure_used_count}) 

                        if 'error' in features_2:
                            azure_used_count = azure_used_count - 1 
                            return render(request, 'compareimages/compareNUpload.html', {'form': form, 'error': features_2['error'],'Azure_used_count':azure_used_count}) 
    
                        # タグ
                        tags1 = features_1['description']['tags']
                        tags2 = features_2['description']['tags']

                        # 説明
                        descriptions1 = features_1['description']
                        descriptions2 = features_2['description']

                        # カテゴリ
                        categories1 = features_1['categories']
                        categories2 = features_2['categories']

                        # 色
                        colors1 = features_1['color']
                        colors2 = features_2['color']

                        # オブジェクト
                        if len(features_1['objects'] )== 0:
                            objects1 = "No Object"
                        else:
                            objects1 = features_1['objects']

                        if len(features_2['objects'] )== 0:
                            objects2 = "No Object"
                        else:
                            objects2 = features_2['objects']

                        # 画像タイプ
                        image_types1 = features_1['imageType']
                        image_types2 = features_2['imageType']

                        # タグの類似度を計算
                        tags_similarity = calculate_similarity(features_1['description']['tags'], features_2['description']['tags'])

                        # 説明を比較
                        descriptions_similarity = compare_descriptions(features_1['description'], features_2['description'])
            
                        # カテゴリを比較
                        categories_similarity = compare_categories(features_1['categories'], features_2['categories'])
    
                        # 色を比較
                        colors_similarity = compare_colors(features_1['color'], features_2['color'])

                        # オブジェクトを比較
                        max_len = max(len(features_1['objects']), len(features_2['objects']))
                        if max_len == 0:
                            image_objects_similarity = 0
                        else:
                            image_objects_similarity = compare_objects(features_1['objects'], features_2['objects'])

                        # 画像タイプを比較
                        image_types_similarity = compare_image_types(features_1['imageType'], features_2['imageType'])


                        newImage.image_title1 = newimage.name
                        newImage.image_title2 = oldimage.name
                        newImage.image1 = newimage
                        newImage.image2 = oldimage
                        newImage.Azure_used_count = azure_used_count
                        newImage.tags1 = tags1 
                        newImage.descriptions1 = descriptions1
                        newImage.categories1 = categories1 
                        newImage.colors1 = colors1 
                        newImage.image_objects1 = objects1 
                        newImage.image_types1 = image_types1
                        newImage.tags2 = tags2 
                        newImage.descriptions2 = descriptions2
                        newImage.categories2 = categories2 
                        newImage.colors2 = colors2 
                        newImage.image_objects2 = objects2 
                        newImage.image_types2 = image_types2
                        newImage.tags_similarity = tags_similarity 
                        newImage.descriptions_similarity = descriptions_similarity 
                        newImage.categories_similarity = categories_similarity 
                        newImage.colors_similarity = colors_similarity 
                        newImage.image_objects_similarity = image_objects_similarity 
                        newImage.image_types_similarity = image_types_similarity
                        newImage.score_corr = 0
                        newImage.score_chi_square = 0
                        newImage.Azure_used_count = azure_used_count
                        newImage.actFlg = 'N対N比較'
                        newImage.completed = timezone.now()
                        newImage.save() 
                        
                        ##########################################################################################################
                        # OpenCVでの画像コンペア
                        # 画像サイズ不一致の場合は、同じサイズに調整
                        currentImage = CompareImageModels.objects.last()
                        image1_path = currentImage.image1.path
                        image2_path = currentImage.image2.path

                        image1 = cv2.imread(image1_path) 
                        image2 = cv2.imread(image2_path) 
            
                        if image1.shape != image2.shape:
                           image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

                        # 画像差異を計算
                        difference = cv2.subtract(image1, image2)
                        b, g, r = cv2.split(difference)

                        if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                            result = "画像完全一致"
                        else:
                            result = "画像差異あり"

                        # 直方図を計算
                        hist1 = compute_histogram(image1)
                        hist2 = compute_histogram(image2)

                        # 直方図を比較
                        score_corr = 0
                        score_chi_square = 0
                        methods = ['相関係数（Correlation）', 'カイ二乗検定（Chi-Square）']
                        for method in methods:
                            if method == '相関係数（Correlation）':
                               score_corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                            elif method == 'カイ二乗検定（Chi-Square）':
                               score_chi_square = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)

                        # 画像差異を保存
                        # Convert OpenCV BGR image to RGB
                        difference = cv2.cvtColor(difference, cv2.COLOR_BGR2RGB) 

                        # Convert OpenCV image to PIL Image
                        pil_image = Image.fromarray(difference) 

                        # Create an in-memory file for the image
                        img_io = BytesIO()
                        pil_image.save(img_io, 'JPEG') 

                        # Save the image to the model field
                        currentImage.diffimage.save('diff_image.jpg', ContentFile(img_io.getvalue()), save=False) 

                        # 結果をmodelsに保存
                        currentImage.result = result
                        currentImage.score_corr = score_corr
                        currentImage.score_chi_square = score_chi_square
                        samename_accout = samename_accout + 1 
                        currentImage.save()
                        
                        # 結果をCSVに保存
                        csv_content.append([currentImage.image_title1, currentImage.tags_similarity, currentImage.descriptions_similarity, currentImage.categories_similarity, currentImage.colors_similarity, currentImage.image_objects_similarity, currentImage.image_types_similarity, currentImage.result, currentImage.score_corr, currentImage.score_chi_square])

                        #当月Azure利用回数+1
                        azure_used_count = azure_used_count + 1

            if samename_accout == 0:
                azure_used_count = azure_used_count - 1 
                return render(request, 'compareimages/compareNUpload.html', {'form': form, 'error': '選択した画像に同じファイ名の画像が存在しません。','Azure_used_count':azure_used_count})
            else:
                csv_string = "" 
                for row in csv_content: 
                    csv_string += ",".join(map(str, row)) + "\n" 
                csv_file = ContentFile(csv_string.encode('utf-8-sig'))
                csv_instance = csvModels.objects.create() 
                csv_instance.csv.save(csv_name, csv_file) 
                csv_instance.created_datetime = timezone.now()
                csv_instance.save()

                return redirect('compareNResult') 
        else:
            return render(request, 'compareimages/compareNUpload.html', {'form': form, 'error': form.errors})
 
def compareNResult(request):
    csv = csvModels.objects.last()
    return render(request, 'compareimages/compareNResult.html', {'csv':csv})


def imageUpload(request):
    if request.method == 'GET':
        form = imageUploadForm()
        lastimage = CompareImageModels.objects.last()

        if (lastimage is None or lastimage.completed.year<timezone.now().year or lastimage.completed.month<timezone.now().month):
            azure_used_count =  0
        else:
            azure_used_count = lastimage.Azure_used_count
        
        return render(request, 'compareimages/imageUpload.html', {'form':form,'Azure_used_count':azure_used_count})
    else:
        form = imageUploadForm(request.POST, request.FILES)

        if form.is_valid():
        	
            newImage = form.save(commit=False) 

            #Azureの無料枠の月間利用回数が5000回を超えかを判断します
            lastimage = CompareImageModels.objects.last()

            if (lastimage is None):
                azure_used_count =  1
            else:
                if lastimage.Azure_used_count > 0:
                   if lastimage.completed.year<timezone.now().year or lastimage.completed.month<timezone.now().month:
                      azure_used_count = 1  
                   else:                
                      azure_used_count = lastimage.Azure_used_count + 1
                else:
                    azure_used_count = 1  

            if azure_used_count > 5000:
                azure_used_count = azure_used_count - 1
                return render(request, 'compareimages/imageUpload.html', {'form': form, 'error': 'Azureの無料枠の月間利用回数が5000回になりましたため、誠に申し訳ございませんが、現在ご利用を一時停止させていただいております。','Azure_used_count':azure_used_count})
            
            # 画像の特徴を取得
            features_1 = get_image_features(newImage.image1)

            if 'error' in features_1:
                azure_used_count = azure_used_count - 1 
                return render(request, 'compareimages/imageUpload.html', {'form': form, 'error': features_1['error'],'Azure_used_count':azure_used_count}) 

            # タグ
            tags1 = features_1['description']['tags']

            # 説明
            descriptions1 = features_1['description']

            # カテゴリ
            categories1 = features_1['categories']

            # 色
            colors1 = features_1['color']

            # オブジェクト
            if len(features_1['objects'] )== 0:
                objects1 = "No Object"
            else:
                objects1 = features_1['objects']

            # 画像タイプ
            image_types1 = features_1['imageType']

            newImage.image_title1 = newImage.image1.name
            newImage.tags1 = tags1 
            newImage.descriptions1 = descriptions1
            newImage.categories1 = categories1 
            newImage.colors1 = colors1 
            newImage.image_objects1 = objects1 
            newImage.image_types1 = image_types1
            newImage.completed = timezone.now()
            newImage.Azure_used_count = azure_used_count
            newImage.actFlg = '画像分析'
            newImage.save() 
            return redirect('imageDisplay') 

        else:
            return render(request, 'compareimages/imageUpload.html', {'form': form, 'error': form.errors})

def imageDisplay(request):
    image = CompareImageModels.objects.last()
    return render(request, 'compareimages/imageDisplay.html', {'image':image})

def apisetting(request):
    if request.method == 'GET':
        form = apisettingForm()
        lastapi = apiModels.objects.last()

        return render(request, 'compareimages/apisetting.html', {'form': form, 'error': form.errors,'lastapi':lastapi})
    else:
        form = apisettingForm(request.POST)
 
        if form.is_valid():
            newApi = form.save(commit=False) 
            newApi.created_datetime = timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')
            newApi.save() 
            return redirect('apisetting') 

        else:
            return render(request, 'compareimages/apisetting.html', {'form': form, 'error': form.errors})

def documentUpload(request):
    if request.method == 'GET':
        return render(request, 'compareimages/documentUpload.html', {'form':documentForm()})
    else:
        form = documentForm(request.POST, request.FILES)

        if form.is_valid():
            newDocument = form.save(commit=False) 
            newDocument.created_datetime = timezone.now()
            newDocument.save() 
            return redirect('documentDisplay') 
        else:
            return render(request, 'compareimages/documentUpload.html', {'form': form, 'error': form.errors})

def documentDisplay(request):
    documents = documentModels.objects.all()
    return render(request, 'compareimages/documentDisplay.html', {'documents':documents})

def history(request):
    act_flg_query = request.GET.get('actFlg') 
    completed_query = request.GET.get('completed') 
    history_list = CompareImageModels.objects.all() 
    history_cnt = history_list.count()
    if act_flg_query: 
        history_list = history_list.filter(actFlg=act_flg_query) 
    
    if completed_query: 
        history_list = history_list.filter(completed__date=completed_query) 
    
    history_list = history_list.order_by('-completed')
    
    paginator = Paginator(history_list, 10) 
    
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number) 
    return render(request, 'compareimages/history.html', { 'page_obj': page_obj, 'actFlg': act_flg_query, 'completed': completed_query ,'history_cnt':history_cnt})

def detail_view(request, pk):
    image = get_object_or_404(CompareImageModels, pk=pk)
    return render(request, 'compareimages/compare1Result.html', {'image':image})

def delete_old_history(request):
    two_months_ago = timezone.now() - timezone.timedelta(days=60)
    old_records = CompareImageModels.objects.filter(completed__lt=two_months_ago)
    old_csv = csvModels.objects.filter(created_datetime__lt=two_months_ago)

    for record in old_records:
        # 物理删除文件
        if record.image1 and os.path.isfile(record.image1.path):
            os.remove(record.image1.path)
        if record.image2 and os.path.isfile(record.image2.path):
            os.remove(record.image2.path)
        if record.diffimage and os.path.isfile(record.diffimage.path):
            os.remove(record.diffimage.path)
        # 删除数据库记录
        record.delete()

    for csv in old_csv:
        # 物理删除文件
        if csv.csv and os.path.isfile(csv.csv.path):
            os.remove(csv.csv.path)
        # 删除数据库记录
        csv.delete()

    return render(request, 'compareimages/delete_history.html', {'deleted_count': len(old_records),'deleted_csv_count': len(old_csv)})
