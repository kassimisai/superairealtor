from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..core.database import get_db
from ..core.security import get_current_user, TokenData
from ..schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadQualification
from ..models.lead import Lead
from ..agents.lead_generation_agent import LeadGenerationAgent
from ..mcp.core import AgentContext, AgentType

router = APIRouter(prefix="/leads", tags=["leads"])

@router.post("", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Create a new lead.
    """
    db_lead = Lead(**lead_data.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.get("", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all leads for the current user.
    """
    leads = db.query(Lead).filter(
        Lead.user_id == current_user.user_id
    ).offset(skip).limit(limit).all()
    return leads

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get a specific lead by ID.
    """
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.user_id == current_user.user_id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead

@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update a lead's information.
    """
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.user_id == current_user.user_id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    for field, value in lead_data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return lead

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Delete a lead.
    """
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.user_id == current_user.user_id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    db.delete(lead)
    db.commit()

@router.post("/{lead_id}/qualify", response_model=dict)
async def qualify_lead(
    lead_id: UUID,
    qualification_data: LeadQualification,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Qualify a lead using the Lead Generation Agent.
    """
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.user_id == current_user.user_id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Initialize Lead Generation Agent
    agent_context = AgentContext(
        agent_type=AgentType.LEAD_GENERATION,
        capabilities=["lead_qualification"],
        tools=[]
    )
    agent = LeadGenerationAgent(agent_context)

    # Qualify the lead
    qualification_result = await agent.qualify_lead({
        "conversation_history": qualification_data.conversation_history,
        "criteria": qualification_data.criteria
    })

    # Update lead status based on qualification
    lead.status = "qualified" if qualification_result.get("qualification_status") == "Qualified" else "contacted"
    lead.metadata.update({
        "qualification_result": qualification_result,
        "qualified_at": qualification_result.get("qualified_at")
    })

    db.commit()
    db.refresh(lead)

    return qualification_result 