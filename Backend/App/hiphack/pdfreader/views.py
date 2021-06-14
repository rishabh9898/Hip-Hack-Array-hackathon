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
import json


#Define paper data class somewhere
class Paper_Data:
	description = ""
	similarity = ""
	organization = ""
	def __init__(self, description, similarity, organization):
		self.description = description
		self.similarity = similarity
		self.organization = organization


def index(request):
	return render(request,'pdfreader/landing.html')

# def get_name(request):
#     # if this is a POST request we need to process the form data
#     if request.method == 'POST':
#         # create a form instance and populate it with data from the request:
#         form = NameForm(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             # process the data in form.cleaned_data as required
#             # ...
#             # redirect to a new URL:
#             return HttpResponseRedirect('/thanks/')

#     # if a GET (or any other method) we'll create a blank form
#     else:
#         form = NameForm()

#     return render(request, 'landing.html', {'form': form})
charities = []

def search_papers(title,model,corpus_embeddings,papers):
  query_embedding = model.encode(title+'[SEP]', convert_to_tensor=True)
  data_dict = {}

  count = 0

  search_hits = util.semantic_search(query_embedding, corpus_embeddings)
  search_hits = search_hits[0]  #Get the hits for the first query
  paper_list = []

  print("Query:", title)
  print("\nMost similar papers:")
  for hit in search_hits:
  	count+=1
  	related_paper = papers[hit['corpus_id']]
  	print(str(count)+". "+related_paper['title'])
  	print(related_paper['abstract'])
  	print(related_paper['url'])
  	x = Paper_Data(related_paper['abstract'],str(format(search_hits[count-1]['score'],".2f")),related_paper['title'])
  	paper_list.append(x)
  	data_dict['paper_list'] = paper_list
  return data_dict



# def search_papers(title,model,corpus_embeddings,papers,df):  #consider adding request parameter here
#    data_dict = {} # this is the means through which the data is sent to the result template html #definitely need to convert this into a classs
#    query_embedding = model.encode('[CLS]'+title+'[SEP]', convert_to_tensor=True) # Converts to tensor
#    search_hits = util.semantic_search(query_embedding, corpus_embeddings)
#    search_hits = search_hits[0]
#    count = 0
#    paper_list = []

#    for hit in search_hits:
#          related_paper = papers[hit['corpus_id']]
#          count += 1
#          print(str(count)+ ")" + " Description of charity : " +related_paper)
#          print("similiarity score of " + str(format(search_hits[count-1]['score'],".2f")))
#          subsetDataFrame = df[df['Description'] == related_paper]
#          k=subsetDataFrame.values
#          a_string = "Name of Organization"
#          print("\033[1m" + a_string + "\033[0m")
#          print(str(k[0][1]))
#          x = Paper_Data(related_paper, str(format(search_hits[count-1]['score'],".2f")),str(k[0][1]))
#          paper_list.append(x)
#          # data_dict['Paper'+str(count)] = x
#     # data_dict['count'] = count
#    data_dict['paper_list'] = paper_list
#    return data_dict #path 'pdfreader/results.html' is not made yet, need to make the template to accept data


def add_items(request):
	if request.method =='POST':
		form = CreateForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			search = form.cleaned_data['search']

			form.save()
			print(search)

			# model = pickle.load(open('model_pickle','rb'))

			with open("D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\paper_model","rb") as f:
				model = pickle.load(f)

			# df = pd.read_csv('D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\')
			dataset_file = 'emnlp2016-2018.json'

			if not os.path.exists(dataset_file):
				util.http_get("https://sbert.net/datasets/emnlp2016-2018.json", dataset_file)
			with open(dataset_file) as fIn:
				papers = json.load(fIn)

			# papers = df.Description.values
			corpus_embeddings = torch.load("D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\tensor_research_papers.pt")
			context = search_papers(title=search,model= model,corpus_embeddings=corpus_embeddings,papers = papers)
			print("rendering new page....")
			return render(request,'pdfreader/results.html',context)




	form = CreateForm()
	print(" rendering same page...")
	return render(request,'pdfreader/search.html',{'form':form})





