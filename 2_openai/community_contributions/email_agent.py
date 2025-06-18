import os
from typing import Dict

import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, To
from agents import Agent, function_tool

@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """ Send an email with the given subject and HTML body """
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email("mahadevann.iyerr@maavrus.com") # put your verified sender here
        to_email = To("krisshnaa.iyyer@gmail.com") # put your recipient here
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        print("Email response", response.status_code)
        return {"status": "success", "message": f"Email sent with status code: {response.status_code}"}
    except Exception as e:
        print(f"Email sending failed: {e}")
        return {"status": "error", "message": f"Failed to send email: {str(e)}"}


INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed markdown report. You should use your send_email tool to send one email:
1. Convert the markdown report to clean, well-presented HTML
2. Create an appropriate subject line based on the report content
3. Send the email using the send_email tool

Focus on creating clean HTML formatting that preserves the structure and readability of the report."""

# Email agent is NOT converted to a tool since it's called separately after research completion
email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)