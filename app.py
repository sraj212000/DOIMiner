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

# Custom CSS for UI Tweaks (Theme Compatible)
st.markdown("""
<style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom Styling for Metric Cards to blend with theme */
    div[data-testid="metric-container"] {
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    /* Button Styling (Theme Neutral/Accent) */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# --- Main Content ---
st.title("🔬 DOIMiner")
st.markdown("#### *Find relevant scientific papers efficiently*")

# --- Configuration (Moved to Expander for Mobile Friendliness) ---
with st.expander("🔍 **Search Configuration & Parameters**", expanded=True):
    st.info("Enter keywords and set filters to find papers relevant to your research.")
    
    keywords_input = st.text_area(
        "Keywords (separated by +)",
        value="CVD+Growth+2D+DFT",
        height=70,
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

# Parse Keywords
keywords = [k.strip() for k in keywords_input.split('+') if k.strip()]

st.markdown("---")

# --- Action Area ---
col_status, col_action = st.columns([3, 1])

with col_status:
    if keywords:
        st.write(f"**Targeting:** `{', '.join(keywords)}`")
    else:
        st.warning("Please enter at least one keyword.")

with col_action:
    start_search = st.button("🚀 Start Search", type="primary")


# --- Search Logic ---
if start_search and keywords:
    progress_bar = st.progress(0)
    status_text = st.empty()
    metrics_placeholder = st.empty()
    
    def update_progress(scanned, matches):
        # Update progress bar
        # Visual scale: just to show activity
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
            height=500
        )
        
        # Download Button
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
        st.warning("No matches found. Try lowering the threshold.")

elif start_search and not keywords:
    st.error("Please provide at least one keyword.")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; opacity: 0.7; font-size: 12px; font-family: "Inter", sans-serif;'>
        <p style='margin-bottom: 5px;'>© 2026 GR-MMG Lab, Department of Chemistry, IIT Bombay</p>
        <p>Developed by <b>Raj Singh</b> at the GR-MMG Lab, under the supervision of <b>Prof. Gopalan Rajaraman</b>.</p>
    </div>
    """,
    unsafe_allow_html=True
)
