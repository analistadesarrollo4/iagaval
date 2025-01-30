import streamlit as st

pg= st.navigation([st.Page("IAgavalChat.py", title= "IAgaval Chat", url_path= "IAgaval"), st.Page("DoAssistant.py", title= "DO Assistant", url_path= "DoAssistant")], position="sidebar", expanded=False)
#st.session_state.clear()
pg.run()