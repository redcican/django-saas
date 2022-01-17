from twilio.rest import Client
from django.conf import settings

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
phone_number = settings.TWILIO_PHONE_NUMBER
client = Client(account_sid, auth_token)

def send_sms(to_number, tpl, code):
    """send sms to the users for verfiying the phone number
    
    Args:
        to_number ([int]): the user's phone number
        tpl ([str]): the template of the sms [register, login]
        code ([str]): the verification code
    """
    body = ''
    if tpl == 'register':
        body = f'Your register verification code is {code}'
    else:
        body = f'Your login verification code is {code}'
    message = client.messages \
        .create(
            body=body,
            from_=phone_number,
            to=to_number
         )
    message_out = client.messages(message.sid).fetch()
    return message_out
    
