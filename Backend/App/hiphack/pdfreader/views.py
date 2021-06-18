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


#Define paper data class somewhere
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


def index(request):
	return render(request,'pdfreader/landing.html')

charities = []

def search_papers(title,model,corpus_embeddings,papers):
  query_embedding = model.encode(title+'[SEP]', convert_to_tensor=True)

  data_dict = {}

  count = 0

  search_hits = util.semantic_search(query_embedding, corpus_embeddings)
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
  	x = Paper_Data(related_paper['abstract'],str(format(search_hits[count-1]['score'],".2f")),related_paper['title'],related_paper['url']+".pdf",str(count))
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

def add_items(request):
	if request.method =='POST':
		form = CreateForm(request.POST, request.FILES)
		if form.is_valid():
			f1 = request.FILES['file1']
			pdf = PyPDF2.PdfFileReader(f1)
			num_pages= pdf.getNumPages()
			text=''
			for i in range(num_pages):
				page=pdf.getPage(i)
				text=text+page.extractText()
			text = preprocess(text)
			print(text)

			# name = form.cleaned_data['name']
			search = form.cleaned_data['search']

			form.save()
			print(search)

			# model = pickle.load(open('model_pickle','rb'))

			with open("pdfreader/paper_model","rb") as f:
				model = pickle.load(f)

			with open("D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\bert_summary_model","rb") as fi:
				model_1= pickle.load(fi)

			bert_summary = ''.join(model_1(text, min_length=60))

			print(bert_summary)

			# df = pd.read_csv('D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\')
			dataset_file = 'emnlp2016-2018.json'

			if not os.path.exists(dataset_file):
				util.http_get("https://sbert.net/datasets/emnlp2016-2018.json", dataset_file)
			with open(dataset_file) as fIn:
				papers = json.load(fIn)

			title = bert_summary

			corpus_embeddings = torch.load("D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\tensor_research_papers.pt")
			context = search_papers(title=title,model= model,corpus_embeddings=corpus_embeddings,papers = papers)
			print("rendering new page....")
			return render(request,'pdfreader/results.html',context)


		# form = CreateForm(request.POST)
		

	form = CreateForm()
	print(" rendering same page...")
	return render(request,'pdfreader/search.html',{'form':form})





