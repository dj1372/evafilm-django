from extensions import jalali
from django.utils import timezone

from django.conf import settings

from celery import Celery
from celery import shared_task

import requests, json, redis

r = redis.Redis(host='localhost', port=6379, db=0)


def get_sms_token():
    if r.exists('sms_token'):
        token = r.get('sms_token')
    else:
        data = {
            'UserApiKey': 'f5d726a88e520952f5d26a9',
            'SecretKey': 'awukvhsvswvriRHRhwuhf498849y938hfiosn'
        }
        response = requests.post('https://restfulsms.com/api/token', data)
        json_data = json.loads(response.text)
        token = json_data["TokenKey"]
        if token is not None:
            r.set('sms_token', token)
            r.expire('sms_token', 1500)
    return token


def my_send_sms(message, phone):

    token = get_sms_token()
    headers = {
        "Content-Type": "application/json",
        "x-sms-ir-secure-token": token
    }
    data = {
        "ParameterArray": [{
            "Parameter": "verification_code",
            "ParameterValue": message
        }],
        "Mobile":
        phone,
        "TemplateId":
        "47805"
    }

    response = requests.post("https://restfulsms.com/api/ultrafastsend",
                             data=json.dumps(data),
                             headers=headers)

    json_data = json.loads(response.text)
    if json_data["IsSuccessful"]:
        return True
    else:
        return False


from django.core.mail import send_mail as send
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class Email:
    @staticmethod
    def send_mail(subject, to, template, context):
        html_message = render_to_string(template, context)
        message = strip_tags(html_message)
        send(subject, message, None, to, html_message=html_message)


def persian_numbers_converter(string):
    numbers = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹",
    }

    for e, p in numbers.items():
        string = string.replace(e, p)

    return string


def jalali_converter(time):
    time = timezone.localtime(time)
    jmonth = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ]
    time_to_str = f"{time.year},{time.month},{time.day}"
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()

    output = f"{time_to_tuple[2]} {jmonth[time_to_tuple[1]-1]} {time_to_tuple[0]} ، ساعت  \
	{time.hour}:{time.minute}"

    return persian_numbers_converter(output)
