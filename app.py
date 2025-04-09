import streamlit as st
# Remove the direct import of streamlit_oauth as it's now handled in the component
# import streamlit_oauth
from components.auth import authenticate_google # Import the new function

# --- Remove Google OAuth Configuration loading --- 
# The following lines are moved to components/auth.py
# try:
#     client_id = st.secrets["google_oauth"]["client_id"]
#     client_secret = st.secrets["google_oauth"]["client_secret"]
#     redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
# except KeyError:
#     st.error("Google OAuth credentials not found in secrets.toml.")
#     st.info("Please create a `.streamlit/secrets.toml` file with your Google Client ID, Client Secret, and Redirect URI.")
#     st.stop()
# except FileNotFoundError:
#      st.error("Secrets file not found.")
#      st.info("Please create a `.streamlit/secrets.toml` file in your project root.")
#      st.stop()


# --- Call the Authentication Function from the component ---
# user_info = streamlit_oauth.google_oauth(...)
# user_info = authenticate_google()

# --- App Logic ---
st.title("Learnify Your Personal Tutor")

# --- Tabbed Interface ---
tab1, tab2, tab3 = st.tabs(["📄 Document Uploader", "⚙️ Settings", "📚 Learn"])

with tab1:
    st.header("Document Uploader")
    st.write("Upload your PDF documents here for analysis.")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    # Store uploaded file in session state
    if uploaded_file is not None:
        # Read the file content
        file_content = uploaded_file.read()
        
        # Store both the file content and name in session state
        st.session_state.uploaded_file = {
            "content": file_content,
            "name": uploaded_file.name
        }
        
        # Display file info
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
        # Display PDF statistics
        from components.pdf_stats import get_pdf_statistics
        try:
            stats = get_pdf_statistics(file_content)
            st.subheader("Document Statistics")
            st.write(f"Total Pages: {stats['total_pages']}")
            st.write(f"Total Images: {stats['total_images']}")
            st.write(f"Total Text Blocks: {stats['total_text_blocks']}")
            st.write(f"Total Lines: {stats['total_lines']}")
            st.write(f"Total Words: {stats['total_words']}")
            st.write(f"Total Characters: {stats['total_characters']}")
            
            # Display metadata if available
            if stats['metadata']:
                st.subheader("Document Metadata")
                for key, value in stats['metadata'].items():
                    if value:  # Only display non-empty metadata
                        st.write(f"{key}: {value}")
        except Exception as e:
            st.error(f"Error analyzing PDF: {str(e)}")
        
        # Reset the file uploader
        uploaded_file = None
    
    # Display current file info if exists
    if 'uploaded_file' in st.session_state:
        st.info(f"Current file: {st.session_state.uploaded_file['name']}")
    
    # Add a clear button
    if st.button("Clear Uploaded File"):
        if 'uploaded_file' in st.session_state:
            del st.session_state.uploaded_file
            st.success("File cleared successfully!")

with tab2:
    st.header("Settings")
    st.subheader("LLM Provider")
    st.info("Currently using OpenAI GPT-4 Turbo for content generation.")
    
    # Check if a file is uploaded
    if 'uploaded_file' not in st.session_state:
        st.warning("Please upload a PDF file in the Document Uploader tab first.")
        st.stop()
    
    # Page numbers of interest
    st.subheader("Pages of Interest")
    page_numbers = st.text_input(
        "Enter page numbers (e.g., '1-5' or '1,3,5' or '1-3,5-7')",
        help="Specify the pages you want to focus on. Use ranges with '-' or individual pages with ','"
    )
    
    # Store page numbers in session state
    if page_numbers:
        st.session_state.page_numbers = page_numbers
    
    # Content Generation Options
    st.subheader("Content Generation")
    options = st.multiselect(
        "Select content types to generate",
        ["Generate a quick summary", "Create a quick Quiz", "Create a set of analytics questions"],
        default=["Generate a quick summary"]
    )
    
    # Generate Content Button
    if st.button("Generate Content"):
        if not page_numbers:
            st.warning("Please enter page numbers first.")
        elif not options:
            st.warning("Please select at least one content type to generate.")
        else:
            try:
                # Extract text from PDF
                from components.pdf_extractor import extract_text_from_pages
                extracted_text = extract_text_from_pages(
                    st.session_state.uploaded_file["content"],
                    st.session_state.page_numbers
                )
                
                # Initialize content dictionary
                generated_content = {}
                
                # Generate content based on selected options
                if "Generate a quick summary" in options:
                    from components.summarizer import generate_summary
                    summary = generate_summary(extracted_text)
                    generated_content["summary"] = summary
                
                if "Create a quick Quiz" in options:
                    from components.quiz_generator import generate_quiz
                    quiz = generate_quiz(extracted_text)
                    generated_content["quiz"] = quiz
                
                if "Create a set of analytics questions" in options:
                    from components.analytics_questions import generate_analytics_questions
                    analytics = generate_analytics_questions(extracted_text)
                    generated_content["analytics"] = analytics
                
                # Store in session state
                st.session_state.generated_content = generated_content
                st.success("Content generated successfully! Check the Learn tab to view the results.")
                
            except Exception as e:
                st.error(f"Error generating content: {str(e)}")

with tab3:
    st.header("Learn")
    st.write("Explore and interact with your learning materials here.")
    
    # Add a section for generated content
    st.subheader("Generated Content")
    
    # Display generated content
    if 'generated_content' in st.session_state:
        # Display summary if available
        if "summary" in st.session_state.generated_content:
            summary_content = st.session_state.generated_content["summary"]
            st.markdown("### Summary")
            st.write(summary_content["content"])
            st.info(f"Generated using {summary_content['metadata'].get('provider', 'unknown').capitalize()} ({summary_content['metadata'].get('model', 'unknown')})")
            st.markdown("---")
        
        # Display quiz if available
        if "quiz" in st.session_state.generated_content:
            quiz_content = st.session_state.generated_content["quiz"]
            st.markdown("### Quiz")
            
            # Initialize session state for quiz if not exists
            if 'quiz_answers' not in st.session_state:
                st.session_state.quiz_answers = {}
            
            # Display each question and collect answers
            for i, question in enumerate(quiz_content["content"]["questions"]):
                st.markdown(f"#### Question {i + 1}")
                st.write(question["question"])
                
                # Create radio buttons for options
                answer = st.radio(
                    "Select your answer:",
                    options=question["options"],
                    key=f"quiz_question_{i}",
                    index=None
                )
                
                # Store the answer
                if answer:
                    st.session_state.quiz_answers[str(i)] = answer[0]  # Store just the letter (A, B, C, D)
            
            # Submit button
            if st.button("Submit Quiz"):
                from components.quiz_generator import evaluate_quiz
                results = evaluate_quiz(quiz_content["content"], st.session_state.quiz_answers)
                
                # Display results
                st.markdown("### Quiz Results")
                st.write(f"Total Questions: {results['total_questions']}")
                st.write(f"Correct Answers: {results['correct_answers']}")
                st.write(f"Score: {results['percentage']:.1f}%")
                
                # Show correct answers
                st.markdown("### Correct Answers")
                for i, question in enumerate(quiz_content["content"]["questions"]):
                    st.write(f"Question {i + 1}: {question['correct_answer']}")
            
            st.info(f"Generated using {quiz_content['metadata'].get('provider', 'unknown').capitalize()} ({quiz_content['metadata'].get('model', 'unknown')})")
            st.markdown("---")
        
        # Display analytics questions if available
        if "analytics" in st.session_state.generated_content:
            analytics_content = st.session_state.generated_content["analytics"]
            st.markdown("### Analytical Questions")
            
            # Initialize session state for analytics answers if not exists
            if 'analytics_answers' not in st.session_state:
                st.session_state.analytics_answers = {}
            
            # Display each question and collect answers
            for i, question in enumerate(analytics_content["content"]["questions"]):
                st.markdown(f"#### Question {i + 1}")
                st.write(question["question"])
                st.write("Evaluation Criteria:")
                for criterion in question["evaluation_criteria"]:
                    st.write(f"- {criterion}")
                
                # Create text area for answer
                answer = st.text_area(
                    "Type your answer here:",
                    key=f"analytics_question_{i}",
                    height=150
                )
                
                # Store the answer
                if answer:
                    st.session_state.analytics_answers[str(i)] = {
                        "answer": answer,
                        "criteria": question["evaluation_criteria"]
                    }
            
            # Submit button for analytics questions
            if st.button("Submit Answers"):
                from components.analytics_questions import evaluate_answer
                provider = st.session_state.get('llm_provider', 'openai')
                
                # Evaluate each answer
                for i, answer_data in st.session_state.analytics_answers.items():
                    question = analytics_content["content"]["questions"][int(i)]["question"]
                    evaluation = evaluate_answer(
                        question,
                        answer_data["answer"],
                        answer_data["criteria"],
                        provider
                    )
                    
                    # Display evaluation results
                    st.markdown(f"### Evaluation for Question {int(i) + 1}")
                    st.write(f"Score: {evaluation['score']}/100")
                    st.markdown("#### Feedback")
                    st.write(evaluation["feedback"])
                    st.markdown("#### Suggestions for Improvement")
                    for suggestion in evaluation["suggestions"]:
                        st.write(f"- {suggestion}")
                    st.markdown("#### Model Answer")
                    st.write(evaluation["model_answer"])
                    st.markdown("---")
            
            st.info(f"Generated using {analytics_content['metadata'].get('provider', 'unknown').capitalize()} ({analytics_content['metadata'].get('model', 'unknown')})")
    else:
        st.info("No content generated yet. Go to Settings tab to generate content from your uploaded PDF.")

st.markdown("---") # Separator before logout

# Example: Logout button (optional, clears session state)

# You can add more app content outside the login check if needed
st.markdown("---")
st.write("Copyright Thili.net Evron Technologies")
