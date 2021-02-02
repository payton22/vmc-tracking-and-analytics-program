from django import forms

class DateForm(forms.Form):
    date = forms.CharField(label="date(mm/dd/yyyy)", max_length=10)

