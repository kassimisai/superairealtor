from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    LEAD_GENERATION = "lead_generation"
    TRANSACTION_COORDINATOR = "transaction_coordinator"
    FOLLOW_UP = "follow_up"
    SCHEDULER = "scheduler"

class AgentState(str, Enum):
    INITIALIZED = "initialized"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"

class AgentContext(BaseModel):
    agent_id: UUID = Field(default_factory=uuid4)
    agent_type: AgentType
    capabilities: List[str]
    tools: List[str]
    memory: Dict = Field(default_factory=dict)
    state: AgentState = AgentState.INITIALIZED
    last_active: Optional[datetime] = None

class AgentTask(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    task_type: str
    priority: int = 1
    context: Dict
    dependencies: List[str] = Field(default_factory=list)
    deadline: Optional[datetime] = None
    status: str = "pending"

class AgentTeam(BaseModel):
    team_id: UUID = Field(default_factory=uuid4)
    agents: List[AgentContext]
    shared_context: Dict = Field(default_factory=dict)
    active_tasks: List[AgentTask] = Field(default_factory=list)

class MCPController:
    def __init__(self):
        self.agents: Dict[UUID, AgentContext] = {}
        self.teams: Dict[UUID, AgentTeam] = {}
        self.task_queue: List[AgentTask] = []

    async def create_agent(self, agent_type: AgentType, capabilities: List[str]) -> AgentContext:
        agent = AgentContext(
            agent_type=agent_type,
            capabilities=capabilities,
            tools=[],
            memory={},
            state=AgentState.INITIALIZED
        )
        self.agents[agent.agent_id] = agent
        return agent

    async def create_team(self, agents: List[AgentContext]) -> AgentTeam:
        team = AgentTeam(
            agents=agents,
            shared_context={},
            active_tasks=[]
        )
        self.teams[team.team_id] = team
        return team

    async def assign_task(self, agent_id: UUID, task: AgentTask) -> bool:
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        if agent.state != AgentState.READY:
            return False

        agent.state = AgentState.BUSY
        agent.last_active = datetime.now()
        self.task_queue.append(task)
        return True

    async def update_agent_state(self, agent_id: UUID, state: AgentState) -> bool:
        if agent_id not in self.agents:
            return False
        
        self.agents[agent_id].state = state
        self.agents[agent_id].last_active = datetime.now()
        return True 