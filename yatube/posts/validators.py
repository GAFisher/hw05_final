from django import forms


def validate_not_empty(value):
    if value == '':
        raise forms.ValidationError(
            'Это поле необходимо заполнить',
            params={'value': value},
        )
