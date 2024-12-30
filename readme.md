# RAG-Based Smart Course Search 📚

This project is a RAG (Retrieval-Augmented Generation) based smart course search tool. It allows users to search for courses using natural language queries and provides contextualized responses. The tool is built using Streamlit, LangChain, and various other libraries.

## Features

- Natural language search for courses
- Contextualized responses using RAG
- Integration with FAISS for vector search
- Uses HuggingFace models for embeddings and language generation

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/sasank-sasi/VidhyaQuest

# Create a virtual environment and activate it:

python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

# Install the required packages:

pip install -r requirements.txt

# Usage
Ensure you have the necessary environment variables set up. Create a .env file in the root directory with the following content:
add the GROQ_API_KEY in the .env file ( your groq api key)

--> first run the scraper.py (scrape the details such as courses)
       this will generate a courses.json
--> then run the detail_scraper.py ( scrapes all the deeper details from the course pages)
       this will generate a course_details.json

--> then run the url.py
       make sure the paths were correct for courses.json and course_details.json

--> then run the app.py (starts the streamlit app)
       make sure you replace the file path in the app.py with the course_details.json

# Project Structure
app.py: The main application file containing the Streamlit app and all the logic for loading data, creating embeddings, and performing queries.
courses.json: Contains the basic course information.
course_details.json: Contains detailed information about each course.
requirements.txt: Lists all the dependencies required for the project.

# Live
Run the Streamlit app:
https://analyticsvidya.streamlit.app/
