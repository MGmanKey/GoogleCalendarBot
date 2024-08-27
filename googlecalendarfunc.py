from __future__ import print_function

import datetime
import os.path
import oauth2client

from oauth2client import client
from oauth2client import tools
from dateutil.parser import parse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = 'credentials.json'
APPLICATION_NAME = 'boteamapp'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


async def get_calendar_events(events_count: int = 5):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            return 3

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=events_count, singleEvents=True,
                                              orderBy='startTime').execute()
        print(events_result)
        events = events_result.get('items', [])

        if not events:
            return ['Нет предстоящих событий((']

        # Add to list next events
        event_list = []
        for event in events:
            startdt = parse(dict(event['start'])['dateTime'])
            startdt = str(startdt.date()) + ' ' + str(startdt.time())
            enddt = parse(dict(event['end'])['dateTime'])
            enddt = str(enddt.time())
            info = f"{event['summary']} \nвремя: {startdt}-{enddt} \nважность: {event['colorId']}"
            if 'description' in event:
                info += f"\n{event['description']}"
            if 'attachments' in event:
                for attach in event['attachments']:
                    info += f"\n{dict(attach)['title']}\n{dict(attach)['fileUrl']}"
            info += '\n'
            event_list.append(info)

        return event_list

    except HttpError as error:
        print('An error occurred: %s' % error)
        return 2
    except Exception as ex:
        print(ex)
        return 2


def insert_event(summary='eventFromBot', description=None, colorId=1,
                 start=datetime.datetime.now(), event_time=60,
                 attendees=None, reminders=None):
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('calendar', 'v3', credentials=creds)

        enddt = start + datetime.timedelta(minutes=event_time)
        event = {
            'summary': 'Google I/O 2015',
            'description': 'A chance to hear more about Google\'s developer products.',
            'start': {
                'dateTime': '2023-06-18T03:00:00+03:00',
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': '2023-06-18T03:30:00+03:00',
                'timeZone': 'Europe/Moscow',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created %s' % (event.get('htmlLink')))


insert_event()
