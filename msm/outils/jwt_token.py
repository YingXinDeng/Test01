import jwt
import datetime
from django.conf import settings


def creat_token(payload, timeout=60):

    salt = settings.SECRET_KEY
    # print("salt : ", salt)
    header = {
        'alg': 'HS256',
        "typ": "JWT"
    }
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)  # 超时时间
    # token = toke.encode('utf-8').decode('utf-8')
    token = jwt.encode(payload=payload, key=salt, headers=header)
    # print(token)
    return token


