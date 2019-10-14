import urllib.request
import os
import json
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import time

import messages

# Configurations for pushing to LINE Messaging API
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
LINE_USER_ID = os.getenv('LINE_USER_ID', None)
global TARGET_ID
TARGET_ID = LINE_USER_ID

URL = 'https://api.line.me/v2/bot/message/push'
HEADERS = {
    'User-Agent': 'Mozilla',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'.format(LINE_CHANNEL_ACCESS_TOKEN)
}
RECONCILATION_PERIOD_SEC = 60


def pushing_messages(text_message):
    DATA = json.dumps(text_message).encode('utf-8')
    req = urllib.request.Request(
        url=URL,
        headers=HEADERS,
        data=DATA
    )

    with urllib.request.urlopen(req) as res:
        body = res.read()
    if res.getcode() == 200:
        print('POST success, you might get push notifications soon.')
    else:
        print('Return-Code: {} | Failed to POST ...'.format(res.getcode()))

    print('Response body : \n{}'.format(json.loads(body.decode('utf-8'))))


def get_message_body(t):
    msg = ''
    candidate_times = [m.get('time') for m in messages.msg]

    if t.strftime('%H-%M') in candidate_times:
        index = candidate_times.index(t.strftime('%H-%M'))
        msg = messages.msg[index]['text']

    return msg

if __name__ == '__main__':
    while True:
        print('Starting closed loop, checking time...')
        time.sleep(RECONCILATION_PERIOD_SEC)
        now = datetime.now()
        if os.getenv('TZ') != 'Asia/Tokyo':
            tz = timezone(timedelta(hours=9), 'JST')
            now = datetime.now(tz)

        push_text = get_message_body(t=now)

        if push_text == '':
            print('>>> Current Time : {} | It is not time to remind. nothing to do.'.format(now))
            continue
        else:
            print('>>> Current Time : {} | Time to remind. Run push-notification.'.format(now))
            push_data = {
                'to': TARGET_ID,
                'messages': [
                    {
                        'type': 'text',
                        'text': push_text
                    }
                ]
            }
            pushing_messages(push_data)

