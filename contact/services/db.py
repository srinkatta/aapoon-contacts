import threading
import uuid
from datetime import datetime

import boto3

from aapooncontact import settings
from contact.helpers.utils import check_friend_status


class Contacts:
    """Encapsulates an Amazon DynamoDB table of contact data."""

    def __init__(self):
        self.AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
        self.client = None
        self.dynamodb = None
        self.initialize()
        self.table = self.dynamodb.Table(f"{settings.TABLE_NAME}")

    def initialize(self):
        self.client = boto3.client(
            "dynamodb",
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name="us-east-1",
        )
        self.dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name="us-east-1",
        )
        return

    def get_contact(self, data):
        contact = data["contact"]
        response = self.table.scan(
            FilterExpression="contact.contactCountryCode = :code AND contact.contactPhoneNumber = :ph AND userid = :userid",
            ExpressionAttributeValues={
                ":code": f"{contact['contactCountryCode']}",
                ":ph": f"{contact['contactPhoneNumber']}",
                ":userid": f"{data['userid']}",
            },
        )

        return response["Items"]

    def get_contact_with_old_phone_details(self, data):
        contact = data["contact"]
        response = self.table.scan(
            FilterExpression="contact.contactCountryCode = :code AND contact.contactPhoneNumber = :ph AND userid = :userid",
            ExpressionAttributeValues={
                ":code": f"{contact['contactOldCountryCode']}",
                ":ph": f"{contact['contactOldPhoneNumber']}",
                ":userid": f"{data['userid']}",
            },
        )

        return response["Items"]

    def list_contacts(self, user_id):
        response = self.table.scan(
            FilterExpression="contact.aapoonUser = :f AND userid = :uid",
            ExpressionAttributeValues={
                ":f": False,
                ":uid": user_id,
            },
        )
        return response["Items"]

    def add_contact(self, data):
        """
        Adds a contact to the table.
        """
        data["id"] = f"{uuid.uuid4()}"
        data["contact"]["aapoonUser"] = False
        data["contact"]["contactCreated"] = str(
            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        data["contact"]["contactUpdated"] = str(
            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        try:
            self.table.put_item(Item=data)
        except Exception as err:
            print(
                "Couldn't add contact %s to table %s. Here's why: %s: %s",
                data["contact"]["contactPhoneNumber"],
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def update_contact(self, data):
        """
        Updates contact data for a contact in the table.
        """
        try:
            contact = self.get_contact_with_old_phone_details(data)
            if contact:
                contact_data = data["contact"]
                response = self.table.update_item(
                    Key={"id": contact[0]["id"]},
                    UpdateExpression="set contact.contactId = :cid, contact.contactPhoneNumber = :cph, contact.contactCountryCode = :code, contact.contactUpdated = :updated",
                    ExpressionAttributeValues={
                        ":cid": contact_data["contactId"],
                        ":cph": contact_data["contactPhoneNumber"],
                        ":code": contact_data["contactCountryCode"],
                        ":updated": str(
                            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                        ),
                    },
                    ReturnValues="UPDATED_NEW",
                )
                return response["Attributes"]
        except Exception as err:
            print(
                "Couldn't update contact %s. Here's why: %s: %s",
                userid,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def update_contact_name(self, data):
        """
        Updates contact name for a contact in the table.
        """
        try:
            contact = self.get_contact(data)
            if contact:
                contact_data = data["contact"]
                response = self.table.update_item(
                    Key={"id": contact[0]["id"]},
                    UpdateExpression="set contact.contactName = :cname, contact.contactUpdated = :updated",
                    ExpressionAttributeValues={
                        ":cname": contact_data["contactName"],
                        ":updated": str(
                            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                        ),
                    },
                    ReturnValues="UPDATED_NEW",
                )
                return response["Attributes"]

        except Exception as err:
            print(
                "Couldn't update contact %s. Here's why: %s: %s",
                userid,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def delete_contact(self, data):
        """
        Deletes a contact from the table.
        """
        try:
            contact = self.get_contact(data)
            if contact:
                self.table.delete_item(Key={"id": contact[0]["id"]})
        except Exception as err:
            print(
                "Couldn't delete contact %s and %s. Here's why: %s: %s",
                userid,
                phone_number,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
