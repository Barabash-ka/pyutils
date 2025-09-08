import ollama
import pandas as pd
import matplotlib.pyplot as plt

# question
q = '''How can data science techniques improve predictive maintenance
of rotating equipment such as pumps and turbines?'''

# context
cntx = '''In engineering, particularly in industries such as manufacturing,
transportation, and energy, machinery and equipment are crucial assets.
These assets require regular maintenance to ensure optimal performance
and to prevent unexpected breakdowns, which can be costly and disruptive.
Traditional maintenance strategies often rely on scheduled maintenance
routines or responding to equipment failures as they occur. However,
with the advancement of data science techniques such as machine learning
and predictive analytics, engineers can now predict when a machine is
likely to fail or require maintenance. This approach, known as predictive
maintenance, uses historical data, sensor data, and algorithms to identify
patterns and predict potential issues before they happen. The implementation
of these data science techniques in engineering maintenance can lead to
more efficient use of resources, reduced downtime, and potentially
significant cost savings.'''

# models
models = ['phi','mistral','gemma'] #,'mixtral']

# store results
r = []
idx = []
# prompt without context
pmpt = f'Question: {q}'
for i,mx in enumerate(models):
    r.append(ollama.generate(model=mx, prompt=pmpt))
    idx.append(mx)
    print(f"Model: {idx[-1]}, Time: {r[-1]['total_duration']/1e9}s")

# prompt with context
pmpt = f'Context: {cntx} Question: {q}'
for i,mx in enumerate(models):
    r.append(ollama.generate(model=mx, prompt=pmpt))
    idx.append(mx+'+ctx')
    print(f"Model: {idx[-1]}, Time: {r[-1]['total_duration']/1e9}s")

# put results in DataFrame
rcols = ['total_duration','load_duration',
         'prompt_eval_count','eval_count',
         'prompt_eval_duration','eval_duration']
data = {}
for i,x in enumerate(rcols):
    if (i==2) or (i==3):
        data[x] = [ri[x] for ri in r]
    else:
        data[x] = [ri[x]/1e9 for ri in r]
data = pd.DataFrame(data, index=idx)
data['calc_duration'] = data['total_duration']-data['load_duration']
data['prompt_rate'] = data['prompt_eval_count']/data['prompt_eval_duration']
data['eval_rate'] = data['eval_count']/data['eval_duration']
print(data)

pcols = ['load_duration','prompt_rate','eval_rate']
axs = data[pcols].plot(figsize=(6,5),kind='bar',subplots=True)
ylb = ['Time (s)','Rate (tk/s)','Rate (tk/s)']
for i,ax in enumerate(axs):
    ax.set_title('')
    ax.set_ylabel(ylb[i])
plt.tight_layout(); plt.savefig('results.png',dpi=300); plt.show()
