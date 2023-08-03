from fastapi import FastAPI, Request
from langchain import OpenAI, SQLDatabase , SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import openai
import json
import os
import re
import ast

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model_name='gpt-3.5-turbo', openai_api_key=openai_key, temperature=0.3)
current_path = os.path.dirname(__file__)
dburi = os.path.join('sqlite:///' + current_path,
                     "db", "product.db")
db = SQLDatabase.from_uri(dburi)
 
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True,return_intermediate_steps=True)

from langchain.chains import SQLDatabaseSequentialChain
db_chain_multi = SQLDatabaseSequentialChain.from_llm(llm, db, verbose=True,return_intermediate_steps=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

message = []


@app.post("/chat/")
async def chat(reqeust: Request):
    body = await reqeust.json()
    # additional_query = """"""
    # query = body['query']
    # if query == "clamping heads":
    #     return {"message": "sfdsfsfds"}
    query = body['query']
    additional_query = """ Select top 20. Output only SQLQuery and SQLResult not Answer.
"""


    additional_query2 = """
    """
    # query = query + additional_query
    # if (query == "I am looking for clamping heads") or (query == "what tools do you have"):                                                                                                                                                                                                                                                                                                      
    #     return {"message": "What type of clamping heads are you looking for? Or for what type of machine? Tell me more so I can help you find the correct product!"}
        
    # else:
    query += additional_query
    # print(query)
    res = db_chain(query)
    steps = res['intermediate_steps']
    text = steps[0]['input']

    summary = res['result']
    ########### Get Headers ###################
    split_text = text.split("SELECT")[1].split("FROM")[0].strip()
    keylist = list(split_text.split(","))
    # Split the header names based on commas and remove any surrounding quotes or spaces
    header_names = [name.strip('\"') for name in split_text.split(",")]
    ########### Get Values #####################
    result_match = re.search(r'SQLResult: (.+)', text)
    if result_match:
        sql_result = result_match.group(1)
    array_sql_result = ast.literal_eval(sql_result)
    print("----------------")
    print(array_sql_result)
    print("----------------")


#     json_data = json.loads(res["result"])

#     # print(json_data)

# # Get the keys as an array
#     key_array = list(json_data[0].keys())
    # print("----------------")
    # print(key_array)
    return {"message": "success", "row": array_sql_result, "column": keylist}

    
    # if res['result'] == "Ooops":
    #     print("------")
    #     messages = [ {"role": "system", "content": 
    #                 "You are a intelligent assistant."} ]
    #     while True:
    #         message = body['query'] + additional_query2
    #         if message:
    #             messages.append(
    #                 {"role": "user", "content": message},
    #             )
    #             chat = openai.ChatCompletion.create(
    #                 model="gpt-3.5-turbo", messages=messages
    #             )
    #         reply = chat.choices[0].message.content
    #         return {"message": reply}
    # else:
    #     return {"message": res['result']}