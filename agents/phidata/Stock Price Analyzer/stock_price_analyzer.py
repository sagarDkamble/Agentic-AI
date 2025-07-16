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
finance_agent.print_response("Summarize analyst recommendations for NVDA", stream=True)

import os
import streamlit as st
import markdown2
from xhtml2pdf import pisa
import tempfile


# PDF generation using xhtml2pdf
def generate_pdf(markdown_text, filename="paper.pdf"):
    html = markdown2.markdown(markdown_text)
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pisa.CreatePDF(html, dest=pdf_file)
    return pdf_file.name

# Streamlit UI
st.set_page_config(page_title="Stock Price Analyzer", layout="wide")
st.title("Stock Price Analyzer")
st.markdown("Enter a name of stock.")

topic_input = st.text_input("Enter stock to analyze:")

if st.button("Generate Analysis Report") and topic_input.strip() != "":
    with st.spinner("Synthesizing paper using LLM and tools..."):
        try:
            paper = finance_agent.print_response({"topic": topic_input})
            st.subheader("🧾 Generated Paper:")
            st.markdown(paper)

            # Save to PDF and offer download
            pdf_path = generate_pdf(paper)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download as PDF",
                    data=f,
                    file_name="Anlysis Report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"❌ Error: {e}")
else:
    st.info("🔍 Enter a stock name and click 'Generate Analysis and Recommented summary'")
