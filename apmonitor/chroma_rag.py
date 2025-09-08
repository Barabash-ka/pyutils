import pandas as pd
import chromadb

# read Gekko LLM training data
url='https://raw.githubusercontent.com'
path='/BYU-PRISM/GEKKO/master/docs/llm/train.jsonl'
qa = pd.read_json(url+path,lines=True)

# # read training data
path='mydb.jsonl'
qa = pd.read_json(path,lines=True)

documents = []
metadatas = []
ids = []
for i in range(len(qa)):
    s = f"### Question: {qa['question'].iloc[i]} ### Answer: {qa['answer'].iloc[i]}"
    documents.append(s)
    metadatas.append({'qid':f'qid_{i}'})
    ids.append(str(i))

# in memory
cc = chromadb.Client()
collection = cc.create_collection(name='mydb')
# on local drive
#from chromadb.config import Settings
#st = Settings(anonymized_telemetry=False)
#cc = chromadb.PersistentClient(path='chroma',settings=st)
#try:
#    cc.delete_collection('mydb')
#except:
#    pass
#collection = cc.create_collection(name='mydb')

collection.add(
   documents=documents,
   metadatas=metadatas,
   ids=ids
)

results = collection.query(
   query_texts=['What are you trained to do?'],
   n_results=5,
   include=['distances','documents'])
print(results)
