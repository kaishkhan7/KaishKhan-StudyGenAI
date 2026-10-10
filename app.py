
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

load_dotenv()

st.set_page_config(
    page_title="StudyGen AI",
    page_icon="🎓",
    layout="wide"
)


st.title("🎓 Kaish Khan's StudyGen AI")
st.subheader("Your Personal AI Study Assistant 🤖")
st.caption("Developed by Kaish Khan | B.Tech CSE AI & ML")

st.write("Upload PDF or photos of your notes and learn with AI.")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API key nahi mili. .env file check karo.")
    st.stop()

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.8-flash"
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 AI Model")
st.sidebar.write(MODEL)
st.sidebar.markdown("---")
st.sidebar.caption("Created by Kaish Khan ❤️")

uploaded_files = st.file_uploader(
    "📚 Upload PDF or Notes Photos",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

document_parts = []

if uploaded_files:

    for uploaded_file in uploaded_files:

        if uploaded_file.type == "application/pdf":
            try:
                reader = PdfReader(uploaded_file)

                for page_number, page in enumerate(
                    reader.pages, start=1
                ):
                    page_text = page.extract_text() or ""

                    if page_text.strip():
                        document_parts.append(
                            f"File: {uploaded_file.name}, "
                            f"Page {page_number}\n{page_text}"
                        )

            except Exception:
                st.warning(
                    f"{uploaded_file.name} read nahi hui."
                )

        elif uploaded_file.type.startswith("image/"):
            document_parts.append({
                "name": uploaded_file.name,
                "mime_type": uploaded_file.type,
                "data": uploaded_file.getvalue()
            })

    st.success(f"{len(uploaded_files)} file(s) selected!")

    for file in uploaded_files:
        st.write("📄", file.name)

    text_content = "\n\n".join(
        part for part in document_parts
        if isinstance(part, str)
    )[:20000]

    image_parts = [
        part for part in document_parts
        if isinstance(part, dict)
    ]

    if not text_content.strip() and not image_parts:
        st.warning(
            "Readable text nahi mila. "
            "Text-based PDF ya clear photo try karo."
        )
        st.stop()

    def ask_ai(task):
        prompt = f"""

You are Kaish Khan's StudyGen AI tutor.

Give direct, accurate and concise answers.
Use simple English and short headings.
For theory, explain in exam-ready points.
For MCQs, give clear options and an answer key.
Avoid unnecessary introductions and repetition.
Use only the provided study material when relevant.


STUDENT TASK:
{task}

PDF TEXT:
{text_content}
"""

        contents = [prompt]

        for image_info in image_parts:
            contents.append(
                genai.types.Part.from_bytes(
                    data=image_info["data"],
                    mime_type=image_info["mime_type"]
                )
            )

        response = client.models.generate_content(
            model=MODEL,
            contents=contents
        )

        return response.text or "AI response nahi mila."

    tab1, tab2, tab3 = st.tabs(
        ["💬 Ask AI", "📝 Summary", "❓ MCQs"]
    )

    with tab1:
        question = st.text_input(
            "Apna question likho",
            placeholder="Explain these notes in simple words..."
        )

        if st.button("Ask AI"):
            if question.strip():
                try:
                    with st.spinner("AI answer bana raha hai..."):
                        answer = ask_ai(question)

                    st.markdown(answer)

                except Exception as error:
                    st.error("AI request fail hui.")
                    st.code(str(error))
            else:
                st.warning("Pehle question likho.")

    with tab2:
        if st.button("Generate Summary"):
            try:
                with st.spinner("Summary ban rahi hai..."):
                    summary = ask_ai(
                        "Create clear study notes with "
                        "important definitions and examples."
                    )

                st.markdown(summary)

                st.download_button(
                    "Download Summary",
                    summary,
                    file_name="study_notes.md"
                )

            except Exception as error:
                st.error("Summary generate nahi hui.")
                st.code(str(error))

    with tab3:
        number = st.slider(
            "Number of MCQs", 3, 10, 5
        )

        if st.button("Generate MCQs"):
            try:
                with st.spinner("MCQs ban rahe hain..."):
                    quiz = ask_ai(
                        f"Generate {number} MCQs from these notes. "
                        "Give four options per question, one correct "
                        "answer, and explanations in an answer key."
                    )

                st.markdown(quiz)

                st.download_button(
                    "Download MCQs",
                    quiz,
                    file_name="study_mcqs.md"
                )

            except Exception as error:
                st.error("MCQs generate nahi hue.")
                st.code(str(error))

else:
    st.info("Pehle PDF ya notes ki photo upload karo.")

st.divider()
st.markdown(
    "<div style='text-align:center;'>"
    "<h4>🎓 Kaish Khan's StudyGen AI</h4>"
    "<p>Built with ❤️ by Kaish Khan</p>"
    "<p>B.Tech CSE | AI & ML</p>"
    "</div>",
    unsafe_allow_html=True
)
