import streamlit as st
import pandas as pd
import google.generativeai as genai

def add_gemini_chatbot(df: pd.DataFrame):
    st.subheader("💬 Chat with your data!")

    # Configure the Gemini API key from Streamlit secrets
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"Error configuring the API key: {e}")
        st.stop()

    # Create the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Initialize chat history in session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display prior chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask me anything about the dataset!"):
    # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in the chat
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- Start of Changed Section ---

        # Prepare the data context
        sample_text = df.head(200).to_string()
        summary_text = df.describe().to_string()

        # This is the new, more powerful prompt template for manager-style answers
        manager_prompt_template = f"""
    You are an executive assistant reporting to a busy manager.
    Your task is to answer the question using ONLY the provided data.

    Follow these rules STRICTLY:
    1. Your answer must be the absolute shortest possible. Use the minimum number of characters.
    2. Do not add any introductory phrases like "The answer is...".
    3. Do not explain your reasoning.
    4. If the answer is a number, provide only the number.
    5. If the question about a chart or graph, provide a concise insight based on the dataset you have.


    ---
    DATASET PREVIEW AND STATISTICS:

    Dataset Preview (first 20 rows):
    {sample_text}

    Summary Statistics:
    {summary_text}
    ---

    MANAGER'S QUESTION:
    {prompt}

    ANSWER:
    """
        # --- End of Changed Section ---

        with st.chat_message("assistant"):
            try:
                # Use the new manager_prompt_template instead of the old 'context'
                response = model.generate_content(manager_prompt_template)
                bot_response = response.text.strip() # .strip() removes unwanted whitespace
                st.markdown(bot_response)
            except Exception as e:
                bot_response = f"Error: {e}"
                st.error(bot_response)

        # Save assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

