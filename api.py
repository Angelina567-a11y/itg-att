import requests

API_URL = "https://v6.exchangerate-api.com/v6/your-api-key/latest/USD"  # замените на ваш ключ

def get_rates():
    try:
        response = requests.get(API_URL)
        data = response.json()
        if data['result'] == 'success':
            return data['conversion_rates']
        else:
            return None
    except:
        return None