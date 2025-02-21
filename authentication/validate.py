import requests
from django.conf import settings

def introspect_token(token):
    introspection_url = settings.INTROSPECTION_URL
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET

    response = requests.post(
        introspection_url,
        data={'token': token},
        auth=(client_id, client_secret)
    )

    if response.status_code == 200:
        token_info = response.json()
        print(token_info)
        return token_info.get('active', False)
    return False
