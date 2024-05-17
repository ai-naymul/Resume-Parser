import streamlit as st
import base64
from dotenv import load_dotenv
import google.generativeai as genai
import pdf2image
import io
import os
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


genai.configure(api_key=GOOGLE_API_KEY)


sample_json = """
{ 
  'first_name': 'First name of the candidate',
  'last_name': 'Last name of the cadidate',
  'full_name': 'Full name of the candidate',
  'email': 'Email of that candidate',
  'phone_number': 'Phone number of that candidate',
  'Location': 'Location of that candidate',
  'Address': 'Address of that candidate',
  'Zip_Code': 'Zip code of that address',
  'City': 'City name from the address',
  'Website': 'Website name of that candidate',
  'summary/description': 'Summary or description or career objective of the candidate',
  'Work_history': [
    'current_title': 'Title of the candidate in the company',
    'current_organization': 'Current organization the candidate work on',
  ],

 }
"""




def get_gemini_response(input,pdf_content,prompt):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
    response=model.generate_content([input,pdf_content[0],prompt])
    print(response.text)
    try:
    # Check if 'candidates' list is not empty
        if response.candidates:
            # Access the first candidate's content if available
            if response.candidates[0].content.parts:
                generated_text = response.candidates[0].content.parts[0].text
                return generated_text
            else:
                return "No generated text found in the candidate."
        else:
            return "No candidates found in the response."
    except (AttributeError, IndexError) as e:
        print("Error:", e)


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image
        images=pdf2image.convert_from_bytes(uploaded_file.read())

        first_page=images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")
    

st.set_page_config(page_title="Resume Parser - Using Gemini Pro API")
st.header("Resume Parser")
uploaded_file = st.file_uploader("Upload your resume(Format should be in PDF)",type=["pdf"])


if uploaded_file is not None:
    st.write('Resume Uploaded Successfully')
else:
    st.write('Please Upload Your Resume In PDF Format.')


get_feedback_submit_btn = st.button("Fetch The Data")

feedback_prompt = f"""
You are a expert resume parser you are the best resume parser who can parse reusme smoothly.Your sole purpose is to extract information from the resume to get the specific information about the candidate.You have the resume in pdf format, you have to fetch the data according to the format that I will give to you. I will give you a sample json format, you have to get those data from the data that is relative to the key of the sample json I will give you.Remember don't give me extra information just those which are in the sample json's keys.Also remember give me the response in that json format I will give you. So here is the sample json: {sample_json}.
"""

if get_feedback_submit_btn:
    if uploaded_file is not None:
        pdf_content=input_pdf_setup(uploaded_file)
        response=get_gemini_response(prompt=feedback_prompt,pdf_content=pdf_content)
        st.write(response)
    else:
        st.write("Please uplaod the resume")