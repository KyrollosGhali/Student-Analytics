import streamlit as st
from pymongo import MongoClient
import pandas as pd

@st.cache_resource
def get_client():
    uri = st.secrets["MONGO_URI"]

    client = MongoClient(
        uri,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=15000
    )

    return client
def get_db():
    return get_client()[st.secrets.get("MONGO_DB", "student_analytics")]

@st.cache_data(ttl=600)
def load_collection(name):
    db = get_db()
    docs = list(db[name].find({}, {"_id": 0}))
    return pd.DataFrame(docs)

def get_db():
    return get_client()[st.secrets.get("MONGO_DB", "student_analytics")]

@st.cache_data(ttl=600)
def load_collection(name):
    db = get_db()
    docs = list(db[name].find({}, {"_id": 0}))
    return pd.DataFrame(docs)
