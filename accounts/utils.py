from django.core.mail import EmailMessage
from django.conf import settings
import jwt


class Util:
    @staticmethod
    def send_otp_vai_email(otp,email):
        data = {
            'to': email,
            'subject': 'Verify your email address',
            'body': f'This mail is sent to you because you have just signed up for Digital Museum \n \n Your otp is: \n\n {otp}'
        }
        # Send email
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to']],
        )
        email.send()

    @staticmethod
    def jwt_encode(payload):
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def jwt_decode(token):
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        