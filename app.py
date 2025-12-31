"""
GenAI Table Processing - Streamlit Application

A tool for processing tabular data (Excel) using AI to enrich rows with generated content.
"""
import io
import pandas as pd
import streamlit as st
from services.processing import OpenAIProcessingService
from utils.prompt_helper import replace_placeholders, extract_placeholders


# Page configuration
st.set_page_config(
    page_title="GenAI Table Processing",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #a0aec0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .step-container {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 3px solid #667eea;
    }
    .success-banner {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = None
    if 'processing_steps' not in st.session_state:
        st.session_state.processing_steps = []
    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = {"prompt": 0, "completion": 0}
    if 'estimated_cost' not in st.session_state:
        st.session_state.estimated_cost = 0.0


def add_processing_step():
    """Add a new processing step to the configuration."""
    st.session_state.processing_steps.append({
        "prompt": "",
        "output_fields": "",
        "model": "gpt-4o-mini"
    })


def remove_processing_step(index: int):
    """Remove a processing step by index."""
    if 0 <= index < len(st.session_state.processing_steps):
        st.session_state.processing_steps.pop(index)


def process_dataframe(df: pd.DataFrame, steps: list, preview_only: bool = False) -> pd.DataFrame:
    """Process the dataframe with configured steps."""
    try:
        service = OpenAIProcessingService()
    except ValueError as e:
        st.error(f"❌ {str(e)}")
        return df
    
    result_df = df.copy()
    total_prompt_tokens = 0
    total_completion_tokens = 0
    
    # Determine rows to process
    rows_to_process = 1 if preview_only else len(result_df)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for row_idx in range(rows_to_process):
        row_data = result_df.iloc[row_idx].to_dict()
        
        for step_idx, step in enumerate(steps):
            if not step["prompt"] or not step["output_fields"]:
                continue
                
            status_text.text(f"Processing row {row_idx + 1}/{rows_to_process}, step {step_idx + 1}/{len(steps)}...")
            
            # Replace placeholders in prompt
            formatted_prompt = replace_placeholders(step["prompt"], row_data)
            output_fields = [f.strip() for f in step["output_fields"].split(",")]
            
            # Call OpenAI
            result = service.process_item(
                prompt=formatted_prompt,
                output_fields=output_fields,
                model=step["model"]
            )
            
            # Add AI columns to dataframe
            for field, value in result.response.items():
                col_name = f"AI_{field}"
                result_df.at[row_idx, col_name] = str(value) if not isinstance(value, str) else value
                # Update row_data for subsequent steps
                row_data[col_name] = value
            
            # Track token usage
            total_prompt_tokens += result.prompt_tokens
            total_completion_tokens += result.completion_tokens
        
        progress_bar.progress((row_idx + 1) / rows_to_process)
    
    status_text.text("✅ Processing complete!")
    
    # Update session state with token usage
    st.session_state.total_tokens = {
        "prompt": total_prompt_tokens,
        "completion": total_completion_tokens
    }
    st.session_state.estimated_cost = service.estimate_cost(
        total_prompt_tokens, 
        total_completion_tokens,
        steps[0]["model"] if steps else "gpt-4o-mini"
    )
    
    return result_df


def main():
    """Main application entry point."""
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 GenAI Table Processing</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enrich your tabular data with AI-generated content</p>', unsafe_allow_html=True)
    
    # Sidebar - File Upload & Configuration
    with st.sidebar:
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload Excel file",
            type=["xlsx", "xls"],
            help="Upload an Excel file to process"
        )
        
        if uploaded_file:
            st.session_state.df = pd.read_excel(uploaded_file)
            st.success(f"✅ Loaded {len(st.session_state.df)} rows")
            st.write("**Columns:**")
            st.write(", ".join(st.session_state.df.columns.tolist()))
        
        st.divider()
        
        st.header("⚙️ Model Settings")
        default_model = st.selectbox(
            "Default Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
            help="Model to use for processing"
        )
    
    # Main content area
    if st.session_state.df is not None:
        # Data preview
        with st.expander("📊 Data Preview", expanded=True):
            st.dataframe(st.session_state.df.head(10), use_container_width=True)
        
        # Processing Steps Configuration
        st.header("🔧 Processing Steps")
        st.caption("Configure AI processing steps. Use {@ColumnName} to reference data from each row.")
        
        if st.button("➕ Add Processing Step", type="secondary"):
            add_processing_step()
        
        for idx, step in enumerate(st.session_state.processing_steps):
            with st.container():
                st.markdown(f'<div class="step-container">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([3, 1, 0.5])
                
                with col1:
                    st.session_state.processing_steps[idx]["prompt"] = st.text_area(
                        f"Prompt (Step {idx + 1})",
                        value=step["prompt"],
                        placeholder="Analyze this review: {@CustomerReview}. Determine the sentiment.",
                        key=f"prompt_{idx}",
                        height=100
                    )
                    
                    # Show detected placeholders
                    if step["prompt"]:
                        placeholders = extract_placeholders(step["prompt"])
                        if placeholders:
                            st.caption(f"📌 Referenced columns: {', '.join(placeholders)}")
                
                with col2:
                    st.session_state.processing_steps[idx]["output_fields"] = st.text_input(
                        "Output Fields",
                        value=step["output_fields"],
                        placeholder="sentiment, keyPoints",
                        key=f"fields_{idx}",
                        help="Comma-separated field names for AI output"
                    )
                    
                    st.session_state.processing_steps[idx]["model"] = st.selectbox(
                        "Model",
                        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
                        index=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"].index(step["model"]),
                        key=f"model_{idx}"
                    )
                
                with col3:
                    st.write("")
                    st.write("")
                    if st.button("🗑️", key=f"remove_{idx}", help="Remove this step"):
                        remove_processing_step(idx)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Processing Actions
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Preview (1 row)", type="primary", use_container_width=True):
                if st.session_state.processing_steps:
                    with st.spinner("Processing preview..."):
                        st.session_state.processed_df = process_dataframe(
                            st.session_state.df,
                            st.session_state.processing_steps,
                            preview_only=True
                        )
                else:
                    st.warning("⚠️ Add at least one processing step")
        
        with col2:
            if st.button("🚀 Process All", type="primary", use_container_width=True):
                if st.session_state.processing_steps:
                    with st.spinner("Processing all rows..."):
                        st.session_state.processed_df = process_dataframe(
                            st.session_state.df,
                            st.session_state.processing_steps,
                            preview_only=False
                        )
                else:
                    st.warning("⚠️ Add at least one processing step")
        
        with col3:
            if st.session_state.processed_df is not None:
                # Create download buffer
                buffer = io.BytesIO()
                st.session_state.processed_df.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Download Result",
                    data=buffer,
                    file_name="processed_output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        # Results Display
        if st.session_state.processed_df is not None:
            st.divider()
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows Processed", len(st.session_state.processed_df))
            with col2:
                st.metric("Prompt Tokens", f"{st.session_state.total_tokens['prompt']:,}")
            with col3:
                st.metric("Completion Tokens", f"{st.session_state.total_tokens['completion']:,}")
            with col4:
                st.metric("Estimated Cost", f"${st.session_state.estimated_cost:.4f}")
            
            # Result preview
            st.subheader("📋 Processed Results")
            
            # Highlight AI columns
            ai_columns = [col for col in st.session_state.processed_df.columns if col.startswith("AI_")]
            if ai_columns:
                st.caption(f"✨ AI-generated columns: {', '.join(ai_columns)}")
            
            st.dataframe(st.session_state.processed_df, use_container_width=True)
    
    else:
        # Empty state
        st.info("👆 Upload an Excel file in the sidebar to get started!")
        
        with st.expander("📖 How to use", expanded=True):
            st.markdown("""
            ### Quick Start Guide
            
            1. **Upload** an Excel file using the sidebar
            2. **Add processing steps** with prompts that reference your data columns
            3. **Use placeholders** like `{@ColumnName}` to inject row data into prompts
            4. **Preview** with one row to verify the output
            5. **Process all** rows and download the enriched Excel
            
            ### Example Prompt
            ```
            Analyze this customer review: "{@CustomerReview}"
            
            Determine:
            1. The overall sentiment (positive/neutral/negative)
            2. Key points mentioned by the customer
            ```
            
            Output fields: `sentiment, keyPoints`
            """)


if __name__ == "__main__":
    main()
