"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pydantic import BaseModel
import uuid
from crewai import Agent, Crew, LLM, Task, Process
from crewai.tools import tool
from dotenv import load_dotenv
import litellm
import os

load_dotenv()

litellm.vertex_project = os.getenv("GOOGLE_CLOUD_PROJECT")
litellm.vertex_location = os.getenv("GOOGLE_CLOUD_LOCATION")


class TransactionRequest(BaseModel):
    request_id: str
    period: str
    delivery_method: str
    email: str | None = None
    phone: str | None = None


class TransactionResponse(BaseModel):
    request_id: str
    status: str
    message: str


@tool("send_transaction_history")
def send_transaction_history(period: str, delivery_method: str, email: str = None, phone: str = None) -> str:
    """
    Sends transaction history to the user via specified delivery method.

    Args:
        period: The period for transaction history (e.g., "1개월", "3개월", "6개월", "1년")
        delivery_method: The delivery method ("이메일" or "SMS")
        email: Email address if delivery_method is "이메일"
        phone: Phone number if delivery_method is "SMS"

    Returns:
        str: A message indicating that the transaction history has been sent.
    """
    try:
        request_id = str(uuid.uuid4())
        request = TransactionRequest(
            request_id=request_id,
            period=period,
            delivery_method=delivery_method,
            email=email,
            phone=phone
        )
        print("===")
        print(f"Transaction history request created: {request}")
        print("===")

        response = TransactionResponse(
            request_id=request_id,
            status="completed",
            message=f"{period} 거래내역이 {delivery_method}로 발송되었습니다."
        )
    except Exception as e:
        print(f"Error sending transaction history: {e}")
        return f"Error sending transaction history: {e}"
    return f"Transaction request {response.model_dump()} has been completed"


class TransactionAgent:
    TaskInstruction = """
# INSTRUCTIONS

You are a specialized assistant for card transaction history service.
Your sole purpose is to help users request and receive their card transaction history.
If the user asks about anything other than transaction history, politely state that you cannot help with that topic and can only assist with transaction history requests.
Do not attempt to answer unrelated questions or use tools for other purposes.

# CONTEXT

Received user query: {user_prompt}
Session ID: {session_id}

Available transaction history periods:
- 1개월 (1 month)
- 3개월 (3 months)
- 6개월 (6 months)
- 1년 (1 year)

Available delivery methods:
- 이메일 (Email)
- SMS

# RULES

- If user wants to request transaction history, follow this order:
    1. Ask for the desired period if not specified
    2. Ask for the delivery method (이메일 or SMS) if not specified
    3. Ask for the email address or phone number based on the delivery method
    4. Confirm the request details with the user
    5. Use `send_transaction_history` tool to process the request
    6. Finally, provide response to the user about the request details and confirmation

- Set response status to input_required if asking for user information or confirmation.
- Set response status to error if there is an error while processing the request.
- Set response status to completed if the request is complete.
- Always respond in Korean language.
"""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def invoke(self, query, sessionId) -> str:
        model = LLM(
            model="vertex_ai/gemini-2.5-flash-lite",
        )
        transaction_agent = Agent(
            role="Transaction History Agent",
            goal=(
                "Help user to request and receive their card transaction history via email or SMS."
            ),
            backstory=("You are an expert and helpful card transaction history service agent."),
            verbose=False,
            allow_delegation=False,
            tools=[send_transaction_history],
            llm=model,
        )

        agent_task = Task(
            description=self.TaskInstruction,
            agent=transaction_agent,
            expected_output="Response to the user in friendly and helpful manner in Korean",
        )

        crew = Crew(
            tasks=[agent_task],
            agents=[transaction_agent],
            verbose=False,
            process=Process.sequential,
        )

        inputs = {"user_prompt": query, "session_id": sessionId}
        response = crew.kickoff(inputs)
        return response


if __name__ == "__main__":
    agent = TransactionAgent()
    result = agent.invoke("최근 3개월 거래내역을 이메일로 보내주세요", "default_session")
    print(result)
