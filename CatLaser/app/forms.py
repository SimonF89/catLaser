"""
Definition of forms.
"""

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from .models import Point, Edge, Playground, POINT_TYPE



class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class EdgeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EdgeForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            for point in Point.objects.all():
                print(point.type)
            self.fields['A'].queryset = Point.objects.filter(type=POINT_TYPE[0][0])
            self.fields['B'].queryset = Point.objects.filter(type=POINT_TYPE[0][0])
            self.fields['Vr'].queryset = Point.objects.filter(type=POINT_TYPE[2][0])
            self.fields['Nr'].queryset = Point.objects.filter(type=POINT_TYPE[2][0])
