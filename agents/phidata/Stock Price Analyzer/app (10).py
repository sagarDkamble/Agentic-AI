import os
import streamlit as st
import markdown2
from xhtml2pdf import pisa
import tempfile
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools

# Initialize the finance agent
finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    instructions=["Use tables to display data", "Provide comprehensive analysis including stock price, analyst recommendations, company info, and recent news"],
    show_tool_calls=True,
    markdown=True,
)

# PDF generation using xhtml2pdf
def generate_pdf(markdown_text, filename="analysis_report.pdf"):
    """Convert markdown text to PDF"""
    try:
        # Convert markdown to HTML
        html = markdown2.markdown(markdown_text, extras=['tables', 'fenced-code-blocks'])
        
        # Add basic CSS styling for better PDF appearance
        styled_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1, h2, h3 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Stock Analysis Report</h1>
            </div>
            {html}
        </body>
        </html>
        """
        
        # Create temporary PDF file
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        
        # Generate PDF
        pisa_status = pisa.CreatePDF(styled_html, dest=pdf_file)
        pdf_file.close()
        
        if pisa_status.err:
            st.error("Error generating PDF")
            return None
            
        return pdf_file.name
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(
    page_title="Stock Price Analyzer", 
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

st.title("📈 Stock Price Analyzer")
st.markdown("Get comprehensive stock analysis including price data, analyst recommendations, company information, and recent news.")

# Sidebar for additional information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This application provides:
    - Real-time stock prices
    - Analyst recommendations
    - Company information
    - Recent news
    - PDF export functionality
    """)
    
    st.header("Instructions")
    st.markdown("""
    1. Enter a stock symbol (e.g., AAPL, GOOGL, TSLA)
    2. Click 'Generate Analysis Report'
    3. View the analysis
    4. Download as PDF if needed
    """)

# Main input section
col1, col2 = st.columns([3, 1])

with col1:
    stock_symbol = st.text_input(
        "Enter stock symbol to analyze:",
        placeholder="e.g., AAPL, GOOGL, TSLA, NVDA",
        help="Enter a valid stock ticker symbol"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    generate_button = st.button("🔍 Generate Analysis Report", type="primary")

# Analysis section
if generate_button and stock_symbol.strip() != "":
    with st.spinner(f"Analyzing {stock_symbol.upper()}... This may take a moment."):
        try:
            # Create the analysis prompt
            analysis_prompt = f"Provide a comprehensive analysis for {stock_symbol.upper()} including current stock price, analyst recommendations, company information, and recent news. Format the response with clear sections and use tables where appropriate."
            
            # Get the analysis from the agent
            response = finance_agent.run(analysis_prompt)
            
            if response and hasattr(response, 'content'):
                analysis_content = response.content
            else:
                analysis_content = str(response) if response else "No analysis available"
            
            # Display the analysis
            st.subheader(f"📊 Analysis Report for {stock_symbol.upper()}")
            st.markdown(analysis_content)
            
            # PDF download section
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("📥 Generate & Download PDF Report", type="secondary"):
                    with st.spinner("Generating PDF..."):
                        pdf_path = generate_pdf(analysis_content)
                        
                        if pdf_path:
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="📄 Download Analysis Report (PDF)",
                                    data=pdf_file.read(),
                                    file_name=f"{stock_symbol.upper()}_Analysis_Report.pdf",
                                    mime="application/pdf",
                                    type="primary"
                                )
                            
                            # Clean up temporary file
                            try:
                                os.unlink(pdf_path)
                            except:
                                pass
                                
        except Exception as e:
            st.error(f"❌ Error generating analysis: {str(e)}")
            st.markdown("""
            **Possible solutions:**
            - Check if the stock symbol is valid
            - Ensure you have internet connection
            - Try again in a few moments
            """)

elif generate_button and stock_symbol.strip() == "":
    st.warning("⚠️ Please enter a stock symbol before generating the report.")

else:
    st.info("🔍 Enter a stock symbol and click 'Generate Analysis Report' to get started.")
    
    # Example section
    with st.expander("📝 Example Stock Symbols"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Technology:**
            - AAPL (Apple)
            - GOOGL (Google)
            - MSFT (Microsoft)
            - NVDA (NVIDIA)
            """)
            
        with col2:
            st.markdown("""
            **Finance:**
            - JPM (JPMorgan)
            - BAC (Bank of America)
            - WFC (Wells Fargo)
            - GS (Goldman Sachs)
            """)
            
        with col3:
            st.markdown("""
            **Other:**
            - TSLA (Tesla)
            - AMZN (Amazon)
            - META (Meta)
            - NFLX (Netflix)
            """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Stock Price Analyzer - Powered by AI and Real-time Data</div>", 
    unsafe_allow_html=True
)

