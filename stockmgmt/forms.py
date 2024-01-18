from django import forms
from .models import *
from django.forms.widgets import DateInput, Select 

class DateInput(forms.DateInput):
    input_type = 'date'

class StockCreateForm(forms.ModelForm):
   class Meta:
     model = Stock
     fields = ['category', 'item_name', 'price']

  

     widgets = {
            'category': Select(attrs={'class': 'form-control'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            # 'expiration_date': DateInput(attrs={'class': 'form-control'}),
        }
    #  def clean_expiration_date(self):
    #     expiration_date = self.cleaned_data.get('expiration_date')
    #     if expiration_date is None:
    #         raise forms.ValidationError("Expiration date is required.")
    #     return expiration_date
    
   
class StockHistorySearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)
    
    class Meta:
        model = StockHistory
        fields = ['category', 'item_name', 'start_date', 'end_date']
		
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['item_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Item Name'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control',})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control',})


class StockSearchForm(forms.ModelForm):
   export_to_CSV = forms.BooleanField(required=False)
   class Meta:
     model = Stock
     fields = ['category', 'item_name']
     
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['item_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Item Name'})

class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'price',]

        widgets = {
             'expiration_date': DateInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Get the user object from kwargs
        super().__init__(*args, **kwargs)
        
        if not user.is_staff:  # Check if the user is not staff
            for field_name in self.fields:
                self.fields[field_name].widget.attrs['readonly'] = True  # Set the fields as read-only

        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['item_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Item Name'})
        self.fields['price'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Item price'})
        
        
   

class IssueForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['issue_quantity', ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['issue_quantity'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Issue Quantity'})
        
	

class ReceiveForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['receive_quantity',]
		
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['receive_quantity'].widget.attrs.update({'class': 'form-control'})
        
class ReorderLevelForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['reorder_level'] 
          
	def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
         self.fields['reorder_level'].widget.attrs.update({'class': 'form-control'})

        #  pormosa sabaysaby