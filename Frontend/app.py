import streamlit as st
import requests
import json
import pandas as pd

URL = "http://127.0.0.1:8000/v1/answer/?query="

st.title("Talk to Database!!!")

prompt = st.chat_input("Ask Anything!!!")
if prompt:
    URL+=prompt
    ini_resp = requests.get(url = URL)
    ini_json = json.loads(ini_resp.text)
    if "completed" in ini_json['message'].lower():
        data=ini_json['result']
        data=json.loads(data)
        df = pd.DataFrame.from_dict(data)
        st.header(prompt)
        st.subheader('Table')
        st.dataframe(df)
        st.divider()
        st.subheader('Gemini response: ')
        st.write(f'Query Executed : {ini_json['gem_response']['Query']}')
        st.write(f' Graph Details :')
        st.write(f'X-axis : {ini_json['gem_response']['X-Axis']}')
        st.write(f'Y-axis : {ini_json['gem_response']['Y-Axis']}')
        st.write(f'Type of Graph : {ini_json['gem_response']['Graph']}')
        
        #chart
        if (ini_json['gem_response']['Graph']).lower() == 'bar':
            st.bar_chart(df,x=ini_json['gem_response']['X-Axis'],y=ini_json['gem_response']['Y-Axis'])
        elif (ini_json['gem_response']['Graph']).lower() == 'line':
            st.line_chart(df,x=ini_json['gem_response']['X-Axis'],y=ini_json['gem_response']['Y-Axis'])
        elif (ini_json['gem_response']['Graph']).lower() == 'scatter':
            st.scatter_chart(df,x=ini_json['gem_response']['X-Axis'],y=ini_json['gem_response']['Y-Axis'])
        else:
            st.write('Chart type not in the description')






    else:
        st.write("OOPS!!! Something went wrong!!")
        st.write(f'Possible err : {ini_json['message']}')



    


