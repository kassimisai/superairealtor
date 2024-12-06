import httpx
from typing import Dict, Optional
from ..core.config import settings

class VapiService:
    def __init__(self):
        self.api_key = settings.VAPI_API_KEY
        self.base_url = "https://api.vapi.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_call(
        self,
        phone_number: str,
        assistant_id: str,
        initial_message: str,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Create a new outbound call using Vapi.ai.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/call",
                headers=self.headers,
                json={
                    "phone_number": phone_number,
                    "assistant_id": assistant_id,
                    "initial_message": initial_message,
                    "metadata": metadata or {},
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_call(self, call_id: str) -> Dict:
        """
        Get call details by ID.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/call/{call_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def end_call(self, call_id: str) -> Dict:
        """
        End an ongoing call.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/call/{call_id}/end",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def create_assistant(
        self,
        name: str,
        instructions: str,
        voice_id: str,
        model: str = "gpt-4",
    ) -> Dict:
        """
        Create a new Vapi assistant.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/assistant",
                headers=self.headers,
                json={
                    "name": name,
                    "instructions": instructions,
                    "voice_id": voice_id,
                    "model": model,
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_assistant(self, assistant_id: str) -> Dict:
        """
        Get assistant details by ID.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/assistant/{assistant_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def update_assistant(
        self,
        assistant_id: str,
        name: Optional[str] = None,
        instructions: Optional[str] = None,
        voice_id: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict:
        """
        Update an existing assistant.
        """
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if instructions is not None:
            update_data["instructions"] = instructions
        if voice_id is not None:
            update_data["voice_id"] = voice_id
        if model is not None:
            update_data["model"] = model

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/assistant/{assistant_id}",
                headers=self.headers,
                json=update_data,
            )
            response.raise_for_status()
            return response.json()

    async def get_call_transcript(self, call_id: str) -> Dict:
        """
        Get the transcript of a call.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/call/{call_id}/transcript",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_call_recording(self, call_id: str) -> Dict:
        """
        Get the recording URL of a call.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/call/{call_id}/recording",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

# Create a singleton instance
vapi_service = VapiService() 