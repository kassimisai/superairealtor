from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from uuid import UUID
import openai
from ..mcp.core import AgentContext, AgentType, AgentState

class FollowUpTemplate(BaseModel):
    template_id: str
    name: str
    content: str
    channel: str
    conditions: Dict
    delay: Optional[int]  # delay in days

class FollowUpSchedule(BaseModel):
    lead_id: UUID
    templates: List[FollowUpTemplate]
    last_contact: Optional[datetime]
    next_contact: Optional[datetime]
    status: str
    notes: List[str]

class FollowUpAgent:
    def __init__(self, context: AgentContext):
        self.context = context
        self.openai_client = openai.OpenAI()
        self.follow_up_schedules: Dict[UUID, FollowUpSchedule] = {}
        self.templates: Dict[str, FollowUpTemplate] = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, FollowUpTemplate]:
        """
        Initializes default follow-up templates.
        """
        return {
            "initial_thank_you": FollowUpTemplate(
                template_id="initial_thank_you",
                name="Initial Thank You",
                content="Thank you for your interest in {property_address}. I enjoyed our conversation about {highlights}.",
                channel="email",
                conditions={"stage": "initial_contact"},
                delay=1
            ),
            "property_update": FollowUpTemplate(
                template_id="property_update",
                name="Property Update",
                content="I wanted to update you on {property_address}. {update_details}",
                channel="email",
                conditions={"stage": "viewing_scheduled"},
                delay=2
            ),
            "market_update": FollowUpTemplate(
                template_id="market_update",
                name="Market Update",
                content="Here's the latest market update for {area}: {market_details}",
                channel="email",
                conditions={"stage": "nurturing"},
                delay=7
            ),
            "viewing_followup": FollowUpTemplate(
                template_id="viewing_followup",
                name="Viewing Follow-up",
                content="I hope you enjoyed viewing {property_address}. I'd love to hear your thoughts.",
                channel="email",
                conditions={"stage": "viewed"},
                delay=1
            )
        }

    async def create_follow_up_schedule(self, lead_id: UUID, lead_data: Dict) -> FollowUpSchedule:
        """
        Creates a follow-up schedule for a lead based on their status and preferences.
        """
        templates = self._select_templates(lead_data)
        schedule = FollowUpSchedule(
            lead_id=lead_id,
            templates=templates,
            last_contact=datetime.now(),
            next_contact=self._calculate_next_contact(templates[0] if templates else None),
            status="active",
            notes=[]
        )
        
        self.follow_up_schedules[lead_id] = schedule
        return schedule

    async def generate_follow_up_message(self, lead_id: UUID, template_id: str, context: Dict) -> Dict:
        """
        Generates a personalized follow-up message using the specified template.
        """
        if lead_id not in self.follow_up_schedules:
            raise ValueError("Lead not found in follow-up schedules")

        template = self.templates.get(template_id)
        if not template:
            raise ValueError("Template not found")

        # Create the prompt for message generation
        prompt = self._create_message_prompt(template, context)

        # Get personalized message from OpenAI
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a real estate follow-up expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        # Process the response
        message = self._process_message_response(response.choices[0].message.content)
        
        # Update schedule
        schedule = self.follow_up_schedules[lead_id]
        schedule.last_contact = datetime.now()
        schedule.next_contact = self._calculate_next_contact(template)
        schedule.notes.append(f"Sent {template.name} on {datetime.now().isoformat()}")

        return message

    def _select_templates(self, lead_data: Dict) -> List[FollowUpTemplate]:
        """
        Selects appropriate templates based on lead data and status.
        """
        stage = lead_data.get('stage', 'initial_contact')
        selected_templates = []
        
        for template in self.templates.values():
            if template.conditions.get('stage') == stage:
                selected_templates.append(template)
        
        return selected_templates

    def _calculate_next_contact(self, template: Optional[FollowUpTemplate]) -> Optional[datetime]:
        """
        Calculates the next contact time based on template delay.
        """
        if not template or not template.delay:
            return None
        
        return datetime.now() + timedelta(days=template.delay)

    def _create_message_prompt(self, template: FollowUpTemplate, context: Dict) -> str:
        """
        Creates a prompt for message generation based on template and context.
        """
        prompt = f"""
        Please generate a personalized follow-up message using this template:
        {template.content}

        Context:
        Lead Name: {context.get('lead_name', 'Not specified')}
        Property Interest: {context.get('property_interest', 'Not specified')}
        Last Interaction: {context.get('last_interaction', 'Not specified')}
        Stage: {context.get('stage', 'Not specified')}

        Additional Notes:
        {chr(10).join(context.get('notes', []))}

        Please make the message personal and engaging while maintaining professionalism.
        """
        return prompt

    def _process_message_response(self, response_text: str) -> Dict:
        """
        Processes the OpenAI response into a structured message.
        """
        return {
            'content': response_text,
            'generated_at': datetime.now().isoformat(),
            'metadata': {
                'type': 'follow_up',
                'version': '1.0'
            }
        }

    async def update_context(self, new_context: Dict) -> None:
        """
        Updates the agent's context with new information.
        """
        self.context.memory.update(new_context)
        await self.context.update_agent_state(self.context.agent_id, AgentState.READY) 