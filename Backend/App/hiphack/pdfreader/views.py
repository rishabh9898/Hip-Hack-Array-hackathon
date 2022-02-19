from flask import Flask, request, jsonify, make_response, send_from_directory, send_file
import os
from flask_mysqldb import MySQL
from flask_cors import CORS
from werkzeug.utils import send_from_directory
import PyPDF2
from sentence_transformers import SentenceTransformer, util
import string
import re
import pickle
import json
import torch
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import tempfile
import moviepy.editor as mp
from google.cloud import vision

"""
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sweseek'
app.config['SECRET_KEY'] = 'MySecretKey'
app.config["CLIENT_pdfs"] = "C:/Users/Nick/Desktop/University/CPSC471/Project/SWESeek/backendPython/resumeStorage"

CORS(app)
mysql = MySQL(app)
"""

def preprocess (text):
      str_punctuation=string.punctuation.replace('.','')
      text=text.lower()
      text = re.sub(r'^https?://.[\r\n]', '', text, flags=re.MULTILINE)
      #text = text.translate(str.maketrans('', '', str_punctuation))
      text=" ".join(filter(lambda x:x[0]!='[', text.split()))
      text = text.replace('\n','')
      text= text.replace('\t','')
      text=re.sub(' +', ' ', text)
      return text


def search_papers(title,model,corpus_embeddings,papers):

    query_embedding = model.encode(title + '[SEP]', convert_to_tensor=True)
    search_hits = util.semantic_search(query_embedding, corpus_embeddings)
    search_hits = search_hits[0]  # Get the hits for the first query
    result = []

    #print("Query:", title)
    #print("\nMost similar papers:")

    for hit in search_hits:

        related_paper = papers[hit['corpus_id']]
        result.append({'title': related_paper['title'], 'abstract': related_paper['abstract'], 'url': related_paper['url']})

    return result

def model_reader(text):

    with open("specter.sav", "rb") as f:
        model = pickle.load(f)

    with open('bert_summary_model.sav', "rb") as fi:
        model_1 = pickle.load(fi)

    bert_summary = ''.join(model_1(text, min_length=60))
    dataset_file = 'emnlp2016-2018.json'  # all papers dataset

    if not os.path.exists(dataset_file):
        util.http_get("https://sbert.net/datasets/emnlp2016-2018.json", dataset_file)

    with open(dataset_file) as fIn:
        papers = json.load(fIn)

    title = bert_summary  # input to specter (Paper summary)
    corpus_embeddings = torch.load('tensor_research_papers.pt')
    context = search_papers(title=title, model=model, corpus_embeddings=corpus_embeddings, papers=papers)

    result = {'summary': bert_summary, 'all_papers_details': context}
    return result

#@app.route('/api/signup', methods=['POST'])
def machinelearning():

    path = "nlp_video.mp4"
    #path = request.json['path']
    file_type = path.split('.',1)

    if ((file_type[1].lower() == "jpg") or (file_type[1].lower() == "jpeg") or (file_type[1].lower() == "png")):

        print("1")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'data-cycle-341817-e8ec2ea6c8ca.json'
        client = vision.ImageAnnotatorClient()

        file = open(path ,'rb')
        content = file.read() # read the entire file

        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        docText = response.full_text_annotation.text

        print(docText)

        result = model_reader(docText)
        #return jsonify({'text': docText})

        print(result)

        #return jsonify(result)

    elif (file_type[1].lower() =="mp3" or file_type[1].lower() =="mp4"):

        f1 = open(path, 'rb')

        apikey = 'P4L2u2NeULGbw5DkEQELCXph4119eFNo9XXKa4ku4qVA'
        url = 'https://api.au-syd.speech-to-text.watson.cloud.ibm.com/'
        authenticator = IAMAuthenticator(apikey)
        stt = SpeechToTextV1(authenticator=authenticator)
        stt.set_service_url(url)

        authenticator = IAMAuthenticator(apikey)
        stt = SpeechToTextV1(authenticator=authenticator)
        stt.set_service_url(url)

        if file_type[1].lower() == "mp4":
            transcript = ""

            video = mp.VideoFileClip(path)
            video.audio.write_audiofile('output.mp3')
            with open('output.mp3', 'rb') as fin:
                res = stt.recognize(audio=fin, content_type='audio/mp3', model='en-AU_NarrowbandModel', inactivity_timeout=30).get_result()
                text = [result['alternatives'][0]['transcript'].rstrip() + '.\n' for result in res['results']]
                text = [para[0].title() + para[1:] for para in text]
                transcript = ''.join(text)

        result = model_reader(transcript)


        print(result)
        return

        #return jsonify(result)

    elif file_type[1].lower() == "pdf":

        f1 = open(path, 'rb')

        pdf = PyPDF2.PdfFileReader(f1)
        num_pages = pdf.getNumPages()
        text = ''
        for i in range(num_pages):
            page = pdf.getPage(i)
            text = text + page.extractText()
        text = preprocess(text)
        name = "Refrences"
        #ri = text.find(name)
        #text = text[:ri]

        print(text)

        result = model_reader(text)

        print(result['all_papers_details'][0]['url'])

        #return jsonify(result)


    else:

        return jsonify("Error"), 500



print(machinelearning())
