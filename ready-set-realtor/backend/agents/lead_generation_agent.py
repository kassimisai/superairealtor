from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
import openai
from ..mcp.core import AgentContext, AgentType, AgentState

class LeadQualificationCriteria(BaseModel):
    budget_min: Optional[float]
    budget_max: Optional[float]
    property_type: Optional[str]
    location: Optional[str]
    timeline: Optional[str]
    pre_approved: Optional[bool]

class LeadGenerationAgent:
    def __init__(self, context: AgentContext):
        self.context = context
        self.openai_client = openai.OpenAI()
        self.qualification_criteria = {}

    async def qualify_lead(self, lead_data: Dict) -> Dict:
        """
        Qualifies a lead based on conversation history and criteria.
        """
        # Prepare the conversation context
        conversation_history = lead_data.get('conversation_history', [])
        criteria = LeadQualificationCriteria(**lead_data.get('criteria', {}))

        # Create the prompt for lead qualification
        prompt = self._create_qualification_prompt(conversation_history, criteria)

        # Get qualification assessment from OpenAI
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a real estate lead qualification expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        # Process the response
        qualification_result = self._process_qualification_response(response.choices[0].message.content)
        
        return qualification_result

    async def schedule_appointment(self, lead_id: UUID, availability: Dict) -> Dict:
        """
        Attempts to schedule an appointment with a qualified lead.
        """
        # Implementation for appointment scheduling
        pass

    def _create_qualification_prompt(self, conversation_history: List[str], criteria: LeadQualificationCriteria) -> str:
        """
        Creates a prompt for lead qualification based on conversation history and criteria.
        """
        prompt = f"""
        Please analyze this lead conversation and determine qualification based on the following criteria:
        - Budget Range: {criteria.budget_min or 'Not specified'} to {criteria.budget_max or 'Not specified'}
        - Property Type: {criteria.property_type or 'Not specified'}
        - Location: {criteria.location or 'Not specified'}
        - Timeline: {criteria.timeline or 'Not specified'}
        - Pre-approved: {criteria.pre_approved or 'Not specified'}

        Conversation History:
        {chr(10).join(conversation_history)}

        Please provide a structured analysis of:
        1. Lead Qualification Status
        2. Key Insights
        3. Recommended Next Steps
        4. Risk Factors
        """
        return prompt

    def _process_qualification_response(self, response_text: str) -> Dict:
        """
        Processes the OpenAI response into a structured qualification result.
        """
        # Parse the response text into structured data
        # This is a simplified version - in production, you'd want more robust parsing
        sections = response_text.split('\n\n')
        
        return {
            'qualification_status': sections[0] if len(sections) > 0 else 'Unknown',
            'key_insights': sections[1] if len(sections) > 1 else '',
            'recommended_next_steps': sections[2] if len(sections) > 2 else '',
            'risk_factors': sections[3] if len(sections) > 3 else '',
            'qualified_at': datetime.now().isoformat(),
        }

    async def update_context(self, new_context: Dict) -> None:
        """
        Updates the agent's context with new information.
        """
        self.context.memory.update(new_context)
        await self.context.update_agent_state(self.context.agent_id, AgentState.READY) 