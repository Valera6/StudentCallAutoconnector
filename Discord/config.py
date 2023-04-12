from urllib import parse


TOKEN = 'MTA4MDUxNDE2ODU5MzA3MjE3MQ.GhJ9MX.XtSUc1Cd5Z0AKK5BYQld9haLM6YcCjMm6fTNFo'
CLIENT_ID = '1080514168593072171'
CLIENT_SECRET = 'BBfXvNGeSLIdPNpI5WF1AL83VB6VhNEb'
REDIRECT_URI = 'http://localhost:5000/oauth/callback'
OAUTH_URL = f'https://discord.com/api/oauth2/authorize?client_id=1080514168593072171&redirect_uri={parse.quote(REDIRECT_URI)}&response_type=code&scope=identify%20guilds' #'%20voice%20rpc.voice.write'
