import ollama
prompt = 'How can LLMs improve automation?'
stream = ollama.chat(model='mistral',
          messages=[{'role': 'user', 'content': prompt}],
          stream=True,)
for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)
