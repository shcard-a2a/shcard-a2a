from .master_agent import MasterAgent
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

root_agent = MasterAgent(
    remote_agent_addresses=[
        os.getenv("CARD_RECOMMEND_AGENT_URL", "http://localhost:10000"),
        os.getenv("TRANSACTION_AGENT_URL", "http://localhost:10001"),
    ]
).create_agent()
