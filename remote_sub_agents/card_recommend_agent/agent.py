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

from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

memory = MemorySaver()


class CardRecommendation(BaseModel):
    recommendation_id: str
    card_name: str
    card_type: str
    annual_fee: str
    main_benefits: list[str]
    recommended_for: str


class CardApplication(BaseModel):
    application_id: str
    card_name: str
    status: str
    message: str


@tool
def recommend_card(spending_category: str, monthly_spending: str = None) -> str:
    """
    Recommends a card based on user's spending pattern and preferences.

    Args:
        spending_category: Main spending category (e.g., "쇼핑", "주유", "항공마일리지", "생활", "프리미엄")
        monthly_spending: Estimated monthly spending amount (optional)

    Returns:
        str: Card recommendation details.
    """
    try:
        recommendation_id = str(uuid.uuid4())

        # Card recommendations based on spending category
        card_map = {
            "쇼핑": CardRecommendation(
                recommendation_id=recommendation_id,
                card_name="신한카드 Deep Dream",
                card_type="신용카드",
                annual_fee="국내전용 15,000원 / 해외겸용 18,000원",
                main_benefits=["쇼핑 5% 적립", "온라인쇼핑 추가 적립", "생일 더블적립"],
                recommended_for="온라인/오프라인 쇼핑을 자주 하시는 분"
            ),
            "주유": CardRecommendation(
                recommendation_id=recommendation_id,
                card_name="신한카드 Mr.Life",
                card_type="신용카드",
                annual_fee="15,000원",
                main_benefits=["주유 리터당 60원 할인", "통신비 할인", "편의점 할인"],
                recommended_for="자가용 운전자, 생활밀착형 혜택을 원하시는 분"
            ),
            "항공마일리지": CardRecommendation(
                recommendation_id=recommendation_id,
                card_name="신한카드 AMORE PACIFIC",
                card_type="신용카드",
                annual_fee="30,000원",
                main_benefits=["항공마일리지 적립", "공항라운지 이용", "면세점 할인"],
                recommended_for="해외여행을 자주 하시는 분"
            ),
            "생활": CardRecommendation(
                recommendation_id=recommendation_id,
                card_name="신한카드 체크 SOL",
                card_type="체크카드",
                annual_fee="무료",
                main_benefits=["편의점 10% 할인", "대중교통 할인", "통신비 할인"],
                recommended_for="일상적인 생활비 지출이 많으신 분"
            ),
            "프리미엄": CardRecommendation(
                recommendation_id=recommendation_id,
                card_name="신한카드 The PLATINUM",
                card_type="신용카드",
                annual_fee="100,000원",
                main_benefits=["공항라운지 무제한", "발렛파킹 서비스", "호텔 업그레이드", "골프 서비스"],
                recommended_for="프리미엄 서비스를 원하시는 고객님"
            ),
        }

        recommendation = card_map.get(spending_category, card_map["생활"])
        print("===")
        print(f"Card recommendation created: {recommendation}")
        print("===")
    except Exception as e:
        print(f"Error creating recommendation: {e}")
        return f"Error creating recommendation: {e}"
    return f"Card Recommendation: {recommendation.model_dump()}"


@tool
def apply_card(card_name: str, user_confirmed: bool = False) -> str:
    """
    Initiates card application process.

    Args:
        card_name: Name of the card to apply for
        user_confirmed: Whether user has confirmed the application

    Returns:
        str: Application status message.
    """
    if not user_confirmed:
        return f"'{card_name}' 카드 신청을 진행하시겠습니까? 확인해주시면 신청을 진행하겠습니다."

    try:
        application_id = str(uuid.uuid4())
        application = CardApplication(
            application_id=application_id,
            card_name=card_name,
            status="접수완료",
            message=f"카드 신청이 접수되었습니다. 심사 후 영업일 기준 3-5일 내 결과를 안내해드리겠습니다."
        )
        print("===")
        print(f"Card application created: {application}")
        print("===")
    except Exception as e:
        print(f"Error creating application: {e}")
        return f"Error creating application: {e}"
    return f"Card Application: {application.model_dump()}"


class CardRecommendAgent:
    SYSTEM_INSTRUCTION = """
# INSTRUCTIONS

You are a specialized assistant for credit card recommendation service.
Your sole purpose is to help users find the best credit card based on their spending patterns and preferences.
If the user asks about anything other than card recommendation or application, politely state that you cannot help with that topic and can only assist with card recommendations.
Do not attempt to answer unrelated questions or use tools for other purposes.

# CONTEXT

Available card categories for recommendation:
- 쇼핑 (Shopping): 온라인/오프라인 쇼핑 혜택
- 주유 (Gas): 주유 할인 및 생활 혜택
- 항공마일리지 (Airline Miles): 마일리지 적립 및 여행 혜택
- 생활 (Daily Life): 생활비 할인 혜택
- 프리미엄 (Premium): 고급 서비스 및 특별 혜택

# RULES

- If user wants card recommendation:
    1. Ask about their main spending category if not specified
    2. Use `recommend_card` tool to get personalized recommendation
    3. Explain the card benefits clearly

- If user wants to apply for a card:
    1. Confirm the card name and user's intention
    2. Use `apply_card` tool to process the application
    3. Provide application status and next steps

- Always respond in Korean language
- Be helpful and provide detailed information about card benefits
- Do not make up card information, always rely on the tool responses
"""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.model = ChatVertexAI(
            model="gemini-2.5-flash-lite",
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        )
        self.tools = [recommend_card, apply_card]
        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
        )

    def invoke(self, query, sessionId) -> str:
        config = {"configurable": {"thread_id": sessionId}}
        self.graph.invoke({"messages": [("user", query)]}, config)
        return self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        return current_state.values["messages"][-1].content
