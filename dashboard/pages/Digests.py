import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import base64

st.set_page_config(page_title="📄 Digests & Reviews", layout="wide")
st.title("📚 Digest & Review Archive")

output_dir = Path("output")
pdf_files = sorted(output_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)

if not pdf_files:
    st.info("No PDFs generated yet.")
else:
    st.markdown("### All Digests & Reviews")
    for pdf in pdf_files:
        with st.expander(f"{pdf.name} (Generated: {pdf.stat().st_mtime_ns // 1_000_000_000})", expanded=False):
            # Inline PDF viewer using base64
            with open(pdf, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            st.download_button("Download PDF", pdf.read_bytes(), file_name=pdf.name)
    
    st.caption("Scroll and expand any digest to view it inline. Use the download button to save a copy.") 