import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import base64
from datetime import datetime
import os

def get_latest_digest_files():
    """Get the most recent digest files"""
    output_dir = Path("output")
    
    # Find the most recent digest files
    digest_files = {
        'pdf': None,
        'md': None,
        'current_md': None
    }
    
    # Look for current digest files
    current_pdf = output_dir / "digest.pdf"
    current_md = output_dir / "digest.md"
    
    if current_pdf.exists():
        digest_files['pdf'] = current_pdf
    if current_md.exists():
        digest_files['current_md'] = current_md
    
    # Look for dated digest files (most recent)
    pdf_files = list(output_dir.glob("digest-*.pdf"))
    md_files = list(output_dir.glob("digest-*.md"))
    
    if pdf_files and not digest_files['pdf']:
        digest_files['pdf'] = max(pdf_files, key=lambda p: p.stat().st_mtime)
    if md_files and not digest_files['current_md']:
        digest_files['md'] = max(md_files, key=lambda p: p.stat().st_mtime)
    
    return digest_files

def display_digest_content(file_path, file_type):
    """Display digest content based on file type"""
    if not file_path or not file_path.exists():
        return False
    
    try:
        if file_type == 'pdf':
            # Display PDF inline
            with open(file_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Download button
            with open(file_path, "rb") as f:
                st.download_button(
                    f"📥 Download {file_path.name}",
                    f.read(),
                    file_name=file_path.name,
                    mime="application/pdf"
                )
            return True
            
        elif file_type in ['md', 'current_md']:
            # Display Markdown content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Show the markdown content
            st.markdown(content)
            
            # Download button
            with open(file_path, "rb") as f:
                st.download_button(
                    f"📥 Download {file_path.name}",
                    f.read(),
                    file_name=file_path.name,
                    mime="text/markdown"
                )
            return True
            
    except Exception as e:
        st.error(f"Error displaying {file_path.name}: {str(e)}")
        return False

def main():
    st.set_page_config(page_title="📄 Current Digest", layout="wide")
    
    # Get latest digest files
    digest_files = get_latest_digest_files()
    
    # Header
    st.title("📚 Current Digest")
    st.markdown("---")
    
    # Check if we have any current digest
    has_current = any(digest_files.values())
    
    if not has_current:
        st.warning("⚠️ No current digest found. Run the data processing pipeline to generate a new digest.")
        st.info("💡 You can trigger the cloud function to generate a new digest:")
        st.code("curl -X POST https://us-central1-lucky-union-463615-t3.cloudfunctions.net/farmchecker-data-refresh")
        
        # Show archive if available
        show_archive()
        return
    
    # Current Digest Section
    st.subheader("🔥 Latest Digest")
    
    # Create tabs for different formats
    tab1, tab2, tab3 = st.tabs(["📄 PDF Version", "📝 Markdown Version", "📊 Archive"])
    
    with tab1:
        st.markdown("### PDF Digest")
        if digest_files['pdf']:
            display_digest_content(digest_files['pdf'], 'pdf')
        else:
            st.info("No PDF digest available. The digest may be in Markdown format only.")
    
    with tab2:
        st.markdown("### Markdown Digest")
        if digest_files['current_md']:
            display_digest_content(digest_files['current_md'], 'current_md')
        elif digest_files['md']:
            display_digest_content(digest_files['md'], 'md')
        else:
            st.info("No Markdown digest available.")
    
    with tab3:
        show_archive()

def show_archive():
    """Show the digest archive"""
    st.subheader("📚 Digest Archive")
    
    output_dir = Path("output")
    pdf_files = sorted(output_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    md_files = sorted(output_dir.glob("digest-*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    # Show recent digests
    if pdf_files or md_files:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📄 PDF Digests")
            for pdf in pdf_files[:5]:  # Show last 5
                file_time = datetime.fromtimestamp(pdf.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                with st.expander(f"{pdf.name} ({file_time})", expanded=False):
                    display_digest_content(pdf, 'pdf')
        
        with col2:
            st.markdown("#### 📝 Markdown Digests")
            for md in md_files[:5]:  # Show last 5
                file_time = datetime.fromtimestamp(md.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                with st.expander(f"{md.name} ({file_time})", expanded=False):
                    display_digest_content(md, 'md')
    else:
        st.info("No digest files found in the archive.")
    
    # Manual refresh button
    st.markdown("---")
    if st.button("🔄 Generate New Digest"):
        st.info("Generating new digest... This may take a few minutes.")
        # You could add actual digest generation logic here
        st.rerun()

if __name__ == "__main__":
    main() 