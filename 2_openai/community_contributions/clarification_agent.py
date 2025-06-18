from pydantic import BaseModel, Field
from agents import Agent, function_tool
from typing import Dict, Any

CLARIFICATION_INSTRUCTIONS = """You are a research clarification assistant. Given a user's initial research query, 
you need to ask 3 thoughtful questions that will help clarify and refine their research needs.

Your questions should help understand:
1. The scope and depth they want
2. The specific aspects they're most interested in
3. The context or purpose of their research

Generate exactly 3 questions that will help create a more focused and comprehensive research plan."""

SUMMARY_INSTRUCTIONS = """You are a research query refinement assistant. Given an original query 
and the user's responses to clarification questions, create a refined, comprehensive query that 
will guide the research process.

Your refined query should be specific, actionable, and incorporate the user's clarifications 
to ensure the research addresses their actual needs."""


class ClarificationQuestions(BaseModel):
    question_1: str = Field(description="First clarifying question about scope or depth")
    question_2: str = Field(description="Second clarifying question about specific aspects")
    question_3: str = Field(description="Third clarifying question about context or purpose")


class SummarizedQuery(BaseModel):
    original_query: str = Field(description="The user's original query")
    clarifications: str = Field(description="Summary of the user's responses to clarification questions")
    refined_query: str = Field(description="A refined, more specific query for research")
    research_focus: str = Field(description="Key areas the research should focus on")


@function_tool
def clarification_tool(query: str) -> str:
    """Generate 3 clarification questions for the user's research query"""
    import asyncio
    import json
    
    clarification_agent = Agent(
        name="ClarificationAgent",
        instructions=CLARIFICATION_INSTRUCTIONS,
        model="gpt-4o-mini",
        output_type=ClarificationQuestions,
    )
    
    async def run_clarification():
        from agents import Runner
        result = await Runner.run(clarification_agent, f"User's research query: {query}")
        return result.final_output_as(ClarificationQuestions)
    
    # Run the async function
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    questions = loop.run_until_complete(run_clarification())
    
    # Return as JSON string for the function tool
    return json.dumps({
        "status": "success",
        "question_1": questions.question_1,
        "question_2": questions.question_2,
        "question_3": questions.question_3
    })


@function_tool
def summarizer_tool(original_query: str, clarifications: str) -> str:
    """Create a summarized query based on original query and user clarifications"""
    import asyncio
    import json
    
    summarizer_agent = Agent(
        name="SummarizerAgent",
        instructions=SUMMARY_INSTRUCTIONS,
        model="gpt-4o-mini",
        output_type=SummarizedQuery,
    )
    
    async def run_summarizer():
        from agents import Runner
        input_text = f"""Original Query: {original_query}
        
User's Clarification Responses:
{clarifications}

Please create a refined query that incorporates these clarifications."""
        
        result = await Runner.run(summarizer_agent, input_text)
        return result.final_output_as(SummarizedQuery)
    
    # Run the async function
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    summary = loop.run_until_complete(run_summarizer())
    
    # Return as JSON string for the function tool
    return json.dumps({
        "status": "success",
        "original_query": summary.original_query,
        "clarifications": summary.clarifications,
        "refined_query": summary.refined_query,
        "research_focus": summary.research_focus
    })


# Keep original agents for backward compatibility and direct use
clarification_agent = Agent(
    name="ClarificationAgent",
    instructions=CLARIFICATION_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ClarificationQuestions,
)

summarizer_agent = Agent(
    name="SummarizerAgent", 
    instructions=SUMMARY_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=SummarizedQuery,
)