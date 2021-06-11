import pandas as pd

import json
import os
from sentence_transformers import SentenceTransformer, util


df = pd.read_csv('D:\\GITHUB\\rishabh9898\\hackathon-HipHack\\Backend\\App\\hiphack\\pdfreader\\ccc-organizations-2011_1.csv')

model = SentenceTransformer('allenai-specter')
papers = df.Description.values

paper_texts = [paper for paper in papers]

#Compute embeddings for all descriptions
corpus_embeddings = model.encode(paper_texts, convert_to_tensor=True)

import pickle
with open('kungfu','wb') as f:
  pickle.dump(model,f)
