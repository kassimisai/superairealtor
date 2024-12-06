from twilio.rest import Client
from typing import Dict, Optional
from ..core.config import settings

class TwilioService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_PHONE_NUMBER
        self.client = Client(self.account_sid, self.auth_token)

    async def send_sms(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None,
    ) -> Dict:
        """
        Send an SMS message using Twilio.
        """
        params = {
            "to": to_number,
            "from_": self.from_number,
            "body": message,
        }
        if media_url:
            params["media_url"] = [media_url]

        message = self.client.messages.create(**params)
        return {
            "id": message.sid,
            "status": message.status,
            "to": message.to,
            "from": message.from_,
            "body": message.body,
            "date_created": message.date_created,
            "date_sent": message.date_sent,
            "price": message.price,
            "price_unit": message.price_unit,
        }

    async def get_message(self, message_id: str) -> Dict:
        """
        Get message details by ID.
        """
        message = self.client.messages(message_id).fetch()
        return {
            "id": message.sid,
            "status": message.status,
            "to": message.to,
            "from": message.from_,
            "body": message.body,
            "date_created": message.date_created,
            "date_sent": message.date_sent,
            "price": message.price,
            "price_unit": message.price_unit,
        }

    async def get_messages(
        self,
        to_number: Optional[str] = None,
        from_number: Optional[str] = None,
        date_sent_after: Optional[str] = None,
        date_sent_before: Optional[str] = None,
    ) -> Dict:
        """
        Get messages based on filters.
        """
        params = {}
        if to_number:
            params["to"] = to_number
        if from_number:
            params["from_"] = from_number
        if date_sent_after:
            params["date_sent_after"] = date_sent_after
        if date_sent_before:
            params["date_sent_before"] = date_sent_before

        messages = self.client.messages.list(**params)
        return [
            {
                "id": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "body": message.body,
                "date_created": message.date_created,
                "date_sent": message.date_sent,
                "price": message.price,
                "price_unit": message.price_unit,
            }
            for message in messages
        ]

    async def get_message_media(self, message_id: str) -> Dict:
        """
        Get media associated with a message.
        """
        message = self.client.messages(message_id).fetch()
        media_list = self.client.messages(message_id).media.list()
        return [
            {
                "id": media.sid,
                "content_type": media.content_type,
                "url": f"https://api.twilio.com{media.uri}",
            }
            for media in media_list
        ]

# Create a singleton instance
twilio_service = TwilioService() 