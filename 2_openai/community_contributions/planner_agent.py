from pydantic import BaseModel, Field
from agents import Agent, function_tool
from typing import Dict, Any

HOW_MANY_SEARCHES = 5

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")


@function_tool
def planner_tool(refined_query: str) -> str:
    """Create a search plan with 5 search items for the given refined research query"""
    import asyncio
    
    planner_agent = Agent(
        name="PlannerAgent",
        instructions=INSTRUCTIONS,
        model="gpt-4o-mini",
        output_type=WebSearchPlan,
    )
    
    async def run_planner():
        from agents import Runner
        result = await Runner.run(planner_agent, f"Refined Query: {refined_query}")
        return result.final_output_as(WebSearchPlan)
    
    # Run the async function
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    plan = loop.run_until_complete(run_planner())
    
    # Convert to JSON string for tool return
    import json
    return json.dumps({
        "status": "success",
        "searches": [
            {"reason": item.reason, "query": item.query} 
            for item in plan.searches
        ]
    })


# Keep the original agent for direct use if needed
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)