from django.db import models
from accounts.models import SubscriptionPlan
from django.contrib.auth import get_user_model

User = get_user_model()


transactions_status_choice = (
    (0, 'ایجاد شده'), (1, 'تایید شده'), (2, 'لغو شده'), (3, 'انجام شده')
)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=16)
    ref_id = models.CharField(max_length=55)
    card_holder_info = models.CharField(max_length=255)
    sales_reference_id = models.CharField(max_length=55)
    seen = models.BooleanField(default=False)
    status = models.SmallIntegerField(choices=transactions_status_choice, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' - ' + self.get_status_display() + ' - ' + self.order_id

    def get_created_at(self):
        return f'{self.created_at.year}/{self.created_at.month}/{self.created_at.day}'
        # return '{}/{}/{}'.format(self.created_at.year, self.created_at.month, self.created_at.day)
