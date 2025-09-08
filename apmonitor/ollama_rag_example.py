import ollama
import pandas as pd
import chromadb

# Loading and preparing the ChromaDB with data
def setup_chromadb():
    try:
        qa = pd.read_json('mydb.jsonl',lines=True)
    except:
        # file not found, create file
        fid = open('mydb.jsonl','w')
        fid.write('''{"question":"What are the three disciplines of a triathlon?","answer":"The three disciplines of a triathlon are swimming, cycling, and running."}
{"question":"What is the standard distance for an Olympic triathlon?","answer":"An Olympic triathlon consists of a 1.5 km swim, a 40 km bike ride, and a 10 km run."}
{"question":"How do transition areas work in a triathlon?","answer":"Transition areas are used to switch between disciplines. The first transition (T1) is from swimming to cycling, and the second transition (T2) is from cycling to running."}
{"question":"What is an Ironman Triathlon?","answer":"An Ironman Triathlon is a long-distance triathlon race consisting of a 3.86 km swim, 180.25 km bike ride, and a marathon 42.20 km run."}
{"question":"Can relay teams participate in triathlons?","answer":"Yes, relay teams can participate in triathlons, with each team member completing one segment of the race."}
{"question":"What is the purpose of a wetsuit in triathlon swimming?","answer":"A wetsuit provides buoyancy, warmth, and speed enhancement during the swimming portion of a triathlon."}
{"question":"How do triathletes train for a triathlon?","answer":"Triathletes train by developing endurance, strength, and technique in swimming, cycling, and running, often with a balanced training schedule."}
{"question":"What are drafting rules in triathlon cycling?","answer":"Drafting rules in triathlon cycling vary by race. Some races allow drafting, while others, like Ironman races, prohibit it to ensure fairness and safety."}
{"question":"What nutrition is recommended for triathletes during a race?","answer":"Triathletes are recommended to have a balance of carbohydrates, electrolytes, and fluids during the race to maintain energy and hydration levels."}
{"question":"Are there age-group categories in triathlons?","answer":"Yes, most triathlons have age-group categories, allowing athletes of similar ages to compete against each other."}''')
        fid.close()
        qa = pd.read_json('mydb.jsonl',lines=True)
    documents = []
    metadatas = []
    ids = []

    for i in range(len(qa)):
        s = f"### Question: {qa['question'].iloc[i]} ### Answer: {qa['answer'].iloc[i]}"
        documents.append(s)
        metadatas.append({'qid': f'qid_{i}'})
        ids.append(str(i))

    cc = chromadb.Client()
    cdb = cc.create_collection(name='triathlon')
    cdb.add(documents=documents, metadatas=metadatas, ids=ids)
    return cdb

# Ollama LLM function
def ollama_llm(question, context):
    formatted_prompt = f"Question: {question}\n\nContext: {context}"
    response = ollama.chat(model='mixtral', messages=[{'role': 'user', 'content': formatted_prompt}])
    return response['message']['content']

# Define the RAG chain
def rag_chain(question, cdb):
    context = cdb.query(query_texts=[question],
                        n_results=5, include=['documents'])
    formatted_context = "\n\n".join(x for x in context['documents'][0])
    formatted_context += "\n\nI am an AI Triathlon assistant with detailed knowledge about the three disciplines involved in a triathlon (swimming, cycling, and running), the standard distances for different types of triathlon races such as the Olympic triathlon and Ironman Triathlon, and specifics about the transitions between each segment of the race. I am well-versed in the rules and strategies that pertain to each aspect of a triathlon. This includes understanding the significance of equipment such as wetsuits in the swimming segment, the rules around drafting in the cycling portion, and the specific nutritional requirements for triathletes during a race. Additionally, I have information regarding the training methods and schedules used by triathletes to prepare for races, the role of relay teams in triathlons, and the categorization of competitors in different age groups. This information allows me to answer questions related to triathlon races, training, rules, equipment, and strategies effectively and accurately. My responses are informed by a comprehensive set of data and details about triathlons, making me a valuable resource for anyone seeking knowledge in this area."
    result = ollama_llm(question, formatted_context)
    return result

# Setup ChromaDB
cdb = setup_chromadb()

# Create prompt for Local RAG LLM
question = 'What is the total distance of an Ironman?'
out = rag_chain(question, cdb)
print(out)
