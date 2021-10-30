import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from giftcard.forms import GiftCardForm
from giftcard.models import GiftCard, GiftCard_Related_to_User
from django.views.generic import FormView
from django.urls import reverse

from movies.models import Category


class Gift_Cart_View(LoginRequiredMixin, FormView):
    template_name = "subscription - g.html"
    form_class = GiftCardForm
    success_url = "gift"

    def post(self, request, *args, **kwargs):
        code = request.POST.get("code")
        if code != "":
            try:
                gift_code = GiftCard.objects.get_object_or_None(code=code, now=timezone.localtime(timezone.now()))
                all_cats_this_gift_code: Category = [cat_name.get("name_en") for cat_name in
                                                     [l for l in gift_code.category.all().values("name_en")]]
            except:
                return redirect(reverse(self.success_url, kwargs={"status": 2, }))
            now = timezone.localtime(timezone.now())
            if gift_code:
                try:
                    GiftCard_Related_to_User.objects.create(gift_code=gift_code, user=request.user, status=True,
                                                            date_enabeld=now)
                    return redirect(reverse(self.success_url, kwargs={"status": 1, }))
                except:
                    get_object_or_404(GiftCard_Related_to_User, gift_code=gift_code, user=request.user, status=True,
                                      date_enabeld=now)

        return redirect(reverse(self.success_url, kwargs={"status": 3, }))

    def get_context_data(self, **kwargs):
        context = super(Gift_Cart_View, self).get_context_data(**kwargs)
        context['status'] = self.kwargs.get("status")
        return context
