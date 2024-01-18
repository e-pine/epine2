from django.forms import ModelForm
from django import forms
from .models import *
from django.forms.widgets import DateInput, Select 

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Input the type of pineapple here...'})

class DateInput(forms.DateInput):
    input_type = 'date'

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['category', 'number_planted', 'price_per_plant']

        widgets = {
            'category': Select(attrs={'class': 'form-control'}),
            'number_planted': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_plant': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'number_planted': 'Total Planted',
        }
class YieldForm(forms.ModelForm):
    class Meta:
        model = Yield
        fields = ['category', 'number_yield', 'harvest_date']
        
        widgets = {
            'category': Select(attrs={'class': 'form-control'}),
            'number_yield': forms.TextInput(attrs={'class': 'form-control'}),
            'harvest_date': DateInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'number_yield': 'Total Harvest',
        }

class BadPineForm(forms.ModelForm):
    class Meta:
        model = BadPine
        fields = ['category', 'number_yield', 'harvest_date']
        
        widgets = {
            'category': Select(attrs={'class': 'form-control'}),
            'number_yield': forms.NumberInput(attrs={'class': 'form-control'}),
            'harvest_date': DateInput(attrs={'class': 'form-control'}),
        }

class WorkerForm(forms.ModelForm):
    class Meta:
        model = WorkersExpense
        fields = ['name', 'price_pay', 'workers', 'days']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price_pay': forms.TextInput(attrs={'class': 'form-control'}),
            'workers': forms.TextInput(attrs={'class': 'form-control'}),
            'days': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'name': 'Work for',
            'price_pay': 'Salary per Day',
            'workers': 'Number of Workers'
        }

class ApplyFerPesForm(forms.ModelForm):
    class Meta:
        model = ApplyFerPes
        fields = ['product_name', 'type', 'price', 'quantity_used']

        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': Select(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity_used': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StartExpenceForm(forms.ModelForm):
    class Meta:
        model = StartExpense
        fields = ['category', 'price', 'total_number']

        widgets = {
            'category': Select(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'total_number': forms.TextInput(attrs={'class': 'form-control'}),
        }










class YieldSearchForm(forms.ModelForm):
   export_to_CSV = forms.BooleanField(required=False)
   class Meta:
     model = Yield
     fields = ['category',]
     
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})

class PriceForm(forms.ModelForm):
    class Meta:
        model = PinePrice
        fields = ['price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].widget.attrs.update({'class': 'form-control',})

class ValueForm(forms.ModelForm):
    class Meta:
        model = PineValue
        fields = ['value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].widget.attrs.update({'class': 'form-control',})

# for high quality
class BiddingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BiddingForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(groups__name='buyer')

    class Meta:
        model = BiddingProcess
        fields = ['user', 'category', 'bid_price',]

        widgets = {
            'user': Select(attrs={'class': 'form-control'}),
            'category': Select(attrs={'class': 'form-control'}),
            'bid_price': forms.TextInput(attrs={'class': 'form-control'}),

        }
        labels = {
            'category': 'Pineapples Variety'
        }

class BuyPineTotal(forms.ModelForm):
    def __int__(self, *args, **kwargs):
        super(BiddingForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(groups__name='buyer')
    class Meta:
        model = BiddingProcess
        fields = ['total_buy_pine']

        widgets = {
            'total_buy_pine': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'You can add data here after the harvesting ....'}),
        }

# for low quality
class HarvestedBadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HarvestedBadForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(groups__name='buyer')
        
    class Meta:
        model = HarvestedBad
        fields = ['user', 'category', 'total_number', 'price']

        widgets = {
            'user': Select(attrs={'class': 'form-control'}),
            'category': Select(attrs={'class': 'form-control'}),
            'total_number': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
        }

# for rejected
class RejectedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RejectedForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(groups__name='buyer')

    class Meta:
        model = RejectedPine
        fields = ['user', 'category', 'total_number', 'price']

        widgets = {
            'user': Select(attrs={'class': 'form-control'}),
            'category': Select(attrs={'class': 'form-control'}),
            'total_number': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['end_date']  # Exclude end_date field from the form
        widgets = {
            'start_date': forms.TextInput(attrs={'readonly': 'readonly'}),  # Make start_date readonly
        }