import json
import threading
import uuid
from datetime import datetime

import boto3

from contact_service import settings
from contact.helpers.utils import check_friend_status


class ContactsEvents:
    """Encapsulates an Amazon DynamoDB table of contact data."""

    def __init__(self):
        self.AWS_ACCESS_KEY_ID = settings.EVENT_AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = settings.EVENT_AWS_SECRET_ACCESS_KEY
        self.client = None
        self.event = None
        self.initialize()

    def initialize(self):
        self.client = boto3.client(
            "events",
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_EVENTBRIDGE_REGION,
        )
        return

    def create_event(self, data):
        """
        Create an event in Event Bridge
        """
        try:
            print("Event Creation")
            print(data)
            fmt = "%Y-%m-%dT%H:%M:%SZ"
            response = self.client.put_events(
                Entries=[
                    {
                        "EventBusName": settings.EVENT_BUS_NAME,
                        "Time": str(datetime.now(tz=timezone.utc).strftime(fmt)),
                        "Source": "contacts.service",
                        "DetailType": "ContactsSyncEvent",
                        "Detail": json.dumps(data),
                    }
                ],
            )
            print(response)
        except Exception as err:
            print(
                "Couldn't add event to events. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
