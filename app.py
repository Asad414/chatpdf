import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from langchain import OpenAI
from langchain.chains import RetrievalQA
from flask import Flask, render_template, request, send_file, jsonify, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)

def getResponse(query):
    loader = PyPDFLoader("static/output.pdf")
    pages = loader.load_and_split()

    embeddings = OpenAIEmbeddings()

    index = FAISS.from_documents(pages, embeddings)
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        chain_type="stuff",
        retriever=index.as_retriever(),
    )
    return qa.run(query)

def get_next_id():
    with open('users.txt', 'r') as file:
        lines = file.readlines()
        if lines:
            last_id = int(lines[-1].split(',')[0])
            return last_id + 1
        else:
            return 1

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/get_pdf')
def get_pdf():
    pdf_path = 'test.pdf'
    return send_file(pdf_path, as_attachment=True)


@app.route("/chat1")
def chat1():
    return render_template("chat1.html")

@app.route("/get", methods=['POST'])
def get_bot_response():
    data = request.get_json()
    user_message = data['message']
    # Implement your chatbot logic here to generate a response based on the user's message
    chatbot_response = getResponse(user_message)
    return jsonify(chatbot_response)

@app.route('/bot', methods=['POST'])
def upload_file_cv():
    file = request.files.get('file')
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        file.save('data/pdf_file.pdf')

        return render_template("chat1.html")
    return render_template("index.html")

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/signup', methods=['POST'])
def signup1():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        user_id = get_next_id()

        with open('users.txt', 'a') as file:
            file.write(f'{user_id},{name},{email},{password},NO\n')

        return render_template('signup.html', msg="Registered successfuly")

@app.route('/signin')
def signin():
    return render_template('signin.html')
app.run(debug = True)