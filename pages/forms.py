from django import forms

# Base class used for incorporating the password authentication
class CurrentPasswordForm(forms.Form):
    current_password = forms.CharField(label='Enter your password for your account:',
                                       widget=forms.PasswordInput
                                       (attrs={'class':'form-control', 'placeholder':'******'}))
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

# Used for changing the first and/or last name
# Inherits from ChangePassForm and authenticates user before anything
# can be changed
class ChangeNameForm(CurrentPasswordForm):
    attributes_first = {'placeholder':'Jane', 'class':'form-control',
                        'name':'first_name', 'id':'firstName'}
    attributes_last = {'placeholder':'Doe', 'class':'form-control','name':'last_name',
                       'id':'lastName', 'onchange':'nonEmptyFields();'}
    first_name = forms.CharField(label='Enter new first name:',
                                 widget=forms.TextInput(attrs=attributes_first), max_length=50)
    last_name = forms.CharField(label='Enter new last name:',
                                widget=forms.TextInput(attrs=attributes_last), max_length=50)

    def __init__(self, *args, **kwargs):
        super(ChangeNameForm, self).__init__(*args, **kwargs)

# Used for changing the email of a user account
# Inherits from ChangePassForm and authenticates user before anything
# can be changed
class ChangeEmailForm(CurrentPasswordForm):
    attributes_email = {'placeholder':'email@unr.edu', 'class':'form-control',
                        'name':'email_addr', 'id':'NewEmail1'}
    attributes_confirm = {'placeholder':'email@unr.edu', 'class':'form-control','name':'email_confirm',
                       'id':'NewEmail2', 'onchange':'checkEmailMatch();'}
    email_addr = forms.EmailField(label='Enter new email:',
                                 widget=forms.EmailInput(attrs=attributes_email), max_length=50)
    email_confirm = forms.EmailField(label='Confirm new email:',
                                widget=forms.EmailInput(attrs=attributes_confirm), max_length=50)

    def __init__(self, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)





