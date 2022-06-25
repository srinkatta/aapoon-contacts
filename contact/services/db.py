import uuid
import boto3
import threading

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

    def get_contact(self, userid, country_code, phone_number):
        response = self.table.scan(
            FilterExpression="contact_country_code = :code AND contact_phone_number = :contact_phone_number AND userid = :userid",
            ExpressionAttributeValues={
                ":code": f"{country_code}",
                ":contact_phone_number": f"{phone_number}",
                ":userid": f"{userid}",
            },
        )
        return response["Items"]

    def list_contacts(self):
        response = self.table.scan(
            FilterExpression="friend = :f",
            ExpressionAttributeValues={
                ":f": False,
            },
        )
        return response["Items"]

    def add_contact(self, data):
        """
        Adds a contact to the table.
        """
        payload = {
            "id": f"{uuid.uuid4()}",
            "userid": data["userid"],
            "contact_country_code": data["contact_country_code"],
            "contact_phone_number": data["contact_phone_number"],
            "device_contact_id": data["device_contact_id"],
            "contact_name": data["contact_name"],
            "friend": False,
        }
        try:
            self.table.put_item(Item=payload)
            self.__friend_check(payload)
        except Exception as err:
            print(
                "Couldn't add movie %s to table %s. Here's why: %s: %s",
                data["contact_phone_number"],
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def update_contact(self, userid, country_code, phone_number, data):
        """
        Updates contact_name and device_contact_id data for a contact in the table.

        :param userid: User id
        :param contact_phone_number: Contact phone numner
        :param device_contact_id: Contact Id from device
        :param contact_name: Contact Name
        :return: The fields that were updated, with their new values.
        """
        try:
            contact = self.get_contact(userid, country_code, phone_number)
            if contact:
                response = self.table.update_item(
                    Key={"id": contact[0]["id"]},
                    UpdateExpression="set device_contact_id = :cid, contact_name = :cname, contact_phone_number = :cph, contact_country_code = :code",
                    ExpressionAttributeValues={
                        ":cid": data["device_contact_id"],
                        ":cname": data["contact_name"],
                        ":cph": data["contact_phone_number"],
                        ":code": data["contact_country_code"],
                    },
                    ReturnValues="UPDATED_NEW",
                )
        except Exception as err:
            print(
                "Couldn't update contact %s. Here's why: %s: %s",
                userid,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Attributes"]

    def patch_contact(self, uid, data):
        """
        Updates contact_name and device_contact_id data for a contact in the table.

        :param userid: User id
        :param contact_phone_number: Contact phone numner
        :param device_contact_id: Contact Id from device
        :param contact_name: Contact Name
        :return: The fields that were updated, with their new values.
        """
        try:
            response = self.table.update_item(
                Key={"id": uid},
                UpdateExpression="set friend = :f",
                ExpressionAttributeValues={
                    ":f": data["friend"],
                },
                ReturnValues="UPDATED_NEW",
            )
        except Exception as err:
            print(
                "Couldn't update contact %s. Here's why: %s: %s",
                uid,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Attributes"]

    def delete_contact(self, userid, country_code, phone_number):
        """
        Deletes a contact from the table.

        """
        try:
            contact = self.get_contact(userid, country_code, phone_number)
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

    def __friend_check(self, payload):
        uuid = payload["id"]
        country_code = payload["contact_country_code"]
        phone_number = payload["contact_phone_number"]
        phone = f"{country_code}{phone_number}"
        status, friend = check_friend_status(payload["contact_phone_number"])

        data = {
            "contact_phone_number": f"{payload['contact_phone_number']}",
            "device_contact_id": f"{payload['device_contact_id']}",
            "contact_name": f"{payload['contact_name']}",
            "friend": friend,
        }

        return self.patch_contact(uuid, data)
