from django import forms

class DateForm(forms.Form):
    date = forms.CharField(label="date", max_length=10)

