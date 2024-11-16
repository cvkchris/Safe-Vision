import requests

def send_telegram_image(image_file):
    bot_token = '7465229273:AAGAQllb6Z9pu4KjId3WGhsCTE3ywlVjLlM'
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    data = {
        'chat_id': '1398254880'
    }
    files = {
        'photo': image_file
    }
    response = requests.post(url, data=data, files=files)
    return response.json()

def send_telegram_message():
    bot_token = '7465229273:AAGAQllb6Z9pu4KjId3WGhsCTE3ywlVjLlM'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': '1398254880',
        'text': 'violence-detected'
    }
    response = requests.post(url, data=data)
    return response.json()

