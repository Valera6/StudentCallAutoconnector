import json

# <teams module talking>
def schedule_teams(mail, password, time, message):
    with open(r"Teams\config.json", "r") as f:
        config = json.load(f)
    print(config)
    config['email'] = mail
    config['password'] = password
    config['run_at_time'] = time
    config['join_message'] = message

    with open(r'Teams\config.json', 'w') as f:
        json.dump(config, f, indent=4)

    from Teams import auto_joiner
#------------------------------------------------------------

# <zoom module talking>
def schedule_zoom(mail, password, time, meeting_id, meeting_password):
    from zoomus import ZoomClient
    from zoomus import ZoomAPIException

    zoom_client = ZoomClient(email=mail, password=password)

    meeting_id = '1234567890'
    meeting_password = 'your_meeting_password'

    try:
        access_token = zoom_client.user.get(access_token=True)['access_token']
        zoom_client = ZoomClient(access_token=access_token)
#---------------------------------------------------------- 

# <discord module talking>

# <google meets talking>

schedule_teams('v79166789533@gmail.com', 'Valera05!', '23:59', 'Здравствуйте')
