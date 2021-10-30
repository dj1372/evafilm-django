from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login
from django.contrib.auth import authenticate

from .models import SubscriptionPlan
from .tasks import send_code, r
import random
from .tasks import validate_phone
from datetime import datetime
from django.utils import timezone
from django.contrib.sessions.models import Session
from payments.models import Transaction
from invitor.models import invitor_code, generated_invitor_code

from django.contrib.auth import get_user_model

User = get_user_model()


def generate_otp():
    code = str(random.randrange(52889, 99889))
    return code


def generate_api_token():
    code = str(random.randrange(528890, 998890)) + str(random.randrange(528890, 998890)) + \
           str(random.randrange(528890, 998890))
    return code


def login_view(request):
    if request.method == 'POST':
        username = validate_phone(request.POST.get('phone'))
        password = request.POST.get('password')
        if User.objects.filter(username=username).count() == 0:

            alert = 'نام کاربری وجود ندارد. لطفا ابتدا ثبت نام کنید.'
            return render(request, 'account/login_phone.html', {'phone': request.POST.get('phone'),
                                                                'password': request.POST.get('password'),
                                                                'message': alert})
        else:
            if User.objects.get(username=username).is_active:
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('Home')
                else:
                    alert = 'خطا, گذرواژه اشتباه است. لطفا دوباره سعی کنید.'
                    return render(request, 'account/login_phone.html', {'phone': request.POST.get('phone'),
                                                                        'password': request.POST.get('password'),
                                                                        'message': alert})
            else:
                alert = 'خطا،  لطفا ابتدا ثبت نام کنید.'
                return render(request, 'account/login_phone.html', {'phone': request.POST.get('phone'),
                                                                    'password': request.POST.get('password'),
                                                                    'message': alert})
    else:  # request.method == 'GET':   # if user already logged in
        if not request.user.is_authenticated:
            return render(request, 'account/login_phone.html', {})
        else:
            return redirect('Home')


def signup_view(request):
    if request.method == 'POST':
        username = validate_phone(request.POST.get('mobile'))
        if User.objects.filter(username=username).count() == 0:
            user = User.objects.create(username=username, is_active=False)
        else:
            user = User.objects.get(username=username)
            if user.is_active:
                return render(request, 'account/login.html', {'mess': 'این شماره قبلا ثبت نام شده است', })
            else:
                pass
        if request.POST.get('state') == '1':  # Signup form LEVEL
            if not r.exists(username):
                code = generate_otp()
                raw_password = code
                user.set_password(raw_password)
                print('send')
                send_code(username=username, code=code)
                # send_code.delay(username=username, code=code)
            user.save()
            return render(request, 'account/verification.html',
                          {'mobile': username,
                           'state': 2,
                           })
        elif request.POST.get('state') == '2':  # SMS verification LEVEL
            if request.POST.get('vcode') == '':  # Resend Code
                if not r.exists(username):
                    code = generate_otp()
                    user.set_password(code)
                    user.save()
                    send_code(username=username, code=code)
                    # send_code.delay(username=username, code=code)
                    alert = 'کد فعالسازی مجددا ارسال شد.'
                    return render(request, 'account/verification.html',
                                  {'mobile': username,
                                   'state': 2,
                                   'alert': alert,
                                   })
                else:
                    alert = 'خطا, درخواست تکراری است. لطفا دو دقیقه دیگر مجددا تلاش کنید.'
                    return render(request, 'account/verification.html',
                                  {'mobile': username,
                                   'state': 2,
                                   'alert': alert,
                                   })
            else:
                code = request.POST.get('vcode')
                if r.exists(username):
                    if r.get(username).decode("utf-8") == code:
                        # user.is_active = True
                        # user.save()
                        user.Profile.api_token = generate_api_token()
                        user.Profile.save()
                        if user.check_password(code):
                            return render(request, 'account/register.html',
                                          {'mobile': username,
                                           'state': 3,
                                           })
                        else:
                            alert = 'خطا, کد وارد شده اشتباه است.لطفا دوباره سعی کنید.'
                            return render(request, 'account/verification.html',
                                          {'alert': alert,
                                           'mobile': username,
                                           'state': 2,
                                           })
                        # user = authenticate(username=username, password=code)
                        # if user is not None:
                        #     login(request, user)
                        #     return redirect('Home')
                        # else:
                        #     alert = 'خطا, کد وارد شده اشتباه است.لطفا دوباره سعی کنید.'
                        #     return render(request, 'account/verification.html',
                        #                   {'alert': alert,
                        #                    'mobile': username,
                        #                    'state': 2,
                        #                    })
                    else:
                        alert = 'خطا, کد وارد شده اشتباه است.لطفا دوباره سعی کنید.'
                        return render(request, 'account/verification.html',
                                      {'alert': alert,
                                       'mobile': username,
                                       'state': 2,
                                       })
                else:
                    code = generate_otp()
                    send_code(username=username, code=code)
                    # send_code.delay(username=username, code=code)
                    code = generate_otp()
                    user.set_password(code)
                    user.save()
                    alert = 'یک کد فعالسازی برای شماره موبایل شما ارسال شد. لطفا اینجا وارد کنید.'
                    return render(request, 'account/verification.html',
                                  {'alert': alert,
                                   'state': 2,
                                   })
        elif request.POST.get('state') == '3':  # Signup form LEVEL

            # if not r.exists(username):
            first_name = request.POST.get('f_name')
            last_name = request.POST.get('l_name')
            email = request.POST.get('E_user')
            password = request.POST.get('pass')
            repassword = request.POST.get('repass')
            invitation_code = request.POST.get('code')
            context = {}  # فعلا کاری نمی کند
            if password != repassword:
                alert = 'خطا, تکرار گذرواژه اشتباه است.لطفا دوباره سعی کنید.'
                return render(request, 'account/register.html',
                              {'alert': alert,
                               'mobile': username,
                               'state': 3,
                               'first_name': first_name,
                               'last_name': last_name,
                               'email': email,
                               })
            else:
                user.is_active = True
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.set_password(password)
                user.save()
                user = authenticate(username=username, password=password)
                if user is not None:
                    print('user ok')
                    if user.is_active:
                        print('user ok2')
                        login(request, user)
                        if invitation_code:
                            invitor_instance = invitor_code.objects.filter(code=str(invitation_code))
                            g_invitor = generated_invitor_code.objects.filter(code=str(invitation_code))
                            if invitor_instance.exists() and request.user.is_authenticated:
                                invitor_instance = invitor_instance.first()
                                if not invitor_instance.invited_users.filter(username=request.user.username).exists():
                                    invitor_instance.invitations += 1
                                    invitor_instance.invited_users.add(request.user)
                                    invitor_instance.save()
                                    context.update({'status': 200})
                            elif g_invitor.exists() and request.user.is_authenticated:
                                g_invitor = g_invitor.first()
                                if not g_invitor.invited_users.filter(username=request.user.username).exists():
                                    g_invitor.invitations += 1
                                    g_invitor.invited_users.add(request.user)
                                    g_invitor.save()
                                    context.update({'status': 200})
                            else:
                                context.update({'status': 401})
                        else:
                            context.update({'status': 401})
                        return redirect('Home')
        # else:
        #     print('123')

        # user = authenticate(username=username, password=code)
        # if user is not None:
        #     if user.is_active:
        #         login(request, user)
        #         return redirect('Home')
        #     else:
        #         code = generate_otp()
        #         send_code.delay(username=username, code=code)
        #         alert = 'یک کد فعالسازی برای شماره موبایل شما ارسال شد. لطفا اینجا وارد کنید.'
        #         return render(request, 'account/verification.html',
        #                       {'alert': alert,
        #                        })
    else:  # request.method == 'GET':   # if user already logged in
        if not request.user.is_authenticated:
            return render(request, 'account/signup.html', {'state': 1,
                                                           })
        else:
            return redirect('Home')

    # return render(request, 'account/signup.html', {'state': 1,
    #                                                })


def profile(request):
    if not request.user.is_authenticated:
        query_params = ''
        if not request.META.get('HTTP_REFERER') is None:
            query_params += '?r=' + request.META.get('HTTP_REFERER')
            return redirect(reverse('Login') + query_params)
        else:
            return redirect('Login')

    if request.method == 'POST':
        profile = request.user.Profile
        profile.nick_name = request.POST.get('nick_name')
        profile.age = request.POST.get('age')
        profile.save()
        return render(request, 'profile.html', {'profile': profile, 'msg': 1})
    else:
        if request.user.is_authenticated:
            profile = request.user.Profile
            subscription_plans = SubscriptionPlan.objects.exclude(price=0).order_by('name')
            if hasattr(request.user, 'SubscriptionPlan'):
                user_subscription_valid_days = (request.user.SubscriptionPlan.end_date - datetime.now().date()).days
            else:
                user_subscription_valid_days = -1
            return render(request, 'profile.html', {'profile': profile,
                                                    'subscription_plans': subscription_plans,
                                                    'user_subscription_valid_days': user_subscription_valid_days})
        else:
            return redirect('Login')


# profile censor on off

def profile_censor_change(request):
    if not request.user.is_authenticated:
        return redirect('Login')

    if request.method == 'POST':
        censor = request.POST.get('censor')
        profile = request.user.Profile
        if censor == '0':
            profile.is_censor_on = False
        else:
            profile.is_censor_on = True

        profile.save()
        profile = request.user.Profile
        subscription_plans = SubscriptionPlan.objects.exclude(price=0).order_by('name')
        if hasattr(request.user, 'SubscriptionPlan'):
            user_subscription_valid_days = (request.user.SubscriptionPlan.end_date - datetime.now().date()).days
        else:
            user_subscription_valid_days = -1
        return render(request, 'profile.html', {'profile': profile,
                                                'subscription_plans': subscription_plans,
                                                'user_subscription_valid_days': user_subscription_valid_days})
    else:
        return redirect('Profile')


def edit_profile(request):
    if not request.user.is_authenticated:
        query_params = ''
        if not request.META.get('HTTP_REFERER') is None:
            query_params += '?r=' + request.META.get('HTTP_REFERER')
            return redirect(reverse('Login') + query_params)
        else:
            return redirect('Login')

    if request.method == 'POST':
        profile = request.user.Profile
        profile.nick_name = request.POST.get('nick_name')
        profile.age = request.POST.get('age')
        profile.save()
        return render(request, 'edit_profile.html', {'profile': profile, 'msg': 1})
    else:
        if request.user.is_authenticated:
            profile = request.user.Profile
            return render(request, 'edit_profile.html', {'profile': profile})
        else:
            return redirect('Login')


def change_name(request):
    if not request.user.is_authenticated:
        query_params = ''
        if not request.META.get('HTTP_REFERER') is None:
            query_params += '?r=' + request.META.get('HTTP_REFERER')
            return redirect(reverse('Login') + query_params)
        else:
            return redirect('Login')

    if request.method == 'POST':
        profile = request.user.Profile
        user = request.user
        user.first_name = request.POST.get('f_name')
        user.last_name = request.POST.get('l_name')
        user.save()
        profile.save()
        return redirect('Profile')
    else:
        if request.user.is_authenticated:
            profile = request.user.Profile
            return render(request, 'change-name.html', {'profile': profile})
        else:
            return redirect('Login')


def change_email(request):
    if not request.user.is_authenticated:
        query_params = ''
        if not request.META.get('HTTP_REFERER') is None:
            query_params += '?r=' + request.META.get('HTTP_REFERER')
            return redirect(reverse('Login') + query_params)
        else:
            return redirect('Login')

    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email')
        user.save()
        return redirect('Profile')
    else:
        if request.user.is_authenticated:
            profile = request.user.Profile
            return render(request, 'change-email.html', {'profile': profile})
        else:
            return redirect('Login')


def change_pass(request):
    if not request.user.is_authenticated:
        query_params = ''
        if not request.META.get('HTTP_REFERER') is None:
            query_params += '?r=' + request.META.get('HTTP_REFERER')
            return redirect(reverse('Login') + query_params)
        else:
            return redirect('Login')

    if request.method == 'POST':
        unencrypted_password = request.POST.get('npsw')
        profile = request.user.Profile
        user = request.user
        user.first_name = request.user.first_name
        user.last_name = request.user.last_name
        user.set_password(unencrypted_password)  # replace with your real password
        user.save()

        # return redirect('Profile')
        return render(request, 'change_pass.html', {'profile': profile, 'msg': 1})
    else:
        if request.user.is_authenticated:
            profile = request.user.Profile
            return render(request, 'change_pass.html', {'profile': profile})
        else:
            return redirect('Login')


def order_list(request):
    orders = Transaction.objects.filter(user=request.user).filter(status=3)
    return render(request, 'orderlist.html', {'orders': orders})


def forget_password_view(request):
    if request.method == 'POST':
        username = validate_phone(request.POST.get('mobile'))
        if User.objects.filter(username=username).count() == 0:
            alert = 'نام کاربری وجود ندارد.'
            return render(request, 'account/forget_password.html',
                          {'alert': alert, })
        else:
            if User.objects.get(username=username).is_active:
                user = User.objects.get(username=username)
            else:
                alert = 'کاربر ثبت نام نشده است. مراحل ثبت نام را تکمیل نمایید.'
                return render(request, 'account/forget_password.html',
                              {'alert': alert, })

        if request.POST.get('state') == '1':  # Signup form LEVEL
            if not r.exists(username):
                code = generate_otp()
                raw_password = code
                user.set_password(raw_password)
                send_code(username=username, code=code)
                # send_code.delay(username=username, code=code)
            user.save()
            return render(request, 'account/verification.html',
                          {'mobile': username,
                           'state': 2,
                           })
        elif request.POST.get('state') == '2':  # SMS verification LEVEL
            if request.POST.get('vcode') == '':  # Resend Code
                if not r.exists(username):
                    code = generate_otp()
                    user.set_password(code)
                    user.save()
                    send_code(username=username, code=code)
                    # send_code.delay(username=username, code=code)
                    alert = 'کد فعالسازی مجددا ارسال شد.'
                    return render(request, 'account/verification.html',
                                  {'mobile': username,
                                   'state': 2,
                                   'alert': alert,
                                   })
                else:
                    alert = 'خطا, درخواست تکراری است. لطفا دو دقیقه دیگر مجددا تلاش کنید.'
                    return render(request, 'account/verification.html',
                                  {'mobile': username,
                                   'state': 2,
                                   'alert': alert,
                                   })
            else:
                code = request.POST.get('vcode')
                if r.exists(username):
                    if r.get(username).decode("utf-8") == code:
                        # user.is_active = True
                        # user.save()
                        user.Profile.api_token = generate_api_token()
                        user.Profile.save()
                        if user.check_password(code):
                            return render(request, 'account/reset_password.html',
                                          {'mobile': username,
                                           'state': 3,
                                           })
                        else:
                            alert = 'خطا, کد وارد شده اشتباه است.لطفا دوباره سعی کنید.'
                            return render(request, 'account/verification.html',
                                          {'alert': alert,
                                           'mobile': username,
                                           'state': 2,
                                           })
                        # user = authenticate(username=username, password=code)
                        # if user is not None:
                        #     login(request, user)
                        #     return redirect('Home')
                        # else:
                        #     alert = 'خطا, کد وارد شده اشتباه است.لطفا دوباره سعی کنید.'
                        #     return render(request, 'account/verification.html',
                        #                   {'alert': alert,
                        #                    'mobile': username,
                        #                    'state': 2,
                        #                    })
                    else:
                        alert = 'خطا, کد وارد شده اشتباه است.لطفا دوباره سعی کنید.'
                        return render(request, 'account/verification.html',
                                      {'alert': alert,
                                       'mobile': username,
                                       'state': 2,
                                       })
                else:
                    code = generate_otp()
                    send_code(username=username, code=code)
                    # send_code.delay(username=username, code=code)
                    code = generate_otp()
                    user.set_password(code)
                    user.save()
                    alert = 'یک کد فعالسازی برای شماره موبایل شما ارسال شد. لطفا اینجا وارد کنید.'
                    return render(request, 'account/verification.html',
                                  {'alert': alert,
                                   'state': 2,
                                   })
        elif request.POST.get('state') == '3':  # Signup form LEVEL

            # if not r.exists(username):
            password = request.POST.get('pass')
            repassword = request.POST.get('repass')

            if password != repassword:
                alert = 'خطا, تکرار گذرواژه اشتباه است.لطفا دوباره سعی کنید.'
                return render(request, 'account/reset_password.html',
                              {'alert': alert,
                               'mobile': username,
                               'state': 3,
                               })
            else:
                user.set_password(password)
                user.save()
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('Home')

    else:  # request.method == 'GET':   # if user already logged in
        if not request.user.is_authenticated:
            return render(request, 'account/forget_password.html', {'state': 1, })
        else:
            return redirect('Home')

    return render(request, 'account/forget_password.html', {'state': 1, })
