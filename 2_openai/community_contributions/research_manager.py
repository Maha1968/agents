from agents import Runner, trace, gen_trace_id, Agent
from search_agent import search_agent
from planner_agent import planner_agent  
from writer_agent import writer_agent
from clarification_agent import clarification_agent, summarizer_agent
from email_agent import email_agent
import asyncio

class ResearchManager:
    def __init__(self):
        self.max_tries = 6
        self.main_agent = self._create_main_agent()

    def _create_main_agent(self):
        """Create main agent with planner, search, and writer as tools"""
        MAIN_INSTRUCTIONS = """You are a comprehensive research manager. You have access to several tools:
        
        1. planner_agent: Creates a search plan with 5 search items for a refined query
        2. search_agent: Performs web searches and summarizes results  
        3. writer_agent: Writes comprehensive reports from search results
        
        Your job is to orchestrate these tools systematically:
        
        Step 1: Use planner_agent to create a search plan with the refined query
        Step 2: Use search_agent multiple times (once for each search item in the plan)
        Step 3: Use writer_agent to create a comprehensive report from all search results
        
        You have up to 6 tool calls. Follow the steps in order and be systematic.
        Return the final markdown report when complete.
        
        When you call search_agent, use the exact search_query and reason from the search plan."""
        
        return Agent(
            name="MainResearchAgent",
            instructions=MAIN_INSTRUCTIONS,
            tools=[
                planner_agent.as_tool(
                    tool_name="planner_tool",
                    tool_description="Creates a search plan with 5 search items for a refined research query"
                ),
                search_agent.as_tool(
                    tool_name="search_tool", 
                    tool_description="Performs web searches and returns concise summaries of results"
                ),
                writer_agent.as_tool(
                    tool_name="writer_tool",
                    tool_description="Writes comprehensive reports from search results and refined queries"
                )
            ],
            model="gpt-4o"
        )

    async def get_clarification_questions(self, query: str):
        """Get clarification questions using clarification_agent (as agent)"""
        try:
            print(f"Getting clarification questions for query: {query}")
            
            result = await Runner.run(
                clarification_agent,
                f"User's research query: {query}"
            )
            
            questions = result.final_output_as(type(result.final_output))
            print(f"Got clarification questions: {questions}")
            
            return {
                "question_1": questions.question_1,
                "question_2": questions.question_2,
                "question_3": questions.question_3
            }
                
        except Exception as e:
            print(f"Error getting clarification questions: {e}")
            raise

    async def run(self, query: str, clarifications: str):
        """Run the deep research process with clarifications"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            
            try:
                # Step 1: Create summarized query using summarizer_agent (as agent)
                yield "Creating refined research query..."
                print("Calling summarizer_agent...")
                
                summary_result = await Runner.run(
                    summarizer_agent,
                    f"""Original Query: {query}
        
User's Clarification Responses:
{clarifications}

Please create a refined query that incorporates these clarifications."""
                )
                
                summary_data = summary_result.final_output_as(type(summary_result.final_output))
                refined_query = summary_data.refined_query
                print(f"Got refined query: {refined_query}")
                yield f"Refined query: {refined_query}"
                
                # Step 2: Use main agent with tools to do the research
                yield "Starting research with planner, search, and writer tools..."
                
                research_input = f"""Please conduct comprehensive research for this refined query: {refined_query}

Steps to follow:
1. Use planner_agent to create a search plan
2. Use search_agent multiple times based on the search plan
3. Use writer_agent to create a comprehensive report

Please proceed step by step and return the final markdown report."""

                result = await Runner.run(
                    self.main_agent,
                    research_input
                )
                
                yield "Research completed! Preparing to send email..."
                
                # Step 3: Send email using email_agent (as agent)
                if hasattr(result, 'final_output') and result.final_output:
                    report = str(result.final_output)
                    await self._send_email_report(report)
                    yield "Email sent successfully!"
                    yield "## Research Complete!\n\n" + report
                else:
                    yield "Research process completed but no report was generated."
                
            except Exception as e:
                yield f"Error during research: {str(e)}"
                print(f"Research error: {e}")
                import traceback
                traceback.print_exc()

    async def _send_email_report(self, report: str):
        """Send the final report via email using email_agent (as agent)"""
        try:
            result = await Runner.run(email_agent, report)
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")

    # Legacy methods for backward compatibility
    async def plan_searches(self, query: str):
        """Legacy method - now handled by the research manager"""
        pass

    async def perform_searches(self, search_plan):
        """Legacy method - now handled by the research manager"""
        pass

    async def search(self, item):
        """Legacy method - now handled by the research manager"""
        pass

    async def write_report(self, query: str, search_results: list[str]):
        """Legacy method - now handled by the research manager"""
        pass
    
    async def send_email(self, report):
        """Legacy method - now handled separately"""
        return await self._send_email_report(str(report))