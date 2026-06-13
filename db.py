import streamlit as st
from pymongo import MongoClient
import pandas as pd

@st.cache_resource
def get_client():
    return MongoClient(st.secrets["MONGO_URI"])

def get_db():
    return get_client()[st.secrets.get("MONGO_DB", "student_analytics")]

@st.cache_data(ttl=600)
def load_collection(name):
    db = get_db()
    docs = list(db[name].find({}, {"_id": 0}))
    return pd.DataFrame(docs)