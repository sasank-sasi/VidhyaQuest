import streamlit as st
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Verify API key loading
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("GROQ_API_KEY environment variable not set.")
    st.stop()

# Load dataset
@st.cache_data
def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Create embeddings and FAISS index
@st.cache_resource
def create_faiss_index(courses):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    texts = [f"{course['title']} {course['description']}" for course in courses]
    metadata = [{"title": course['title'], "url": course.get('url', 'N/A')} for course in courses]
    vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadata)
    return vector_store

# RAG-based retrieval
def perform_query(query, retriever):
    chat = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="mixtral-8x7b-32768",
        temperature=0.7
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant and you need provide the response relates to artificial intelligence every user input should be related to it. Please provide short passage"),
        ("human", "{text}")
    ])
    chain = prompt | chat
    response = chain.invoke({"text": query})
    return response.content

# Streamlit App
def main():
    st.title("RAG Smart Course Search For Analytics Vidhya")
    st.write("Search for courses using natural language queries with RAG!")

    # Load dataset and create FAISS index
    courses = load_data("course_details.json")
    vector_store = create_faiss_index(courses)

    # Generate suggestions from course titles and descriptions
    course_suggestions = [course['title'] for course in courses] + [
        course['description'][:50] for course in courses if 'description' in course
    ]

    # Input query
    query = st.text_input("Enter your search query:")
    if query:
        # Autocomplete: Filter suggestions based on input
        #suggestions = [suggestion for suggestion in course_suggestions if suggestion.lower().startswith(query.lower())]


        # Perform search
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        response = perform_query(query, retriever)

        # Display results
        st.subheader("Response:")
        st.write(response)

        st.subheader("Relevant Courses:")
        for doc in retriever.get_relevant_documents(query):
            course = next((course for course in courses if course['title'] == doc.metadata['title']), None)
            if course:
                st.markdown(f"**Title:** [{course['title']}]({course.get('url', 'N/A')})")
                st.markdown(f"**Description:** {course.get('description', 'View course for more details')}")
                st.markdown(f"**Instructor:** {course.get('instructor', 'View course for more details')}")
                st.markdown(f"**Duration:** {course['stats'].get('duration', 'N/A')}")
                st.markdown(f"**Level:** {course['stats'].get('level', 'N/A')}")
                st.markdown(f"**Rating:** {course['stats'].get('rating', 'N/A')}")

if __name__ == "__main__":
    main()
