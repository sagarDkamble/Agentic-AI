# app.py
import streamlit as st
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.utilities import SerpAPIWrapper
from tools.swot_tool import swot_tool
from tools.pdf_reader import upload_and_extract
from tools.alpha_vantage_tool import financial_tool
from utils.pdf_export import export_strategy_pdf

import os
from dotenv import load_dotenv
load_dotenv()

# Setup
st.set_page_config(page_title="Business Strategy Consultant", layout="wide")
st.title("🤖 Dynamic Business Strategy Consultant")

# Upload PDF
uploaded_file = st.file_uploader("Upload a business plan or market report (PDF)", type="pdf")
context = upload_and_extract(uploaded_file) if uploaded_file else ""

# Get user input
query = st.text_input("Ask your business strategy question:")

# Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Tools
search = SerpAPIWrapper()
tools = [
    Tool(name="WebSearch", func=search.run, description="Search for market trends or competitors"),
    swot_tool,
    financial_tool
]

# LLM Agent
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

# Agent Execution
if query:
    context_prefixed = f"{context}\n\nUser Query: {query}" if context else query
    response = agent.run(context_prefixed)
    st.markdown("### 📊 Strategy Recommendation:")
    st.write(response)

    if st.button("📤 Export as PDF"):
        export_strategy_pdf(response)
        st.success("Exported strategy.pdf")

