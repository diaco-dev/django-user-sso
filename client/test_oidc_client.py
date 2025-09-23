# import requests
#
# TOKEN_URL = "http://localhost:8000/oidc/token/"
# CLIENT_ID = "873033"
# CLIENT_SECRET = "58241041c20bd194c14b85a4a0a9af4ac6ff8552e1a2ab6fd54b193c"
# REDIRECT_URI = "http://localhost:8001/oidc/callback/"
# AUTH_CODE = "CODE_FROM_BROWSER"
#
# data = {
#     "grant_type": "authorization_code",
#     "code": AUTH_CODE,
#     "redirect_uri": REDIRECT_URI,
#     "client_id": CLIENT_ID,
#     "client_secret": CLIENT_SECRET,
# }
#
# resp = requests.post(TOKEN_URL, data=data)
# tokens = resp.json()
# access_token = tokens.get("access_token")
#
# # Call internal API
# r = requests.get("http://localhost:8001/api/v1/core/internal/", headers={
#     "Authorization": f"Bearer {access_token}"
# })
# print(r.json())


import requests

CLIENT_API_URL = "http://localhost:8001/api/v1/core/internal/"
CLIENT_JWT = "ACCESS_TOKEN_FROM_CALLBACK"

r = requests.get(CLIENT_API_URL, headers={
    "Authorization": f"Bearer {CLIENT_JWT}"
})

print(r.status_code)
print(r.json())
