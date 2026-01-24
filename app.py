import streamlit as st
import os
from modules.bridge import EngineBridge
from modules.llm import GeminiClient
from modules.graph import GraphVisualizer

# UI Setup
st.set_page_config(page_title="SynthLogos", layout="wide")

st.title("SynthLogos: Neuro-Symbolic RAG Agent")
st.markdown("***Hybrid Architecture: C++ Index (Backend) + Gemini (Reasoning)***")

# sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    st.caption("System Status")
    # checking if backend is compiled
    if os.path.exists("backend/engine.exe") or os.path.exists("backend/engine"):
        st.success("Engine: Online")
    else:
        st.error("Engine: Offline (Binary not found)")

# main logic
query = st.text_input("Enter search query:", placeholder="e.g. How does the Linux kernel handle memory?")

if st.button("Search", type="primary"):
    if not query:
        st.warning("Please type something first.")
    else:
        bridge = EngineBridge()
        # we need the LLM before searching to generate keywords form query
        llm = None
        if api_key:
            llm = GeminiClient(api_key)
        with st.spinner("Analyzing query, Extracting Keywords & Searching C++ Index...(Wait a bit)"):
            # passing the llm object so bridge can use it
            keywords = []
            res,keywords = bridge.search(query, llm_client=llm)
            st.success(f"LLM extracted keywords: {keywords}")
        if not res:
            st.warning("No matches found in the docs.")
        else:
            #  display results & Graph
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Retrieved Context by Searching Keywords")
                for item in res :
                    score_val = float(item['score'])  
                    with st.expander(f"Keyword '{item['keyword']}'---found in '{item['file']}'---(Score: {score_val:.7f})", expanded=False):
                        with st.container(height=200, border=False):
                            # 1. Split the raw string by "..." to get individual hits
                            raw_snippets = item['snippet'].split('...')
                            
                            # 2. Filter out empty strings and clean up whitespace
                            clean_snippets = [s.strip() for s in raw_snippets if s.strip()]
                            
                            # 3. Render each snippet 
                            for s in clean_snippets:
                                st.markdown(f"> -->{s}...")
                                st.divider()
                # Graph Visualization
                st.divider()
                st.subheader("Knowledge Graph")
                
                graph_viz = GraphVisualizer()
                graph_viz.build_from_results(query, res)
                fig = graph_viz.render()
                
                if fig:
                    st.pyplot(fig)
                else:
                    st.info("Not enough data to map graph.")
            
            # LLM Generation
            with col2:
                st.subheader("AI Answer (LLM Compiled the Context based on the Query")
                if not api_key:
                    st.info("Enter API Key to generate answer.")
                else:
                    try:
                        with st.spinner("Synthesizing answer ...(Hold a bit while it is producing correct response)"):
                            # formatting context string for the LLM
                            context_parts = []
                            for r in res:
                                clean_snippet = r['snippet'].replace('... ', '\n... ')
                                context_parts.append(f"[{r['file']}]:\n{clean_snippet}")
                                        
                            context_str = "\n".join(context_parts)
                            answer = llm.query_with_context(query, context_str)
                            st.write(answer)
                    except Exception as e:
                        st.error(f"Failed: {e}")

st.markdown("---")
st.caption("Project by Indranil Saha | C++ Backend (Retrieval Layer) | Python Bridge (The Brain)")