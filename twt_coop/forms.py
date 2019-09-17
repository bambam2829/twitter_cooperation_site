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
    def clean_maxFollowInt(self):
        maxFollowInt = self.data.get('maxFollowInt')
        castMaxFollowInt = int(maxFollowInt)
        if 1 > castMaxFollowInt or castMaxFollowInt > 100:
            raise forms.ValidationError(u'フォロー数は1~100の値で入力してください')
        return maxFollowInt

    def __init__(self, *args, **kwargs):
        super(TwitteAutoFollowForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
