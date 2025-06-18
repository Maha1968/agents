from pydantic import BaseModel, Field
from agents import Agent, function_tool
from typing import Dict, Any

INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original refined query, and search results from multiple searches.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final comprehensive report in markdown format")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


@function_tool
def writer_tool(refined_query: str, search_results: str) -> str:
    """Write a comprehensive report based on the refined query and search results"""
    import asyncio
    
    writer_agent = Agent(
        name="WriterAgent",
        instructions=INSTRUCTIONS,
        model="gpt-4o-mini",
        output_type=ReportData,
    )
    
    async def run_writer():
        from agents import Runner
        
        input_text = f"""Refined research query: {refined_query}

Search Results:
{search_results}

Please create a comprehensive report that:
1. Creates an outline for the report structure
2. Synthesizes all search results into a cohesive document
3. Aims for 5-10 pages of content, at least 1000 words
4. Uses markdown formatting"""
        
        result = await Runner.run(writer_agent, input_text)
        return result.final_output_as(ReportData)
    
    # Run the async function
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    report = loop.run_until_complete(run_writer())
    
    import json
    return json.dumps({
        "status": "success",
        "short_summary": report.short_summary,
        "markdown_report": report.markdown_report,
        "follow_up_questions": report.follow_up_questions
    })


# Keep the original agent for direct use if needed
writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)