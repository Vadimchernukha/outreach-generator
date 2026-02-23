"""
Streamlit app for AI Cold Outreach Generator
"""
import os
import sys
import time
import yaml
import pandas as pd
import streamlit as st
import google.generativeai as genai
from datetime import datetime

from core.csv_handler import load_contacts, get_field, build_dynamic_text, save_results, flatten_result
from core.generator import generate_chain
from core.humanizer import humanize


# ─── Page config ────────────────────────────────────
st.set_page_config(
    page_title="AI Outreach Generator",
    page_icon="📧",
    layout="wide"
)


# ─── Load API key ────────────────────────────────────
@st.cache_data
def get_api_key() -> str:
    """Get Gemini API key from environment or secrets."""
    # Try Streamlit secrets first (for cloud deployment)
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    
    # Try environment variable
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        st.error("❌ GEMINI_API_KEY not found. Please set it in Streamlit secrets or environment variables.")
        st.stop()
    return key


# ─── Load client configs ──────────────────────────────
@st.cache_data
def list_clients() -> list[str]:
    """List available client configs."""
    clients_dir = os.path.join(os.path.dirname(__file__), "clients")
    if not os.path.exists(clients_dir):
        return []
    return [
        f.replace(".yaml", "")
        for f in os.listdir(clients_dir)
        if f.endswith(".yaml") and not f.startswith("_")
    ]


def load_config(client_name: str) -> dict:
    """Load client config."""
    clients_dir = os.path.join(os.path.dirname(__file__), "clients")
    path = os.path.join(clients_dir, f"{client_name}.yaml")
    if not os.path.exists(path):
        st.error(f"Client config not found: {path}")
        st.stop()
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─── Process single contact ──────────────────────────
def process_contact(model, row, dynamic_cols: list, config: dict, delay: float, progress_bar=None) -> dict:
    """Process one contact and return result."""
    csv_mapping = config.get("csv_mapping", {})
    language = config.get("language", "english")

    contact = {
        "person_name": get_field(row, "person_name", csv_mapping),
        "title": get_field(row, "title", csv_mapping),
        "company_name": get_field(row, "company_name", csv_mapping),
        "website": get_field(row, "website", csv_mapping),
        "industry": get_field(row, "industry", csv_mapping),
        "company_size": get_field(row, "company_size", csv_mapping),
        "company_country": get_field(row, "company_country", csv_mapping),
        "company_city": get_field(row, "company_city", csv_mapping),
        "dynamic_fields": build_dynamic_text(row, dynamic_cols),
    }

    status_text = f"Processing: {contact['person_name']} | {contact['title']} @ {contact['company_name']}"
    if progress_bar:
        progress_bar.text(status_text)

    # Step 1: Generate raw chain
    try:
        chain = generate_chain(model, contact, config)
    except Exception as e:
        if progress_bar:
            progress_bar.text(f"❌ Error generating: {e}")
        return {"error": str(e), "messages": []}

    time.sleep(delay)

    # Step 2: Humanize each message
    humanized_messages = []
    for msg in chain.get("messages", []):
        step = msg.get("step", "?")
        if progress_bar:
            progress_bar.text(f"{status_text} | Humanizing message {step}...")
        try:
            human_text = humanize(model, msg["text"], language)
        except Exception as e:
            if progress_bar:
                progress_bar.text(f"❌ Error humanizing step {step}: {e}")
            human_text = msg["text"]

        humanized_messages.append({
            "step": msg.get("step", ""),
            "send_after": msg.get("send_after", ""),
            "angle": msg.get("angle", ""),
            "original_text": msg.get("text", ""),
            "humanized_text": human_text,
        })
        time.sleep(delay / 2)

    return {
        "strategy_rationale": chain.get("strategy_rationale", ""),
        "messages": humanized_messages,
    }


# ─── Main UI ──────────────────────────────────────────
def main():
    st.title("📧 AI Cold Outreach Generator")
    st.markdown("Powered by Google Gemini 2.5 Pro")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Client selection
        clients = list_clients()
        if not clients:
            st.error("No client configs found in clients/ folder")
            st.stop()
        
        client_name = st.selectbox("Select Client", clients)
        config = load_config(client_name)
        
        st.info(f"**Company:** {config.get('company_name', 'N/A')}\n\n**Language:** {config.get('language', 'english')}")
        
        # Settings
        st.header("Settings")
        delay = st.slider("Delay between API calls (seconds)", 1.0, 10.0, 4.0, 0.5)
        
        st.markdown("---")
        st.markdown("### 📝 Instructions")
        st.markdown("""
        1. Upload a CSV file with contacts
        2. Click "Generate Outreach" to process
        3. Download results when complete
        """)

    # Main area
    uploaded_file = st.file_uploader(
        "Upload CSV file with contacts",
        type=["csv"],
        help="CSV file should contain contact information (name, title, company, etc.)"
    )

    if uploaded_file is not None:
        # Initialize API
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-pro-preview-06-05")

        # Load contacts
        try:
            # Save uploaded file temporarily
            temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            df, dynamic_cols = load_contacts(temp_path, config)
            
            st.success(f"✅ Loaded {len(df)} contacts")
            st.info(f"Dynamic columns ({len(dynamic_cols)}): {', '.join(dynamic_cols[:5])}{'...' if len(dynamic_cols) > 5 else ''}")
            
            # Show preview
            with st.expander("📋 Preview contacts"):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Process button
            if st.button("🚀 Generate Outreach Messages", type="primary", use_container_width=True):
                # Process all contacts
                all_rows = []
                total = len(df)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, row in df.iterrows():
                    status_text.text(f"Processing contact {idx + 1}/{total}...")
                    progress_bar.progress((idx + 1) / total)
                    
                    result = process_contact(model, row, dynamic_cols, config, delay, status_text)
                    rows = flatten_result(row, result, config.get("csv_mapping", {}))
                    all_rows.extend(rows)
                    
                    time.sleep(delay)
                
                progress_bar.empty()
                status_text.empty()
                
                # Save results
                output_filename = f"results_{client_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                save_results(all_rows, output_filename)
                
                st.success(f"✅ Processing complete!")
                st.info(f"**Contacts processed:** {total}\n\n**Total message rows:** {len(all_rows)}")
                
                # Download button
                with open(output_filename, "rb") as f:
                    st.download_button(
                        label="📥 Download Results CSV",
                        data=f.read(),
                        file_name=output_filename,
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # Show results preview
                with st.expander("📊 Preview Results"):
                    results_df = pd.DataFrame(all_rows)
                    st.dataframe(results_df.head(20), use_container_width=True)
                
                # Cleanup
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(output_filename):
                    # Keep file for download, but note it will be cleaned up on next run
                    pass
            
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.exception(e)
        finally:
            # Cleanup temp file if exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass


if __name__ == "__main__":
    main()
