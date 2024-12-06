from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from uuid import UUID
import openai
from ..mcp.core import AgentContext, AgentType, AgentState

class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    booking_id: Optional[UUID] = None

class Appointment(BaseModel):
    appointment_id: UUID
    lead_id: UUID
    agent_id: UUID
    start_time: datetime
    end_time: datetime
    type: str
    location: str
    status: str
    notes: Optional[str]
    reminders_sent: List[datetime] = []

class SchedulerAgent:
    def __init__(self, context: AgentContext):
        self.context = context
        self.openai_client = openai.OpenAI()
        self.time_slots: Dict[datetime, TimeSlot] = {}
        self.appointments: Dict[UUID, Appointment] = {}

    async def find_available_slots(self, date: datetime, duration: int = 60) -> List[TimeSlot]:
        """
        Finds available time slots for a given date and duration (in minutes).
        """
        available_slots = []
        current_date = date.replace(hour=9, minute=0, second=0, microsecond=0)  # Start at 9 AM
        end_date = current_date.replace(hour=17, minute=0)  # End at 5 PM

        while current_date < end_date:
            slot_end = current_date + timedelta(minutes=duration)
            if slot_end <= end_date:
                slot = self.time_slots.get(current_date)
                if not slot:
                    slot = TimeSlot(start_time=current_date, end_time=slot_end)
                    self.time_slots[current_date] = slot
                
                if slot.is_available:
                    available_slots.append(slot)
            
            current_date += timedelta(minutes=30)  # 30-minute intervals

        return available_slots

    async def schedule_appointment(self, lead_id: UUID, agent_id: UUID, slot: TimeSlot, 
                                 appointment_type: str, location: str) -> Appointment:
        """
        Schedules an appointment for a specific time slot.
        """
        if not slot.is_available:
            raise ValueError("Time slot is not available")

        appointment = Appointment(
            appointment_id=UUID(int=len(self.appointments) + 1),
            lead_id=lead_id,
            agent_id=agent_id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            type=appointment_type,
            location=location,
            status="scheduled",
            notes=None
        )

        slot.is_available = False
        slot.booking_id = appointment.appointment_id
        self.appointments[appointment.appointment_id] = appointment

        # Generate confirmation message
        confirmation = await self._generate_confirmation_message(appointment)
        appointment.notes = confirmation

        return appointment

    async def reschedule_appointment(self, appointment_id: UUID, new_slot: TimeSlot) -> Appointment:
        """
        Reschedules an existing appointment to a new time slot.
        """
        if appointment_id not in self.appointments:
            raise ValueError("Appointment not found")
        if not new_slot.is_available:
            raise ValueError("New time slot is not available")

        appointment = self.appointments[appointment_id]
        old_slot = self.time_slots.get(appointment.start_time)
        if old_slot:
            old_slot.is_available = True
            old_slot.booking_id = None

        appointment.start_time = new_slot.start_time
        appointment.end_time = new_slot.end_time
        new_slot.is_available = False
        new_slot.booking_id = appointment_id

        # Generate rescheduling message
        reschedule_note = await self._generate_reschedule_message(appointment)
        appointment.notes = reschedule_note

        return appointment

    async def cancel_appointment(self, appointment_id: UUID) -> bool:
        """
        Cancels an existing appointment.
        """
        if appointment_id not in self.appointments:
            raise ValueError("Appointment not found")

        appointment = self.appointments[appointment_id]
        slot = self.time_slots.get(appointment.start_time)
        if slot:
            slot.is_available = True
            slot.booking_id = None

        appointment.status = "cancelled"
        
        # Generate cancellation message
        cancellation_note = await self._generate_cancellation_message(appointment)
        appointment.notes = cancellation_note

        return True

    async def send_reminder(self, appointment_id: UUID) -> Dict:
        """
        Sends a reminder for an upcoming appointment.
        """
        if appointment_id not in self.appointments:
            raise ValueError("Appointment not found")

        appointment = self.appointments[appointment_id]
        reminder = await self._generate_reminder_message(appointment)
        appointment.reminders_sent.append(datetime.now())

        return reminder

    async def _generate_confirmation_message(self, appointment: Appointment) -> str:
        """
        Generates a confirmation message for a new appointment.
        """
        prompt = f"""
        Please generate a professional appointment confirmation message with the following details:
        
        Date: {appointment.start_time.strftime('%A, %B %d, %Y')}
        Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}
        Type: {appointment.type}
        Location: {appointment.location}

        Please include:
        1. A warm greeting
        2. Appointment details
        3. What to bring/prepare
        4. Contact information for questions
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional real estate scheduling assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    async def _generate_reschedule_message(self, appointment: Appointment) -> str:
        """
        Generates a message for a rescheduled appointment.
        """
        prompt = f"""
        Please generate a professional appointment rescheduling confirmation with the following details:
        
        New Date: {appointment.start_time.strftime('%A, %B %d, %Y')}
        New Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}
        Type: {appointment.type}
        Location: {appointment.location}

        Please include:
        1. A polite acknowledgment of the change
        2. New appointment details
        3. Confirmation request
        4. Contact information for questions
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional real estate scheduling assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    async def _generate_cancellation_message(self, appointment: Appointment) -> str:
        """
        Generates a cancellation message for an appointment.
        """
        prompt = f"""
        Please generate a professional appointment cancellation message for:
        
        Date: {appointment.start_time.strftime('%A, %B %d, %Y')}
        Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}
        Type: {appointment.type}

        Please include:
        1. A polite acknowledgment of the cancellation
        2. Option to reschedule
        3. Contact information for questions
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional real estate scheduling assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    async def _generate_reminder_message(self, appointment: Appointment) -> Dict:
        """
        Generates a reminder message for an upcoming appointment.
        """
        prompt = f"""
        Please generate a friendly reminder message for an upcoming appointment:
        
        Date: {appointment.start_time.strftime('%A, %B %d, %Y')}
        Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}
        Type: {appointment.type}
        Location: {appointment.location}

        Please include:
        1. A friendly reminder greeting
        2. Appointment details
        3. Any preparation instructions
        4. Contact information
        """

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional real estate scheduling assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return {
            'content': response.choices[0].message.content,
            'generated_at': datetime.now().isoformat(),
            'metadata': {
                'type': 'reminder',
                'version': '1.0'
            }
        }

    async def update_context(self, new_context: Dict) -> None:
        """
        Updates the agent's context with new information.
        """
        self.context.memory.update(new_context)
        await self.context.update_agent_state(self.context.agent_id, AgentState.READY) 