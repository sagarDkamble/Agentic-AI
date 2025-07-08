# agents/research_synthesizer/app.py

import os
import streamlit as st
import markdown2
from xhtml2pdf import pisa
import tempfile

# LangChain
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SerpAPIWrapper
from langchain_community.tools import ArxivQueryRun
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# API keys from Streamlit Secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["SERPAPI_API_KEY"] = st.secrets["SERPAPI_API_KEY"]

# LLM and Tools
llm = ChatOpenAI(model="gpt-4", temperature=0.5)
search = SerpAPIWrapper()
arxiv_tool = ArxivQueryRun()

# Prompt Template
research_paper_prompt = PromptTemplate(
    input_variables=["topic", "search_results", "papers"],
    template="""
You are a professional scientific writer. Using the search and academic data provided below,
generate a concise, well-structured **mini research paper** in academic format.

=========
TOPIC: {topic}

WEB SEARCH RESULTS:
{search_results}

ARXIV PAPER ABSTRACTS:
{papers}
=========

Respond only in this format using clear markdown structure:

# {topic}

## Abstract
...

## 1. Introduction
...

## 2. Recent Advances
...

## 3. Challenges
...

## 4. Future Directions
...

## 5. References
...

Use professional tone and markdown formatting. Keep it precise.
"""
)

# LangChain chain
search_chain = RunnableLambda(lambda x: {"search_results": search.run(x["topic"])})
arxiv_chain = RunnableLambda(lambda x: {"papers": arxiv_tool.run(x["topic"])})
merge_chain = RunnableLambda(lambda inputs: {
    "topic": inputs["topic"],
    "search_results": inputs["search_results"],
    "papers": inputs["papers"]
})

full_chain = (
    RunnablePassthrough.assign(
        search_results=search_chain,
        papers=arxiv_chain
    )
    | merge_chain
    | research_paper_prompt
    | llm
    | StrOutputParser()
)

# PDF generation using xhtml2pdf
def generate_pdf(markdown_text, filename="paper.pdf"):
    html = markdown2.markdown(markdown_text)
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pisa.CreatePDF(html, dest=pdf_file)
    return pdf_file.name

# Streamlit UI
st.set_page_config(page_title="Research Synthesizer Agent", layout="wide")
st.title("📄 Scientific Research Synthesizer Agent")
st.markdown("Enter a topic to generate a mini research paper with AI.")

topic_input = st.text_input("Enter research topic:")

if st.button("Generate Research Paper") and topic_input.strip() != "":
    with st.spinner("Synthesizing paper using LLM and tools..."):
        try:
            paper = full_chain.invoke({"topic": topic_input})
            st.subheader("🧾 Generated Paper:")
            st.markdown(paper)

            # Save to PDF and offer download
            pdf_path = generate_pdf(paper)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download as PDF",
                    data=f,
                    file_name="Research_Paper.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"❌ Error: {e}")
else:
    st.info("🔍 Enter a topic and click 'Generate Research Paper'")

