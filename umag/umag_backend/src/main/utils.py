import requests
from requests.auth import HTTPBasicAuth
from .models import Settings

url = f'{Settings.objects.first().jira_url}/rest/api/3/field'

# Делаем запрос к API
response = requests.get(url, auth=HTTPBasicAuth(Settings.objects.first().username, Settings.objects.first().api_token))


def get_field_id():
    # Проверяем ответ
    if response.status_code == 200:
        fields = response.json()
        for field in fields:
            print(field['name'])
            if field['name'] == Settings.objects.first().telegram_filed: return field['id']
    else:
        print("Failed to retrieve fields: ", response.status_code)