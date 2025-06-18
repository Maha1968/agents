from agents import Agent, WebSearchTool, ModelSettings, function_tool
from typing import Dict, Any

INSTRUCTIONS = (
    "You are a research assistant. Given a search term and reason, you search the web for that term and "
    "produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 "
    "words. Capture the main points. Write succinctly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary itself."
)


@function_tool
def search_tool(search_query: str, reason: str) -> str:
    """Perform a web search based on a search plan item and return a concise summary of results"""
    import asyncio
    
    search_agent = Agent(
        name="Search agent",
        instructions=INSTRUCTIONS,
        tools=[WebSearchTool(search_context_size="low")],
        model="gpt-4o-mini",
        model_settings=ModelSettings(tool_choice="required"),
    )
    
    async def run_search():
        from agents import Runner
        input_text = f"Search term: {search_query}\nReason for searching: {reason}"
        
        try:
            result = await Runner.run(search_agent, input_text)
            return str(result.final_output)
        except Exception as e:
            return f"Search failed for '{search_query}': {str(e)}"
    
    # Run the async function
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    summary = loop.run_until_complete(run_search())
    
    import json
    return json.dumps({
        "status": "success",
        "search_query": search_query,
        "reason": reason,
        "summary": summary
    })


# Keep the original agent for direct use if needed
search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)