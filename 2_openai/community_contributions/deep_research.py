import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager

load_dotenv(override=True)

research_manager = ResearchManager()

def get_clarification_questions(query: str):
    """Get clarification questions for the user's query (synchronous version)"""
    if not query.strip():
        return "", "", "", gr.update(visible=False)
    
    try:
        print(f"Getting clarification questions for: {query}")
        # Run the async method in a new event loop
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        questions = loop.run_until_complete(research_manager.get_clarification_questions(query))
        print(f"Clarification questions received: {questions}")
        
        return (
            questions["question_1"],
            questions["question_2"], 
            questions["question_3"],
            gr.update(visible=True)
        )
            
    except Exception as e:
        print(f"Exception in get_clarification_questions: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", "", "", gr.update(visible=False)

async def run_research(query: str, answer1: str, answer2: str, answer3: str):
    """Run the full research process with clarifications"""
    if not all([query.strip(), answer1.strip(), answer2.strip(), answer3.strip()]):
        yield "Please provide answers to all clarification questions."
        return
    
    # Combine the clarifications
    clarifications = f"""Question 1 Response: {answer1}
Question 2 Response: {answer2}
Question 3 Response: {answer3}"""
    
    print(f"Starting research with query: {query}")
    print(f"Clarifications: {clarifications}")
    
    # Run the research process
    try:
        async for chunk in research_manager.run(query, clarifications):
            yield chunk
    except Exception as e:
        print(f"Exception in run_research: {e}")
        import traceback
        traceback.print_exc()
        yield f"Error during research: {str(e)}"

# Test function to verify agents as tools work
def test_agents_as_tools():
    """Test function to verify the agents as tools work"""
    try:
        # Test that the main agent has the tools
        tools = research_manager.main_agent.tools
        tool_names = [tool.name for tool in tools]
        return f"Agents as tools test successful! Tools available: {tool_names}"
    except Exception as e:
        print(f"Agents as tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return f"Agents as tools test failed: {str(e)}"

with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research with Clarification")
    
    with gr.Column():
        # Test button for debugging
        with gr.Row():
            test_button = gr.Button("Test Agents as Tools", variant="secondary")
            test_output = gr.Textbox(label="Test Output", visible=True)
        
        # Initial query input
        gr.Markdown("## Step 1: Enter your research query")
        query_textbox = gr.Textbox(
            label="What topic would you like to research?",
            placeholder="Enter your research question here...",
            lines=3
        )
        clarify_button = gr.Button("Get Clarification Questions", variant="primary")
        
        # Clarification questions section
        with gr.Column(visible=False) as clarification_section:
            gr.Markdown("## Step 2: Answer these clarification questions to refine your research")
            
            with gr.Row():
                with gr.Column():
                    question1 = gr.Textbox(
                        label="Question 1", 
                        interactive=False,
                        lines=2
                    )
                    answer1 = gr.Textbox(
                        label="Your Answer 1", 
                        placeholder="Please provide your detailed answer...",
                        lines=3
                    )
            
            with gr.Row():
                with gr.Column():
                    question2 = gr.Textbox(
                        label="Question 2", 
                        interactive=False,
                        lines=2
                    )
                    answer2 = gr.Textbox(
                        label="Your Answer 2", 
                        placeholder="Please provide your detailed answer...",
                        lines=3
                    )
            
            with gr.Row():
                with gr.Column():
                    question3 = gr.Textbox(
                        label="Question 3", 
                        interactive=False,
                        lines=2
                    )
                    answer3 = gr.Textbox(
                        label="Your Answer 3", 
                        placeholder="Please provide your detailed answer...",
                        lines=3
                    )
            
            research_button = gr.Button("Start Deep Research", variant="primary", size="lg")
        
        # Results section
        gr.Markdown("## Research Progress & Results")
        report = gr.Markdown(
            label="Research Report",
            value="Research results will appear here...",
            elem_id="research-report"
        )
    
    # Event handlers
    test_button.click(
        fn=test_agents_as_tools,
        outputs=[test_output]
    )
    
    clarify_button.click(
        fn=get_clarification_questions,
        inputs=[query_textbox],
        outputs=[question1, question2, question3, clarification_section]
    )
    
    research_button.click(
        fn=run_research,
        inputs=[query_textbox, answer1, answer2, answer3],
        outputs=[report]
    )

if __name__ == "__main__":
    ui.launch(inbrowser=True, debug=True)