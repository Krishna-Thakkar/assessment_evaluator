import requests
from langchain.prompts import PromptTemplate
import json
import os
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import ezodf
import warnings
warnings.filterwarnings("ignore")

load_dotenv(find_dotenv())

doc = ezodf.opendoc('/home/mind/projects/projects/assessment_evaluator/data.ods')

df_dict = {}
for sheet in doc.sheets:
    for i, col in enumerate(sheet.columns()):
        colname = col[0].display_form
        df_dict[colname] = []
        for j, row in enumerate(col):
            if j == 0:
                continue
            else:
                df_dict[colname].append(row.display_form)
df = pd.DataFrame(df_dict)

# question = "Explain the impact of climate change on ecosystems and biodiversity."

# student_answer = "Climate change has far-reaching effects on ecosystems and biodiversity. Rising temperatures, shifts in precipitation patterns, and extreme weather events can disrupt habitats, leading to the loss of species and alterations in ecosystem dynamics. Additionally, changes in temperature can affect the distribution and behavior of various organisms, influencing their interactions and overall biodiversity."

# actual_answer = "The consequences of climate change on ecosystems and biodiversity are extensive. Disruptions in habitats caused by increasing temperatures, changing precipitation patterns, and extreme weather events contribute to the decline of species and modifications in the functioning of ecosystems. Furthermore, shifts in temperature can influence the behavior and distribution of different organisms, impacting their interactions and the overall diversity of life."

# total_marks = 5

def get_score(question, student_answer, actual_answer, total_marks):

    prompt_template = PromptTemplate.from_template("""
    You are an assessment evaluator. Your task is to score a student's answer out of {total_marks} based on the question and the actual answer. 
    The question, student's answer and the actual answer will be provided to you.

    Question: {question}
    Student's answer: {student_answer}
    Actual answer: {actual_answer}       

    Provide the output in JSON format with 'score' as the key.  
    """)

    prompt_template = prompt_template.format(question=question, 
                                             student_answer=student_answer, 
                                             actual_answer=actual_answer, 
                                             total_marks=total_marks)
    
    new_data = {
    "prompt": str(prompt_template)
    }

    url_post = os.getenv('MODEL_URL')

    r = requests.post(url_post, json=new_data)

    return json.loads(r.content.decode())['score']

marks = list()

for i in df.index:
    marks.append(get_score(df['question'][i], df['student_answer'][i], df['actual_answer'][i], df['total_marks'][i]))

print('score list:', marks)
print('final score:', sum(marks))
print('total score:', pd.to_numeric(df['total_marks']).sum())