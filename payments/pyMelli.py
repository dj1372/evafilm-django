import base64
import uuid
import json
from Crypto.Cipher import DES3
# from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
import datetime

class PaymentRequestInput:

    # def __init__(self, merchant_id, terminal_id, amount, order_id, date, return_url, additional_data, mobile,
    #              ):
    def __init__(self, amount, order_id, return_url, additional_data, mobile):
        # Test
        # self.MerchantId = "000000140336964"
        # self.TerminalId = "24095674"

        self.MerchantId = "000000140336840"
        self.TerminalId = "24095425"
        self.Amount = amount
        self.OrderId = order_id
        self.LocalDateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ReturnUrl = return_url
        self.SignData = self.encrypt_request_payment_data(self.TerminalId, order_id, amount)
        self.AdditionalData = additional_data
        self.UserId = mobile

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


    def pad(self, text, pad_size=16):
        text_length = len(text)
        last_block_size = text_length % pad_size
        remaining_space = pad_size - last_block_size
        text = text + (remaining_space * chr(remaining_space))
        return text

    def encrypt_des3(self, text):
        # Test
        # secret_key_bytes = base64.b64decode("8v8AEee8YfZX+wwc1TzfShRgH3O9WOho")

        secret_key_bytes = base64.b64decode("TSAqzPh9Hg89lOXJaDR4mNhM1XxbztAV")
        text = self.pad(text, 8)
        cipher = DES3.new(secret_key_bytes, DES3.MODE_ECB)
        cipher_text = cipher.encrypt(str.encode(text))
        return base64.b64encode(cipher_text).decode("utf-8")

    def encrypt_request_payment_data(self, terminal_id, tracking_code, amount):
        text = terminal_id + ';' + str(tracking_code) + ';' + str(amount)
        sign_data = self.encrypt_des3(text)
        return sign_data

def pad(text, pad_size=16):
    text_length = len(text)
    last_block_size = text_length % pad_size
    remaining_space = pad_size - last_block_size
    text = text + (remaining_space * chr(remaining_space))
    return text

def encrypt_des3_token(text):
    # Test
    # secret_key_bytes = base64.b64decode("8v8AEee8YfZX+wwc1TzfShRgH3O9WOho")

    secret_key_bytes = base64.b64decode("TSAqzPh9Hg89lOXJaDR4mNhM1XxbztAV")
    text = pad(text, 8)
    cipher = DES3.new(secret_key_bytes, DES3.MODE_ECB)
    cipher_text = cipher.encrypt(str.encode(text))
    return base64.b64encode(cipher_text).decode("utf-8")