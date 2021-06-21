from django.http import HttpResponse
from django.shortcuts import render
from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime
from django.contrib.auth.models import User
import csv
from django.shortcuts import render, redirect
from .forms import CreateForm
import pickle
import pandas as pd
import torch
from sentence_transformers import util
import PyPDF2
import os
from PyPDF2 import PdfFileReader
import json
import re,string
from google.cloud import vision
import io 
import subprocess
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import moviepy.editor as mp
import tempfile



# Class defined which holds attributes of the input provided by the users
class Paper_Data:
	description = ""
	similarity = ""
	organization = ""
	url = ""
	count = ""
	def __init__(self, description, similarity, organization,url,count):
		self.description = description
		self.similarity = similarity
		self.organization = organization
		self.url = url
		self.count = count

# Opens the home page 

def index(request):
	return render(request,'pdfreader/landing.html')


charities = []


def search_papers(title,model,corpus_embeddings,papers):
  query_embedding = model.encode(title+'[SEP]', convert_to_tensor=True)  # Converts input data to tensors

  data_dict = {}   # Creating a dictionary to be passed to the html page

  count = 0

  search_hits = util.semantic_search(query_embedding, corpus_embeddings)  #
  search_hits = search_hits[0]  #Get the hits for the first query
  paper_list = []
  match_list =[]

  # print("Query:", title)
  # print("\nMost similar papers:")
  for hit in search_hits:
  	count+=1
  	related_paper = papers[hit['corpus_id']]
  	print(str(count)+". "+related_paper['title'])
  	# print(related_paper['abstract'])
  	# print(related_paper['url']+".pdf")
  	x = Paper_Data(related_paper['abstract'],str(100*float(format(search_hits[count-1]['score'],".2f"))),related_paper['title'],related_paper['url']+".pdf",str(count))
  	if count<4:
  		match_list.append(x)
  	else:
  		paper_list.append(x)
  data_dict['paper_list'] = paper_list
  data_dict['match_list'] = match_list

  print(len(match_list),len(paper_list))
  return data_dict


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

def model_reader(text):
	with open("pdfreader/paper_model","rb") as f:
					model = pickle.load(f)
	with open('pdfreader/bert_summary_model',"rb") as fi:
		model_1= pickle.load(fi)

	bert_summary = ''.join(model_1(text, min_length=60))
	dataset_file = 'emnlp2016-2018.json'

	if not os.path.exists(dataset_file):
		util.http_get("https://sbert.net/datasets/emnlp2016-2018.json", dataset_file)

	with open(dataset_file) as fIn:
		papers = json.load(fIn)

	title = bert_summary
	corpus_embeddings = torch.load('pdfreader/tensor_research_papers.pt')
	context = search_papers(title=title,model= model,corpus_embeddings=corpus_embeddings,papers = papers)
	context['summary'] = title
	return context


def add_items(request):
	if request.method =='POST':
		form = CreateForm(request.POST, request.FILES)
		if form.is_valid():
			f1 = request.FILES['PDF']
			print(type(f1))
			# print(type(f1['PDF']))
			# print("RESULT IS HERE !!!!!",  f1['PDF'])
			sentence = str(f1)
			file=sentence.rsplit('.', 1)
			file_type=file[1]
			# print(f1['PDF'])
			# print(type(f1['PDF']))
			print(file_type)
			# ff1 = f1['PDF']

			if ((file_type.lower()=="jpg") or (file_type.lower()=="jpeg") or (file_type.lower()=="png")):
				print("1")
				os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'pdfreader/seismic-diorama-316110-5569927e0d86.json'
				client = vision.ImageAnnotatorClient()


				# open(f1['PDF'] ,'rb') as image_file:

				content = f1.read()

				image = vision.Image(content=content)
				response = client.document_text_detection(image=image)

				docText = response.full_text_annotation.text
				print(docText)
				print("rendering new page....")
				return render(request,'pdfreader/results.html',model_reader(docText))




			elif file_type.lower() =="pdf":
				print("2")
				pdf = PyPDF2.PdfFileReader(f1)
				num_pages= pdf.getNumPages()
				text=''
				for i in range(num_pages):
					page=pdf.getPage(i)
					text=text+page.extractText()
				text = preprocess(text)
				name = "Refrences"
				ri = text.find(name)
				text = text[:ri]
				text.find("Refrences")
				print("rendering new page....")
				return render(request,'pdfreader/results.html',model_reader(text))



			elif (file_type.lower() =="mp3" or file_type.lower() =="mp4") :
				print("3")
				apikey = 'mUFzo-xMwW8Ix-J1GSFreZ-gFMGEpvjafNLkAQN0WCoH'
				url = 'https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/35437128-dcf1-4cc7-946c-c4d4b608ba4b'
				authenticator = IAMAuthenticator(apikey)
				stt = SpeechToTextV1(authenticator=authenticator)
				stt.set_service_url(url)
				print("Second time ",type(f1))

				authenticator = IAMAuthenticator(apikey)
				stt = SpeechToTextV1(authenticator=authenticator)
				stt.set_service_url(url)

				if file_type.lower() =="mp4":
					transcript =""
					with tempfile.TemporaryDirectory() as tmpdirname:
						video = mp.VideoFileClip(f1.temporary_file_path())
						video.audio.write_audiofile(str(tmpdirname) + '\\output.mp3')
						with open(str(tmpdirname) + '\\output.mp3', 'rb') as fin:
							res = stt.recognize(audio=fin, content_type='audio/mp3', model='en-AU_NarrowbandModel', continuous=True).get_result()
							text = [result['alternatives'][0]['transcript'].rstrip() + '.\n' for result in res['results']]
							text = [para[0].title() + para[1:] for para in text]
							transcript = ''.join(text)
							with open('output.txt', 'w') as out:
							    out.writelines(transcript)
							    print(transcript)
							# print(transcript)

							
					print("rendering new page....")
					return render(request,'pdfreader/results.html',model_reader(transcript))


					# fp = tempfile.TemporaryFile()
					# # print(f1.temporary_file_path())
					
					# f1 = video.audio
					# fp.write(b(f1))

				# authenticator = IAMAuthenticator(apikey)
				# stt = SpeechToTextV1(authenticator=authenticator)
				# stt.set_service_url(url)
				# with open("D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\nlp.mp3", 'rb') as f:
				res = stt.recognize(audio=f1, content_type='audio/mp3', model='en-AU_NarrowbandModel', continuous=True).get_result()
				text = [result['alternatives'][0]['transcript'].rstrip() + '.\n' for result in res['results']]
				text = [para[0].title() + para[1:] for para in text]
				transcript = ''.join(text)
				with open('output.txt', 'w') as out:
				    out.writelines(transcript)
				# print(transcript)

				
				print("rendering new page....")
				return render(request,'pdfreader/results.html',model_reader(transcript))

			else :
				return render(request,'pdfreader/404.html')


	form = CreateForm()
	print(" rendering same page...")
	return render(request,'pdfreader/search.html',{'form':form})
