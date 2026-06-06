from typing import List
from pydantic import BaseModel
from langchain_groq import ChatGroq
from agents.graph import ResearchState
from core.config import settings

class SubTask(BaseModel):
    task:str
    type:str

class PlannerOutput(BaseModel):
    tasks: List[SubTask]


llm = ChatGroq(
    api_key = settings.groq_api_key,
    model = "llama-3.3-70b-versatile"
)

async def planner_node(state: ResearchState)-> dict:
    structured_llm = llm.with_structured_output(PlannerOutput)

    result = await structured_llm.ainvoke(
        f"""You are a research planner. Break the following query into 3-5 focused sub-tasks.
        Each sub-task should be a specific search or reading task.
        
        Query: {state['query']}"""
    )

    print(f"\n[PLANNER] Created {len(result.tasks)} tasks:")
    for t in result.tasks:
        print(f"-[{t.type}] {t.task}')")
    
    return {"tasks" : [t.model_dump() for t in result.tasks]}