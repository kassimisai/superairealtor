from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from uuid import UUID
import openai
from ..mcp.core import AgentContext, AgentType, AgentState

class TransactionMilestone(BaseModel):
    name: str
    due_date: datetime
    status: str
    description: Optional[str]
    assigned_to: Optional[str]
    completed_at: Optional[datetime]

class TransactionCoordinatorAgent:
    def __init__(self, context: AgentContext):
        self.context = context
        self.openai_client = openai.OpenAI()
        self.active_transactions = {}

    async def create_transaction(self, transaction_data: Dict) -> Dict:
        """
        Creates a new transaction and sets up initial milestones.
        """
        transaction_id = UUID(transaction_data['transaction_id'])
        milestones = self._generate_transaction_milestones(transaction_data)
        
        self.active_transactions[transaction_id] = {
            'data': transaction_data,
            'milestones': milestones,
            'status': 'active',
            'created_at': datetime.now(),
            'last_updated': datetime.now()
        }
        
        return self.active_transactions[transaction_id]

    async def generate_document(self, transaction_id: UUID, document_type: str, context: Dict) -> Dict:
        """
        Generates a real estate document based on transaction context.
        """
        if transaction_id not in self.active_transactions:
            raise ValueError("Transaction not found")

        # Create the prompt for document generation
        prompt = self._create_document_prompt(document_type, context)

        # Get document content from OpenAI
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a real estate document generation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )

        # Process the response into a structured document
        document = self._process_document_response(response.choices[0].message.content)
        
        return document

    async def update_milestone(self, transaction_id: UUID, milestone_name: str, status: str) -> Dict:
        """
        Updates the status of a transaction milestone.
        """
        if transaction_id not in self.active_transactions:
            raise ValueError("Transaction not found")

        transaction = self.active_transactions[transaction_id]
        for milestone in transaction['milestones']:
            if milestone.name == milestone_name:
                milestone.status = status
                if status == 'completed':
                    milestone.completed_at = datetime.now()
                transaction['last_updated'] = datetime.now()
                break

        return transaction

    def _generate_transaction_milestones(self, transaction_data: Dict) -> List[TransactionMilestone]:
        """
        Generates a list of milestones based on transaction type and requirements.
        """
        # This is a simplified version - in production, you'd want more dynamic milestone generation
        base_date = datetime.now()
        milestones = [
            TransactionMilestone(
                name="Contract Signed",
                due_date=base_date + timedelta(days=1),
                status="pending",
                description="Get purchase agreement signed by all parties"
            ),
            TransactionMilestone(
                name="Earnest Money Deposited",
                due_date=base_date + timedelta(days=3),
                status="pending",
                description="Ensure earnest money is deposited into escrow"
            ),
            TransactionMilestone(
                name="Inspection Period",
                due_date=base_date + timedelta(days=10),
                status="pending",
                description="Complete all property inspections"
            ),
            TransactionMilestone(
                name="Loan Approval",
                due_date=base_date + timedelta(days=21),
                status="pending",
                description="Obtain final loan approval"
            ),
            TransactionMilestone(
                name="Closing",
                due_date=base_date + timedelta(days=30),
                status="pending",
                description="Complete closing and transfer of property"
            )
        ]
        return milestones

    def _create_document_prompt(self, document_type: str, context: Dict) -> str:
        """
        Creates a prompt for document generation based on type and context.
        """
        prompt = f"""
        Please generate a {document_type} with the following details:

        Property Address: {context.get('property_address', 'Not specified')}
        Purchase Price: {context.get('purchase_price', 'Not specified')}
        Buyer(s): {context.get('buyers', 'Not specified')}
        Seller(s): {context.get('sellers', 'Not specified')}
        Closing Date: {context.get('closing_date', 'Not specified')}

        Additional Terms:
        {chr(10).join(context.get('additional_terms', []))}

        Please format the document according to standard real estate practices in the jurisdiction.
        """
        return prompt

    def _process_document_response(self, response_text: str) -> Dict:
        """
        Processes the OpenAI response into a structured document.
        """
        return {
            'content': response_text,
            'generated_at': datetime.now().isoformat(),
            'metadata': {
                'format': 'text',
                'version': '1.0'
            }
        }

    async def update_context(self, new_context: Dict) -> None:
        """
        Updates the agent's context with new information.
        """
        self.context.memory.update(new_context)
        await self.context.update_agent_state(self.context.agent_id, AgentState.READY) 