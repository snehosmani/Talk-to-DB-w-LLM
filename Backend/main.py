import pyodbc
from fastapi import FastAPI
import shutil
import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as gemini_client
import json

load_dotenv()

# Access environment variables
GOOGLE_API_KEY= os.environ['GOOGLE_API_KEY']
gemini_client.configure(api_key=GOOGLE_API_KEY)

#set the model
model = gemini_client.GenerativeModel('gemini-pro')

#DB configs -- local server
def dBase_conn(query,count):
    #Connecting to DB
    DRIVER_NAME='SQL SERVER'
    SERVER_NAME='ppgang'
    DATABASE_NAME = 'players'
    count+=1

    connection_string =f"""
        DRIVER={{{DRIVER_NAME}}};
        SERVER={SERVER_NAME};
        DATABASE={DATABASE_NAME};
    """
    try:
        conn = pyodbc.connect(connection_string)
        # crsr = conn.cursor()
        # rows = crsr.execute(query).fetchall()
        sql_df = pd.read_sql_query(query, conn)
        sql_df = sql_df.to_json()
        return sql_df, True, count
            
    except Exception as e:
        return e,False,count



app = FastAPI()

@app.get("/",tags=['ROOT'])
async def root()->dict:
    return {"Test": "Genai"}


@app.get('/v1/answer')
def get_answer(query):
    Table_schema = f"""
TABLE AGENTS
AGENT_CODE: Unique identifier for each agent. This is a Primary key
AGENT_NAME: The agent's full name.
WORKING_AREA: City or region where the agent operates.
COMMISSION: Percentage earned by the agent on sales.
PHONE_NO: Agent's contact phone number.
COUNTRY: Agent's country of residence.

TABLE CUSTOMER
CUST_CODE: Unique identifier for each customer. This is a primary key
CUST_NAME: Customer's full name.
CUST_CITY: City where the customer is located.
WORKING_AREA: Region or area the customer operates within.
CUST_COUNTRY: Customer's country.
GRADE: Customer's rating or ranking.
OPENING_AMT: Initial account balance.
RECEIVE_AMT: Total amount received from the customer.
PAYMENT_AMT: Total amount paid by the customer.
OUTSTANDING_AMT: Remaining balance due from the customer.
PHONE_NO: Customer's contact phone number.
AGENT_CODE: Code of the agent assigned to the customer. This is a foreign key, to be used when connecting to Table AGENTS.


TABLE ORDERS
ORD_NUM: Unique order number. This is a primary key
ORD_AMOUNT: Total value of the order.
ADVANCE_AMOUNT: Down payment or deposit on the order.
ORD_DATE: Date the order was placed.
CUST_CODE: Customer code associated with the order. This is a foreign key, to be used when connecting to Table CUSTOMER.
AGENT_CODE: Agent code associated with the order. This is a foreign key, to be used when connecting to Table AGENTS.
ORD_DESCRIPTION: Brief description of the order contents.
"""
    
    Sql_query='Select * from Agents;'
    graph_type='Line'
    column_name_x='AGENT_CODE'
    column_name_y='ORD_AMOUNT'
    dbnm='players'
    #QUERY='How much amount did each agent receive? Display with Agent name'
    QUERY=query

    Gemini_query=f'''
You are a highly skilled Data Analyst and you master writing complex SQL queries and creating compelling graphs. Given a database name, the table schema and a question, 
you will 1) Accurately give a SQL query ending with semi colon. Note : You will just give an executable query without any additonal text or explanation. And if you are using aggregation function like count,Avg,max then DO NOT forget to give an alias column name.
2) Using the columns from the output of SQL query generated, you will have to give parameters to generate a graph. i.e., x-axis, y-axis and the type of graph (as in bar, pie, line etc)

For example:
Database name : {dbnm}
Table schemas : {Table_schema}
My Question : What is the commission set for all the agents?

Your Answer:
{{"Query" : "Select AGENT_NAME,COMMISSION from AGENTS;",
"X-Axis" : "AGENT_NAME",
"Y-Axis" :"COMMISSION",
"Graph" : "Bar"}}

Here's my question : {QUERY}

Your answer?

NOTE: Answer truthfully as shown in the example do NOT include any additional text in the response.
'''
    
    response = model.generate_content(Gemini_query)
    res = json.loads(response.text)

    count=0
    query_result,flag,count=dBase_conn(res['Query'],count)

    while count<3 and not flag:
        
        Recall_gem=f''' The SQL Query {res['Query']} that you provided for {QUERY} errored out with this message {query_result}.
            Answer correctly for the question : {QUERY}, If you don't know the answer, then respond with "None".
            Note : Please DO NOT provide any text explanation        
    '''
        Recall_gem+=Gemini_query

        response=model.generate_content(Recall_gem)
        res = json.loads(response.text)
        print(res['Query'])
        print('executing')
        query_result,flag,count=dBase_conn(res['Query'],count)
        print(query_result)
        print('Done')

    print(query_result)
    print(res)

    if flag == False:
        status=f'Due to {query_result}, the execution failed'
        return {'result':None,'gem_response':res,'message':status}
    else:
        status='Excecution Completed'
        return {'result':query_result,'gem_response':res,'message':status}
        #ret_que = query_result.to_dict('records')





    


 