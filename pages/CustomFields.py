from django import forms


class CustomEmailField(forms.Field):

    default_validators = []

    def to_python(self):
        pass

    def validate(self):
        pass

    def run_validators(self):
        pass

    def clean(self):
        pass