from rest_framework.response import Response
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def showMessage(data, code=200):
    return Response({'message': data, 'status': code}, status=code)

def showAll(data, code=200):
    return Response({'data': data, 'status': code}, status=code)

def showOne(data, code=200):
    return Response({'data': data, 'status': code}, status=code)

def errorMessage(data, code=400):
    return Response({'error': data, 'status': code}, status=code)

def oneToDict(data, include_keys, msg={}):
    # resultSet = {k: data[k] for k in set(list(data.keys())) - set(exclude_keys)}  # exclude_keys
    if not include_keys:
        return {**data, **msg}
    resultSet = {k: data[k] for k in data.keys() & include_keys}
    return {**resultSet, **msg}

def bulkToDict(data, include_keys, msg={}):
    for i in range(len(data)):
        data[i] = oneToDict(data[i], include_keys, msg)
    return data

def isValidParams(data, include_keys):
    if all(k in data for k in include_keys):
        return True
    return False

def sendEmail(data):
    from_email = settings.EMAIL_HOST_USER
    to_email = data['email']
    subject = data['subject']
    html_message = render_to_string('sign_up_email.html', {'token': data['verification_token']})
    plain_message = strip_tags(html_message)
    mail.send_mail(subject=subject, message=plain_message, from_email=from_email, recipient_list=[to_email], html_message=html_message)
