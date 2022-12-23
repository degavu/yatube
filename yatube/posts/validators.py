from django import forms


def validate_not_empty(value):
    if value == '':
        raise forms.ValidationError(
            'Пустое поле не допустимо!',
            params={'value': value},
        )


def min_size(value):
    size = len(value)
    if size < 10:
        raise forms.ValidationError(
            'Пост должен содержать не меньше 10 символов',
            params={'value': value},
        )


def size_comment(value):
    size = len(value)
    if size < 4:
        raise forms.ValidationError(
            'Комментарий должен содержать не меньше 4 символов',
            params={'value': value},
        )
    if size > 140:
        raise forms.ValidationError(
            'Комментарий должен содержать не больше 140 символов',
            params={'value': value},
        )
