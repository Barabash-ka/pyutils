import ollama
ollama.list()
prompt1 = 'What is the capital of France?'
response = ollama.chat(model='mistral', messages=[
            {'role': 'user','content': prompt1,},])
r1 = response['message']['content']
print(r1)

prompt2 = 'and of Germany?'
response = ollama.chat(model='mistral', messages=[
            {'role': 'user','content': prompt1,},
            {'role': 'assistant','content': r1,},            
            {'role': 'user','content': prompt2,},])
r2 = response['message']['content']
print(r2)
