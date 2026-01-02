# products/forms.py
from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    new_category = forms.CharField(
        required=False,
        label="Suggest New Category",
        widget=forms.TextInput(attrs={
            "placeholder": "Eg: Toys, Machinery, Furniture"
        })
    )

    class Meta:
        model = Product
        fields = [
            "title", "price", "category",
            "description", "image"
        ]
    