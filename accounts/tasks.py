from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery import shared_task
import redis
import requests
import json

from django.contrib.auth import get_user_model

User = get_user_model()

r = redis.Redis(host='localhost', port=6379, db=0)


def validate_phone(username):
    if username[0] == '0':
        phone = username[1:]
    else:
        phone = username
    return phone


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


# @shared_task
def send_code(username, code):
    phone = validate_phone(username)
    token = get_sms_token()
    headers = {"Content-Type": "application/json", "x-sms-ir-secure-token": token}
    data = {"ParameterArray": [
        {"Parameter": "verification_code", "ParameterValue": code}
    ],
        "Mobile": phone,
        "TemplateId": "47805"
    }
    response = requests.post("https://restfulsms.com/api/ultrafastsend", data=json.dumps(data), headers=headers)

    r.set(username, code)
    r.expire(username, 120)

    json_data = json.loads(response.text)
    if json_data["IsSuccessful"]:
        return True
    else:
        return False
