"""ComparePics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from CompareImages import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    #Home
    path('', views.home,name='home'),

    path('admin/', admin.site.urls),

    path('compare1Upload/', views.compare1Upload, name='compare1Upload'),
    path('compare1Result/', views.compare1Result, name='compare1Result'),

    path('compareNUpload/', views.compareNUpload, name='compareNUpload'),
    path('compareNResult/', views.compareNResult, name='compareNResult'),

    path('imageUpload/', views.imageUpload, name='imageUpload'),
    path('imageDisplay/', views.imageDisplay, name='imageDisplay'),

    path('history/', views.history, name='history'),
    path('detail/<int:pk>/', views.detail_view, name='detail'),

    path('deleteHistory/', views.delete_old_history, name='deleteHistory'),

    path('apisetting/', views.apisetting, name='apisetting'),
    path('documentUpload/', views.documentUpload, name='documentUpload'),
    path('documentDisplay/', views.documentDisplay, name='documentDisplay'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
