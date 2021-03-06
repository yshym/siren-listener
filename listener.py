#!/usr/bin/env python3

import asyncio
from datetime import datetime
from decouple import config, Csv
from telethon import TelegramClient, events
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioClient


# telethon credentials
telegram_api_id = config("TELEGRAM_API_ID")
telegram_api_hash = config("TELEGRAM_API_HASH")

telegram_client = TelegramClient(
    "some-session", telegram_api_id, telegram_api_hash
)
channels = config("TELEGRAM_CHANNELS", cast=Csv(str))
channel_links = [f"https://t.me/{chan}" for chan in channels]

# twilio credentials
twilio_sid = config("TWILIO_SID")
twilio_auth_token = config("TWILIO_AUTH_TOKEN")

twilio_from_phone_number = config("TWILIO_FROM_PHONE_NUMBER")
twilio_to_phone_number = config("TWILIO_TO_PHONE_NUMBER")
twilio_client = TwilioClient(twilio_sid, twilio_auth_token)

last_message_time = None
TIMEOUT_SECONDS = 300

print(f"Connecting to channels {channels}")


@telegram_client.on(
    events.NewMessage(chats=channel_links, pattern=r"(?i).*(тривога|сирена)")
)
async def handler(event):
    global last_message_time
    text = event.message.message
    print(f"telegram: message caught - '{text}'")
    print(f"bot: last message time is {last_message_time}")
    time_now = datetime.now()
    if (
        last_message_time
        and (time_now - last_message_time).seconds < TIMEOUT_SECONDS
    ):
        last_message_time = time_now
        print(
            f"bot: last message was cauth less than {TIMEOUT_SECONDS} seconds ago"
        )
        return
    else:
        last_message_time = time_now
    try:
        twilio_client.calls.create(
            to=twilio_to_phone_number,
            from_=twilio_from_phone_number,
            url="http://demo.twilio.com/docs/voice.xml",
        )
    except TwilioRestException as err:
        print(f"twilio: call failed\n{err}")


telegram_client.start()
telegram_client.run_until_disconnected()
