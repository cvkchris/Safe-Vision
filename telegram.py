import requests

def send_telegram_image(image_file):
    bot_token = '<your telegram bot token>'
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    data = {
        'chat_id': '<your telegram chat-id>'
    }
    files = {
        'photo': image_file
    }
    response = requests.post(url, data=data, files=files)
    return response.json()

def send_telegram_message():
    bot_token = '<your telegram bot token>'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': '<your telegram chat-id>',
        'text': 'violence-detected'
    }
    response = requests.post(url, data=data)
    return response.json()

