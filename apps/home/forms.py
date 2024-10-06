from django import forms

class BookLocationForm(forms.Form):
    book_title = forms.CharField(max_length=100, label='Enter the name of the second book')
