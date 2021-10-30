import json
import uuid

import requests
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import SubscriptionPlan, Subscription
from .models import Transaction
from datetime import datetime, timedelta
from .PyMellat import BMLPaymentAPI
import random
from django.urls import reverse
from zeep import Client

from django.views.generic import ListView  # view to show # list of plans
from django.contrib.auth.mixins import LoginRequiredMixin  # user must bt login
from discount_app.forms import DiscountForm  # choice a discount code
from discount_app.models import Discount, CheckUserDiscount
from django.utils import timezone
from django.contrib.auth import get_user_model
from payments.pyMelli import PaymentRequestInput, encrypt_des3_token
from django.contrib.auth.decorators import login_required

User = get_user_model()
pgw = BMLPaymentAPI(username='evafilm', password='74592411', terminal_id=5920279)
try:
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
except:
    client = None
MERCHANT = '8e29ad2b-15c6-46c4-82d8-43c86f5515a9'


def round_up(num, flag=None):
    if flag != None:
        return int(round(num))
    return int(round(num) + 1)


def check_money_with_discount(code, price):
    now = timezone.localtime(timezone.now())
    discount = Discount.objects.get_object_or_None(code, now)
    money = 0
    discount_percent = 0
    if discount is not None:
        discount_percent = discount.discount_percent
        discount_apply = 1 - (discount_percent / 100)
        money = round_up(price * discount_apply, "flag")
    return discount_percent, money


def Take_an_object_and_decide(request, transaction):
    if hasattr(transaction.user, 'SubscriptionPlan'):
        ####################################################################################
        older_plan_spacial_id = request.GET.get("spacial_id")
        older_plan_defind = SubscriptionPlan.objects.get_object_or_none_sp(older_plan_spacial_id)
        old_plan = Subscription.objects.get(user=transaction.user, plan=older_plan_defind)
        ####################################################################################
        bought_plan = transaction.subscription_plan

        # current_plan_status_is_vip = current_plan.is_vip  # True or False
        ####################################################################################
        switch_status = request.GET.get("switch_status")  # s T s = 0 // s T v = 1 // v T v = 2 // c T s = 3 // None
        if switch_status == "0":  # simple to simple
            now = timezone.localdate(timezone.now())  # زمان الان تاریخش
            current_plan_valid_days = (old_plan.end_date - now).days  # کم کردن اعتبار پلن قدیمی با زمان الان
            time_add = transaction.user.SubscriptionPlan.end_date  # روز باقی مانده پلن قدیمی
            time_add += timedelta(days=current_plan_valid_days)  # جمع دو تاش
            old_plan.end_date = time_add  # ریختن جمع دو تاش توی پلن قدیمی
            old_plan.save()
        ####################################################################################
        elif switch_status == "1":  # simple to vip
            now = timezone.localdate(timezone.now())  # زمان الان تاریخش
            left_day_current_plan = (old_plan.end_date - now).days  # کم کردن اعتبار پلن قدیمی با زمان الان
            old_plan.plan = bought_plan  # تعویض پلن کاربر

            end_date = old_plan.end_date  # گرفتن زمان پلن قدیمی
            end_date += timedelta(days=left_day_current_plan)  # جمع زمان پلن قدیمی و روز های باقی موندش با پلن خریده شد

            old_plan.end_date = end_date  # ریختن زمان و عوض کردن پلن به وی ای پی انجام شد
            old_plan.save()
        elif switch_status == "2":  # vip to vip
            now = timezone.localdate(timezone.now())  # زمان الان تاریخش
            current_plan_valid_days = (old_plan.end_date - now).days  # کم کردن اعتبار پلن قدیمی با زمان الان
            time_add = bought_plan.valid_days + current_plan_valid_days  #
            old_plan.end_date += timedelta(days=time_add)
            old_plan.save()

        elif switch_status == "3":  # vip to simple
            err = "شما نمی توانید هنگامی که اکانت وی ای پی دارید از اکانت معمولی استفاده نمایید"
        else:
            pass


def chand_status_dis_code(user, request):
    from discount_app.models import CheckUserDiscount
    user = user
    code = request.GET.get('code')
    dis = Discount.objects.get(code=code)
    CheckUserDiscount.objects.create(user=user, discount=dis, status=True, date_use=timezone.localtime(timezone.now()))


class subscription_view(LoginRequiredMixin, ListView):
    template_name = 'subscription.html'

    def get(self, request):
        context = {}
        try:
            msg = request.GET.get('msg')
            order_id = request.GET.get('order')
        except:
            msg = None
        if msg is None or msg == '':
            context["subscription_plans"] = SubscriptionPlan.objects.exclude(price=0).order_by('name')
            if hasattr(request.user, 'SubscriptionPlan'):
                user_subscription_valid_days = (request.user.SubscriptionPlan.end_date - datetime.now().date()).days
            else:
                context["user_subscription_valid_days"] = -1
            return render(request, self.template_name, context)
        else:
            try:
                transaction = Transaction.objects.get(order_id=order_id)
                if not transaction.seen:
                    transaction.seen = True
                    transaction.save()
                    return render(request, 'subscription-payment-confirm.html', {'msg': msg})
                else:
                    return redirect(reverse("Subscription"))
            except:
                return redirect(reverse("Subscription"))

    def post(self, request, *args, **kwargs):
        cx = {}
        plan_name = request.POST["plan_name"]
        selected_plan = SubscriptionPlan.objects.get(name=plan_name)
        switch_status = "-1"
        if hasattr(request.user, 'SubscriptionPlan'):
            current_plan = request.user.SubscriptionPlan.plan
            if current_plan is not None:
                if (not current_plan.is_vip) and (not selected_plan.is_vip):  # simple to simple
                    switch_status = "0"
                elif (not current_plan.is_vip) and (selected_plan.is_vip):  # simple to vip
                    switch_status = "1"
                elif (current_plan.is_vip) and (selected_plan.is_vip):  # vip to vip
                    switch_status = "2"
                else:
                    switch_status = "3"  # vip to simple
                    err = "شما نمی توانید هنگامی که اکانت وی ای پی دارید از اکانت معمولی استفاده نمایید تا پایان مدت زمان انقضای اکانتتان شکیبا باشید برای بازگشت از دکمه بازگشت استفاده نمایید"
                    cx["err"] = err
                    return render(request, 'subscription.html', cx)

        cx["discount_form"] = DiscountForm(request.POST or None)
        cx['selected_plan'] = selected_plan
        cx['vat_price'] = 0  # maliat 9 %
        cx['invoice_price'] = round_up(round(cx['selected_plan'].price + cx['vat_price']))
        cx['selected_item'] = cx['selected_plan'].title + ' (' + str(cx['selected_plan'].price) + ' تومان)'

        if plan_name is not None or plan_name != "":
            return redirect(reverse("check_discount_code", kwargs={"plan_name": plan_name}))
        else:
            return render(request, 'subscription.html', cx)


@login_required
def check_discount_code(request, plan_name):
    selected_plan = SubscriptionPlan.objects.get(name=plan_name)
    switch_status = "-1"
    if hasattr(request.user, 'SubscriptionPlan'):
        current_plan = request.user.SubscriptionPlan.plan
        limitation = current_plan.max_valid_days
        time_add = request.user.SubscriptionPlan.end_date  # روز باقی مانده پلن قدیمی
        time_add += timedelta(days=selected_plan.valid_days)  # جمع دو تاش
        upgrade_day = request.user.SubscriptionPlan.start_date + timedelta(days=limitation)  # محدودیت خرید پلن
        if current_plan is not None:
            if (not current_plan.is_vip) and (not selected_plan.is_vip):  # simple to simple
                if time_add > upgrade_day:  # اگه جمع دو تاش  بزرگتر از تایم محدودیت بشه حالشو بگیر
                    err = f"مدت زمان پلن شما برای ارتقا بالا تر از {limitation} روز خواهد شد و این مجاز نیست برای بازگشت از دکمه بازگشت استفاده کنید یا روی دکمه زیر کلیک نمایید"
                    return render(request, 'subscription.html', {"err": err})
                else:
                    switch_status = "0"
            elif (not current_plan.is_vip) and (selected_plan.is_vip):  # simple to vip
                switch_status = "1"
            elif (current_plan.is_vip) and (selected_plan.is_vip):  # vip to vip
                if time_add > upgrade_day:
                    err = f"مدت زمان پلن شما برای ارتقا بالا تر از {limitation} روز خواهد شد و این مجاز نیست برای بازگشت از دکمه بازگشت استفاده کنید یا روی دکمه زیر کلیک نمایید"
                    return render(request, 'subscription.html', {"err": err})
                else:
                    switch_status = "2"
            else:
                switch_status = "3"  # vip to simple
                err = "شما نمی توانید هنگامی که اکانت وی ای پی دارید از اکانت معمولی استفاده نمایید تا پایان مدت زمان انقضای اکانتتان شکیبا باشید برای بازگشت از دکمه بازگشت استفاده نمایید"
                return render(request, 'subscription.html', {"err": err})

    code = ""
    discount = []
    now = timezone.localtime(timezone.now())
    discount_form = DiscountForm(request.POST or None)
    selected_plan = get_object_or_404(SubscriptionPlan, name=plan_name)
    price = selected_plan.price
    vat_price = 0  # maliat 9 %
    invoice_price = round_up(round(price + vat_price), "other flag")
    selected_item = selected_plan.title + ' (' + str(price) + ' تومان)'
    er = ""
    if discount_form.is_valid():
        code = discount_form.cleaned_data.get("code")
        use_check = CheckUserDiscount.objects.get_object_or_None(user=request.user, code=code)  # check use before
        use_check_w_s = CheckUserDiscount.objects.get_object_or_None_w_s(user=request.user,
                                                                         code=code)  # check Exist Useable or Not
        if code == "":
            pass
        elif use_check is None:
            if use_check_w_s is None:  # Not Exist Useable
                pass
            else:  # unUseable
                er = "کد مورد نظر شما قبلا توسط حساب شما استفاده شده است لطفا از کد دیگری استفاده نمایید"

    discount = Discount.objects.get_object_or_None(code, now)
    money = 0
    discount_percent = 0

    if discount is not None and er == "":
        discount_percent = discount.discount_percent
        discount_apply = 1 - (discount_percent / 100)
        money = round_up((price * discount_apply))
        discount_percent, money = check_money_with_discount(code, price)

    cx = {
        "code": code,
        "discount": discount,
        'discount_form': discount_form,
        'selected_plan': selected_plan,
        'vat_price': vat_price,
        'invoice_price': invoice_price,
        'selected_item': selected_item,
        "money_with_dis": int(money),
        "percent": int(discount_percent),
        "plan_name": plan_name,
        "errror": er,
        "switch_status": switch_status,
    }
    return render(request, 'subscription-order-confirm.html', cx)


@login_required
def subscription_payment_create(request):
    if request.method == 'GET':
        return redirect(reverse("Subscription"))

    elif request.method == 'POST':
        plan_name = request.POST.get('plan_name')
        selected_plan = SubscriptionPlan.objects.get_object_or_none(plan_name)
        payment_way = request.POST.get('payway')
        vat_price = 0  # round_up(round((selected_plan.price / 100) * 9))
        invoice_price = round_up(round(selected_plan.price + vat_price), "flag")
        ######################################################################
        code = request.POST.get("code")
        if code is not None:
            discount_percent, money = check_money_with_discount(code, selected_plan.price)
            if money:
                invoice_price = round_up(round(money + vat_price), "other flag")
        ######################################################################
        if hasattr(request.user, "SubscriptionPlan"):
            current_plan = request.user.SubscriptionPlan.plan
        switch_status = request.POST.get("switch_status")
        ######################################################################
        if Transaction.objects.count() > 0:
            tid = Transaction.objects.last().id + random.randint(1000000, 9999999)
        else:
            tid = 1 + random.randint(1000000, 9999999)
        ######################################################################
        url = request.headers["Host"].split(":")[0]
        if hasattr(request.user, "SubscriptionPlan"):
            call_back_url_melli = f'https://{url}/subscription/callback/melli/{tid}/?spacial_id={current_plan.spacial_id}&switch_status={switch_status}&code={code}'  # + Authority + Status
            ######################################################################
            call_back_url_mellat = f'https://{url}/subscription/callback/mellat/{tid}/?spacial_id={current_plan.spacial_id}&switch_status={switch_status}&code={code}'  # + Authority + Status
            ######################################################################
            call_back_url_zarinpall = f'https://{url}/subscription/callback/zarinpal/?spacial_id={current_plan.spacial_id}&switch_status={switch_status}&code={code}'  # + Authority + Status
            ######################################################################
        else:
            call_back_url_melli = f'https://{url}/subscription/callback/melli/{tid}/?switch_status={switch_status}&code={code}'
            ######################################################################
            call_back_url_mellat = f'https://{url}/subscription/callback/mellat/{tid}/?switch_status={switch_status}&code={code}'
            ######################################################################
            call_back_url_zarinpall = f'https://{url}/subscription/callback/zarinpal/?switch_status={switch_status}&code={code}'
            ######################################################################
        ref_id = ''
        if payment_way == 'melli':
            tracking_code = int(str(uuid.uuid4().int)[-1 * 16:])
            # data = PaymentRequestInput(amount=1000, order_id=tracking_code, return_url=call_back_url_melli,
            #                            additional_data='', mobile="09123456789")

            data = PaymentRequestInput(amount=invoice_price, order_id=tracking_code, return_url=call_back_url_melli,
                                       additional_data='', mobile=request.user.username)

            URL = 'https://sadad.shaparak.ir/api/v0/Request/PaymentRequest'
            json_data = data.to_json()
            response = requests.post(URL, data=json_data, headers={'Content-Type': 'application/json'})
            res_con = json.loads(response.content)
            token = json.loads(response.content)["Token"]
            transaction = Transaction.objects.create(user=request.user, order_id=tid, ref_id=token,
                                                     subscription_plan=selected_plan)
            return redirect('https://sadad.shaparak.ir/Purchase?Token=' + token)
        ######################################################################
        elif payment_way == 'mellat':
            payment_url = pgw.get_payment_address()
            ref_id = pgw.request_pay_ref(order_id=tid, price=invoice_price * 10,
                                         call_back_address=call_back_url_mellat)
            transaction = Transaction.objects.create(user=request.user, order_id=tid, ref_id=ref_id,
                                                     subscription_plan=selected_plan)
            return render(request, 'pymellat.html', {'ref_id': ref_id})
        ######################################################################
        elif payment_way == 'zarinpal':
            description = tid
            email = request.user.email
            phone = "09121234567"
            ref_id = client.service.PaymentRequest(MERCHANT, invoice_price, description, email, phone,
                                                   call_back_url_zarinpall)
            if ref_id.Status == 100:
                transaction = Transaction.objects.create(user=request.user, order_id=tid, ref_id=ref_id.Authority,
                                                         subscription_plan=selected_plan)
                return redirect('https://www.zarinpal.com/pg/StartPay/' + str(ref_id.Authority))
            else:
                return redirect(reverse("Subscription"))
        else:
            pass
    return redirect(reverse("Subscription"))


def subscription_payment_callback_mellat_view(request, order_id):
    f = open("report.md", "w+")
    msg = '0'
    transaction = Transaction.objects.get(order_id=order_id)
    res_code = request.POST.get('ResCode')
    f.write(f"{res_code}\n{type(res_code)}\n")
    code = request.GET.get("code")
    ##############################################################################################
    if res_code == '0':
        sale_order_id = request.POST.get('saleOrderId')
        sale_reference_id = request.POST.get('SaleReferenceId')
        card_holder_info = request.POST.get('CardHolderInfo')
        transaction.card_holder_info = card_holder_info
        transaction.sales_reference_id = str(sale_reference_id)
        payment_verify_state, message = pgw.verify_payment(order_id=transaction.order_id,
                                                           ref_id=str(sale_reference_id))
        if payment_verify_state is True:
            transaction.status = 1
            transaction.save()
            payment_settle_state, message = pgw.settle_payment(order_id=transaction.order_id,
                                                               ref_id=str(sale_reference_id))
            if payment_settle_state:
                transaction.status = 3
                transaction.save()
                try:
                    f.write(f"{transaction.user}\n")
                    chand_status_dis_code(transaction.user, request)
                    # get request and create a statuse of using discount code
                except Exception as e:
                    f.write(f"{e}\n")
                #############################################################################################
                f.write(f"{transaction.user}\n")
                if hasattr(transaction.user, 'SubscriptionPlan'):
                    Take_an_object_and_decide(request, transaction)  # S T S / S T V / V T V / V T S /
                else:
                    Subscription.objects.create(
                        user=transaction.user,
                        plan=transaction.subscription_plan,
                        end_date=timezone.localdate(timezone.now()) + timedelta(
                            transaction.subscription_plan.valid_days))
                msg = "1"
                f.write(f"success\n")
        else:
            f.write(f"status not 0\n")
            msg = '2'
            transaction.status = 2
            transaction.save()
    else:
        f.write(f"some thing went wrong...\n")
        msg = '2'
    return redirect(reverse('Subscription') + '?msg=' + msg + '&order=' + transaction.order_id)


def subscription_payment_callback_zarinpal_view(request):
    transaction = Transaction.objects.get(ref_id=request.GET['Authority'])
    if request.GET.get('Status') == 'OK':
        amount = transaction.subscription_plan.price  # check is ever use dis code
        code = request.GET.get("code")
        try:
            discount = Discount.objects.get_object_or_None_v2(code=code)
            if discount is not None:
                discount_percent, money = check_money_with_discount(code=code, price=amount)
                amount = money
        except:
            pass
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)

        if result.Status == 100:
            transaction.sales_reference_id = str(result.RefID)
            transaction.card_holder_info = '----'
            transaction.status = 3
            transaction.save()
            #######################################################################################
            try:
                chand_status_dis_code(transaction.user, request)
                # get request and create a statuse of using discount code
            except:
                pass
            if hasattr(transaction.user, 'SubscriptionPlan'):
                Take_an_object_and_decide(request, transaction)  # S T S / S T V / V T V / V T S /
            else:
                Subscription.objects.create(
                    user=transaction.user,
                    plan=transaction.subscription_plan,
                    end_date=timezone.localdate(timezone.now()) + timedelta(transaction.subscription_plan.valid_days))
            msg = "1"
            return redirect(reverse('Subscription') + '?msg=' + msg + '&order=' + transaction.order_id)
            #######################################################################################
        elif result.Status == 101:
            transaction.status = 3
            transaction.save()
            if hasattr(transaction.user, 'SubscriptionPlan'):
                Take_an_object_and_decide(request, transaction)  # S T S / S T V / V T V / V T S /
            else:
                Subscription.objects.create(
                    user=transaction.user,
                    plan=transaction.subscription_plan,
                    end_date=timezone.localdate(timezone.now()) + timedelta(transaction.subscription_plan.valid_days))
            msg = '1'
            return redirect(reverse('Subscription') + '?msg=' + msg + '&order=' + transaction.order_id)
        else:
            transaction.status = 2
            transaction.save()
            msg = '2'
    else:
        msg = '2'
    return redirect(reverse('Subscription') + '?msg=' + msg + '&order=' + transaction.order_id)


def subscription_payment_callback_melli_view(request, order_id):
    msg = '0'
    transaction = Transaction.objects.get(order_id=order_id)
    res_code = request.POST.get('ResCode')
    if res_code == '0':
        sign_data = encrypt_des3_token(transaction.ref_id)
        data = {
            'Token': transaction.ref_id,
            'SignData': sign_data,
        }
        URL = 'https://sadad.shaparak.ir/api/v0/Advice/Verify'
        response = requests.post(URL, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        res_data = json.loads(response.content)
        res_code = res_data['ResCode']
        if res_code == '0':
            transaction.sales_reference_id = str(res_data['RetrivalRefNo'])
            transaction.card_holder_info = '----'
            transaction.status = 3
            transaction.save()
            try:
                chand_status_dis_code(transaction.user, request)
                # get request and create a statuse of using discount code
            except:
                pass
            #############################################################################################

            if hasattr(transaction.user, 'SubscriptionPlan'):
                Take_an_object_and_decide(request, transaction)  # S T S / S T V / V T V / V T S /
            else:
                Subscription.objects.create(
                    user=transaction.user,
                    plan=transaction.subscription_plan,
                    end_date=timezone.localdate(timezone.now()) + timedelta(transaction.subscription_plan.valid_days))
            msg = "1"
        else:
            msg = '2'
            transaction.status = 2
            transaction.save()
    else:
        msg = '2'
    return redirect(reverse('Subscription') + '?msg=' + msg + '&order=' + transaction.order_id)
