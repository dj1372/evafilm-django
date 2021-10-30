from django import forms
from django.contrib.auth import get_user_model

from discount_app.models import Discount
from django.utils import timezone
from discount_app.models import CheckUserDiscount

class DiscountForm(forms.Form):
	code = forms.CharField(
		max_length=16,
		required=False,
	    label="",
 	    label_suffix="",
		widget=forms.TextInput(attrs={
			"id":"txtCode",
			"type":"text",
			"placeholder":"کد تخفیف",
			'name':"code",
			})
		)

	def clean_code(self):

		# User = get_user_model()
		# user = User.objects.get(username=username)
		now = timezone.now()
		code = self.cleaned_data.get("code")
		if code != "":
			dis_check = Discount.objects.get_object_or_None(code, now)
			if dis_check is None:
				raise forms.ValidationError("کد مورد نظر شما صحیح نمی باشد یا منقضی شده است لطفا از صحیح بودن آن اطمینان حاصل نمایید")
		return code

