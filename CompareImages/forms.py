from django import forms
from django.forms import ModelForm
from .models import CompareImageModels
from .models import apiModels
from .models import documentModels

class CompareImageForm(ModelForm):
    class Meta:
        model = CompareImageModels
        fields = ['image1','image2']

class imageUploadForm(ModelForm):
    class Meta:
        model = CompareImageModels
        fields = ['image1']

class apisettingForm(ModelForm):
    class Meta:
        model = apiModels
        fields = ['subscription_key','endpoint','created_datetime']
        widgets = {
            'created_datetime': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(apisettingForm, self).__init__(*args, **kwargs)
        self.fields['created_datetime'].required = False

class documentForm(ModelForm):
    class Meta:
        model = documentModels
        fields = ['title','document']

#class MultipleCompareForm(forms.ModelForm): 
#    class Meta: 
#        model = CompareImageModels 
#        fields = ['image1','image2'] 
        #newImage = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}))
        #oldImage = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}))
    #def __init__(self, *args, **kwargs):
    #    super(MultipleCompareForm, self).__init__(*args, **kwargs)
    #    self.fields['newImage'].required = False


