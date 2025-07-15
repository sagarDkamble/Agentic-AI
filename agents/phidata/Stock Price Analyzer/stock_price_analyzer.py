from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools

finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    instructions=["Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)
#finance_agent.print_response("Summarize analyst recommendations for NVDA", stream=True)

import streamlit as st

st.title("Finance Agent")

user_input = st.text_input("Enter your finance query:")

if user_input:
  # The finance_agent is already defined in the preceding code
  response = finance_agent.run(user_input)
  st.markdown(response)
