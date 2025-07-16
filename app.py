import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
import os

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools

# Create the Finance Agent
finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
            company_news=True
        )
    ],
    instructions=["Use tables to display data"],
    markdown=True,
)

# Streamlit UI
st.title("📈 Stock Analysis & Recommendation Agent")

query = st.text_input("Enter your query", "Summarize analyst recommendations for NVDA")

if st.button("Run Agent"):
    with st.spinner("Getting response from Finance Agent..."):
        response = finance_agent.run(query)
        output = response.output
        if response is None:
            st.error("❌ The agent did not return a response. Check your API key or query.")
        else:
            st.markdown("### 📋 Agent Response")
            st.markdown(output)

        # Save response to PDF
        filename = f"Finance_Agent_Output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = f"{filename}"

        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        y = height - 50
        for line in output.split('\n'):
            if y < 40:
                c.showPage()
                y = height - 50
            c.drawString(40, y, line[:110])
            y -= 15
        c.save()

        # PDF download button
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Response as PDF",
                data=f,
                file_name=filename,
                mime="application/pdf"
            )
