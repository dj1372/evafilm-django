from django import forms
from django.utils import timezone
from giftcard.models import GiftCard


class GiftCardForm(forms.Form):
    code = forms.CharField(
        max_length=255,
        required=False,
        label="",
        label_suffix="",
        widget=forms.TextInput(attrs={
            "id": "txtCode",
            "type": "text",
            "placeholder": "کد کارت هدیه",
            'name': "code",
        })
    )

    def clean_code(self):
        now = timezone.localtime(timezone.now())
        code = self.cleaned_data.get("code")
        if code != "":
            dis_check = GiftCard.objects.get_object_or_None(code, now)
            if dis_check is None:
                raise forms.ValidationError(
                    "کد مورد نظر شما صحیح نمی باشد یا منقضی شده است لطفا از صحیح بودن آن اطمینان حاصل نمایید")
        return code
