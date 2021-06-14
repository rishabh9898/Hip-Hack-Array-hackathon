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


#Define paper data class somewhere


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


def add_items(request):
	if request.method =='POST':
		form = CreateForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			search = form.cleaned_data['search']

			form.save()
			print(search)

			# model = pickle.load(open('model_pickle','rb'))

			with open("D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\kungfu","rb") as f:
				model = pickle.load(f)

			df = pd.read_csv('D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\ccc-organizations-2011_1.csv')
			papers = df.Description.values
			corpus_embeddings = torch.load("D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\tensor.pt")
			search_papers(title=search,model= model,corpus_embeddings=corpus_embeddings,papers = papers,df = df)


	form = CreateForm()
	return render(request,'pdfreader/search.html',{'form':form})



charities = []

def search_papers(title,model,corpus_embeddings,papers,df):  #consider adding request parameter here
   #data_dict = {} # this is the means through which the data is sent to the result template html 
   query_embedding = model.encode('[CLS]'+title+'[SEP]', convert_to_tensor=True) # Converts to tensor
   search_hits = util.semantic_search(query_embedding, corpus_embeddings)
   search_hits = search_hits[0]
   count = 0

   for hit in search_hits:
	 #context_dict = {}
         related_paper = papers[hit['corpus_id']]
         count += 1
         print(str(count)+ ")" + " Description of charity : " +related_paper)
         print("similiarity score of " + str(format(search_hits[count-1]['score'],".2f")))
         subsetDataFrame = df[df['Description'] == related_paper]
         k=subsetDataFrame.values
         a_string = "Name of Organization"
         print("\033[1m" + a_string + "\033[0m")
         print(str(k[0][1]))
	 #context_dict['Description'] = related_paper
	 #context_dict['Similarity'] = str(format(search_hits[count-1]['score'],".2f"))
	 #context_dict['Organization'] = str(k[0][1])
	 #data_dict['Paper'+str(count)] = context_dict
   #data_dict['count'] = count
   #return render(request, 'pdfreader/results.html', data_dict) #path 'pdfreader/results.html' is not made yet, need to make the template to accept data

