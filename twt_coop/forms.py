from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


class TwitteAutoFollowForm(forms.Form):
    keyword = forms.CharField(
        label='キーワード',
        max_length=100,
        required=True,
    )
    maxFollowInt = forms.IntegerField(
        label='フォロー数',
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        required=True,
    )
