from django import forms
from django.utils.safestring import mark_safe
from rbac import models
from rbac.forms.base import BootStrapModelForm
from django.core.exceptions import ValidationError


class MenuModelForm(forms.ModelForm):
    class Meta:
        model = models.Menu
        fields = "__all__"
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.RadioSelect(
                choices=[
                    ['fa-address-book-o', mark_safe('<i class="fa fa-address-book-o" aria-hidden="true"></i>')],
                    ['fa-user-circle-o', mark_safe('<i class="fa fa-user-circle-o" aria-hidden="true"></i>')],
                    ['fa-id-card', mark_safe('<i class="fa fa-id-card" aria-hidden="true"></i>')],
                    ['fa-handshake-o', mark_safe('<i class="fa fa-handshake-o" aria-hidden="true"></i>')],
                    ['fa-check', mark_safe('<i class="fa fa-check" aria-hidden="true"></i>')],
                    ['fa-thumbs-up', mark_safe('<i class="fa fa-thumbs-up" aria-hidden="true"></i>')],
                    ['fa-jpy', mark_safe('<i class="fa fa-jpy" aria-hidden="true"></i>')],
                    ['fa-align-left', mark_safe('<i class="fa fa-align-left" aria-hidden="true"></i>')],
                    ['fa-align-justify', mark_safe('<i class="fa fa-align-justify" aria-hidden="true"></i>')],
                    ['fa-align-right', mark_safe('<i class="fa fa-align-right" aria-hidden="true"></i>')],
                    ['fa-apple', mark_safe('<i class="fa fa-apple" aria-hidden="true"></i>')],

                ]
            )
        }


class SecondMenuModelForm(BootStrapModelForm):
    class Meta:
        model = models.Permission
        fields = ['title', 'url', 'name', 'menu']


class PermissionModelForm(BootStrapModelForm):
    class Meta:
        model = models.Permission
        fields = ['title', 'name', 'url']


class MultiAddPermissionForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    menu_id = forms.ChoiceField(
        choices=[(None, '------')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    pid_id = forms.ChoiceField(
        choices=[(None, '-----')],
        widget=forms.Select(attrs={'class': "form-control"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_id'].choices += models.Menu.objects.values_list('id', 'title')
        self.fields['pid_id'].choices += models.Permission.objects.filter(pid__isnull=True).exclude(
            menu__isnull=True).values_list('id', 'title')


class MultiEditPermissionForm(forms.Form):
    id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    menu_id = forms.ChoiceField(
        choices=[(None, '------')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    pid_id = forms.ChoiceField(
        choices=[(None, '-----')],
        widget=forms.Select(attrs={'class': "form-control"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_id'].choices += models.Menu.objects.values_list('id', 'title')
        self.fields['pid_id'].choices += models.Permission.objects.filter(pid__isnull=True).exclude(
            menu__isnull=True).values_list('id', 'title')
