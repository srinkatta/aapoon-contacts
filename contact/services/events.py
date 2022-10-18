import json
import threading
import uuid
from datetime import datetime

import boto3

from aapooncontact import settings
from contact.helpers.utils import check_friend_status


class ContactsEvents:
    """Encapsulates an Amazon DynamoDB table of contact data."""

    def __init__(self):
        self.AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
        self.client = None
        self.event = None
        self.initialize()

    def initialize(self):
        self.client = boto3.client(
            "events",
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name="us-east-1",
        )
        return

    def create_event(self, data):
        """
        Create an event in Event Bridge
        """
        try:
            print("Event Creation")
            response = self.client.put_events(
                Entries=[
                    {
                        "Time": datetime.now(),
                        "Source": "contacts.service",
                        "DetailType": "ContactsSyncEvent",
                        "Detail": json.dumps(data),
                    },
                ],
            )
        except Exception as err:
            print(
                "Couldn't add event to events. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
