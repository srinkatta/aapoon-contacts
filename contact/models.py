from django.db import models


class Contact(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=250)
    device_contact_id = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=250)
    friend = models.BooleanField(
        default=False, help_text="This would be true if user is on aapoon."
    )

    def __str__(self):
        return f"{self.user_id}, Contact: {self.name}, Friend: {self.friend}"
