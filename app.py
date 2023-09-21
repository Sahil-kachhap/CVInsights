import streamlit as st
import PyPDF2
from model import init_llm_response

st.set_page_config(
    page_title="ResumeAI",
    page_icon="📃"
)

def main():
    st.title("ResumeAI 📃")
    st.subheader("Find your next Superstar Employee 🌟")
    st.divider()

    with st.sidebar.expander("**About**"):
        st.markdown("")
    
    with st.sidebar.form(key="my-form"):
        st.markdown("**Google Drive Folder URL**")
        folder_url = st.text_input("Paste your URL here")
        submit_button = st.form_submit_button(label='Submit')
    
    with st.sidebar.expander("**Upload Files**"):
        files = st.file_uploader("Upload Resume Files", accept_multiple_files=True)
        for file in files:
            file_path = f"resume_files/{file.name}"
            pdf_reader = PyPDF2.PdfReader(file)
            page = pdf_reader.pages[0]
            content = page.extract_text()
        
        

    with st.sidebar.expander("**Example**"):
        st.write("Here is a public folder url from my drive containing a collection of sample resume files for testing purpose.")
        st.code("www.google.com")
    
    # clear chat history
    def clear_chat_history():
        st.session_state.messages = []
    st.sidebar.button("Clear Chat History", on_click=clear_chat_history)
    
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{'role':'assistant', 'content': 'Hey there, How can I assist you today.'}]
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Send your message"):
        st.session_state.messages.append({"role": "user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = init_llm_response(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)

if __name__ == "__main__":
    main()