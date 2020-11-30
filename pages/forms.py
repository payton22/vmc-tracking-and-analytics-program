from django import forms

class CurrentPasswordForm(forms.Form):
    current_password = forms.CharField(label='Enter Current Password:',
                                       widget=forms.PasswordInput(attrs={'class':'form-control'}))
    error_css_class = 'error'
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CurrentPasswordForm, self).__init__(*args, **kwargs)

    def check_entry(self):
        password = self.data['current_password']
        if not self.user.check_password(password):
            self.add_error('current_password', 'Incorrect Password. Please'
                                                     ' enter the correct password for your account.')
            return False
        else:
            return True



