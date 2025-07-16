import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
import os

import markdown2
from xhtml2pdf import pisa


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



# PDF generation using xhtml2pdf
def generate_pdf(markdown_text, filename="paper.pdf"):
    html = markdown2.markdown(markdown_text)
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pisa.CreatePDF(html, dest=pdf_file)
    return pdf_file.name

# Streamlit UI
st.set_page_config(page_title="📈 Stock Analysis & Recommendation Agent", layout="wide")
st.title("📄 stock analysis Agent")
st.markdown("Enter a stock name.")

query = st.text_input("Enter your query", "Summarize analyst recommendations for NVDA")

if st.button("Run Agent") and topic_input.strip() != "":
    with st.spinner("Getting response from Finance Agent..."):
        try:
            response = finance_agent.run(query)
            output = response.content       
            
            st.subheader("📋 Agent Response")
            st.markdown(output)

            # Save to PDF and offer download
            pdf_path = generate_pdf(output)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download as PDF",
                    data=f,
                    file_name="Stock Analysis report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"❌ Error: {e}")
else:
    st.info("🔍 Enter a stock name and click on  'Run Agent'")
