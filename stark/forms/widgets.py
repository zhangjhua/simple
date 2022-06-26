from django import forms


class Datetimepicker(forms.TextInput):
    template_name = 'form_temp/widget/datetimepicker.html'
