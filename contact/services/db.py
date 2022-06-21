import boto3

# from django.conf import settings


class Contacts:
    """Encapsulates an Amazon DynamoDB table of contact data."""

    def __init__(self):
        self.AWS_ACCESS_KEY_ID = "AKIA4YYA7W7DTVBUSCEI"
        self.AWS_SECRET_ACCESS_KEY = "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"
        self.client = None
        self.dynamodb = None
        self.initialize()
        self.table = self.dynamodb.Table("contactdev")

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

    def list_contacts(self):
        response = self.table.scan()
        return response["Items"]

    def add_contact(self, data):
        """
        Adds a contact to the table.
        """
        try:
            self.table.put_item(
                Item={
                    "userid": data["userid"],
                    "contact_phone_number": data["contact_phone_number"],
                    "device_contact_id": data["device_contact_id"],
                    "contact_name": data["contact_name"],
                    "friend": False,
                }
            )
        except Exception as err:
            print(
                "Couldn't add movie %s to table %s. Here's why: %s: %s",
                data["contact_phone_number"],
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def update_contact(self, userid, phone_number, data):
        """
        Updates contact_name and device_contact_id data for a contact in the table.

        :param userid: User id
        :param phone_number: Contact phone numner
        :param device_contact_id: Contact Id from device
        :param contact_name: Contact Name
        :return: The fields that were updated, with their new values.
        """
        try:
            response = self.table.update_item(
                Key={"userid": userid, "contact_phone_number": phone_number},
                UpdateExpression="set device_contact_id = :cid, contact_name = :cname",
                ExpressionAttributeValues={
                    ":cid": data["device_contact_id"],
                    ":cname": data["contact_name"],
                },
                ReturnValues="UPDATED_NEW",
            )
        except Exception as err:
            print(
                "Couldn't update contact %s in table %s. Here's why: %s: %s",
                phone_number,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Attributes"]

    def delete_contact(self, userid, phone_number):
        """
        Deletes a contact from the table.

        """
        try:
            self.table.delete_item(
                Key={"userid": userid, "contact_phone_number": phone_number}
            )
        except Exception as err:
            print(
                "Couldn't delete contact %s. Here's why: %s: %s",
                title,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
