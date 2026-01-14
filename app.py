import streamlit as st
import pandas as pd
from core import run_search

# --- Page Config & Styling ---
st.set_page_config(
    page_title="DOIMiner - Scientific DOI Discovery",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 700;
    }
    
    /* Custom Button */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* DataFrame Container */
    .stDataFrame {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/microscope.png", width=80)
    st.title("DOIMiner Config")
    st.markdown("---")
    
    st.markdown("### 🔍 Search Parameters")
    
    keywords_input = st.text_area(
        "Keywords (separated by +)",
        value="CVD+Growth+2D+DFT",
        height=100,
        help="Enter keywords separated by '+' symbols. Example: 'CVD+MoS2'"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        threshold = st.number_input(
            "Min Matches",
            min_value=1,
            max_value=10,
            value=2,
            help="Minimum number of keywords that must appear in the title"
        )
    with col2:
        limit = st.number_input(
            "Result Limit",
            min_value=10,
            max_value=5000,
            value=100,
            step=10,
            help="Maximum number of papers to retrieve"
        )
        
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info(
        "DOIMiner extracts DOIs and metadata from Crossref based on keyword matching logic tailored for scientific literature."
    )


# --- Main Content ---
st.title("🔬 DOIMiner: Smart DOI Discovery")
st.markdown("#### *Find relevant scientific papers efficiently*")
st.markdown("---")

# Parse Keywords
keywords = [k.strip() for k in keywords_input.split('+') if k.strip()]

col_status, col_action = st.columns([3, 1])

with col_status:
    if keywords:
        st.write(f"**Targeting:** `{', '.join(keywords)}`")
    else:
        st.warning("Please enter at least one keyword.")

with col_action:
    start_search = st.button("🚀 Start Search", use_container_width=True)


# --- Search Logic ---
if start_search and keywords:
    progress_bar = st.progress(0)
    status_text = st.empty()
    metrics_placeholder = st.empty()
    
    def update_progress(scanned, matches):
        # Update progress bar - arbitrary scale for visual feedback since total scope is large
        # We'll just loop it or cap it at 95% until done
        prog_val = min(scanned / (limit * 50) if limit else 0, 0.95) 
        # Actually standard search space is 50k, but let's just show activity
        progress_bar.progress(min((scanned % 100) / 100.0, 1.0)) 
        status_text.markdown(f"**Scanning...** | Scanned: `{scanned}` | Found: `{matches}`")

    with st.spinner("Mining the literature..."):
        df = run_search(keywords, threshold, limit, progress_callback=update_progress)
    
    progress_bar.progress(100)
    status_text.success("Search Complete!")

    # Display Metrics
    total_found = len(df) if not df.empty else 0
    with metrics_placeholder.container():
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Found", total_found)
        m2.metric("Min Keyword Match", threshold)
        m3.metric("Search Query", "+".join(keywords[:2]) + ("..." if len(keywords)>2 else ""))

    # Display Results
    if not df.empty:
        st.subheader(f"📄 Found Papers ({total_found})")
        st.dataframe(
            df,
            column_config={
                "DOI": st.column_config.LinkColumn("DOI Link"),
                "Year": st.column_config.NumberColumn("Year", format="%d"),
            },
            use_container_width=True,
            height=600
        )
        
        # Download Button
        # Check if openpyxl is installed for excel; else CSV
        try:
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            st.download_button(
                label="📥 Download Excel Report",
                data=buffer.getvalue(),
                file_name="doiminer_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except ImportError:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Report",
                data=csv,
                file_name="doiminer_results.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.info("Install `openpyxl` for Excel downloads.")
            
    else:
        st.warning("No papers found matching your criteria. Try lowering the threshold or changing keywords.")

elif start_search and not keywords:
    st.error("Please provide at least one keyword.")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px; font-family: "Inter", sans-serif;'>
        <p style='margin-bottom: 5px;'>© 2026 GR-MMG Lab, Department of Chemistry, IIT Bombay</p>
        <p>Developed by <b>Raj Singh</b> at the GR-MMG Lab, under the supervision of <b>Prof. Gopalan Rajaraman</b>.</p>
    </div>
    """,
    unsafe_allow_html=True
)
