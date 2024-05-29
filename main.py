import streamlit as st
import sqlite3
import os
import qdrant_client
import pandas as pd
from qdrant_client import QdrantClient
import subprocess
import sys
from google.cloud.sql.connector import Connector
import sqlalchemy
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from vertexai.language_models import TextGenerationModel
from vertexai import init as vertexai_init
from vanna.qdrant import Qdrant_VectorStore
from vanna.base import VannaBase  # Adjust this import according to your project structure

CLIENT_FILE = 'client_file.json'

# Set environment variables for Qdrant
os.environ['QDRANT_HOST'] = 'https://6db829ba-d1fc-4463-a9c0-b669c5f623de.us-east4-0.gcp.cloud.qdrant.io:6333'
os.environ['QDRANT_API_KEY'] = 'zdn_wyGDpxD4tc1wCLzAobp4n_eiPRM_F1R-B4g8O-IlYq-hPHqI5w'

project_id = "refined-vector-140309"
INSTANCE_CONNECTION_NAME = f"refined-vector-140309:us-central1:demo-deloitte-vanna"
print(f"Your instance connection name is: {INSTANCE_CONNECTION_NAME}")
DB_USER = "postgres"
DB_PASS = "akshi@09"
DB_NAME = "finance_data"

connector = Connector()

# Function to return the database connection object
def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user="postgres",
        password="akshi@09",
        db="finance_data"
    )
    return conn

# Create connection pool with 'creator' argument to our connection object function
pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

class ChatBison(VannaBase):
    def __init__(self, config=None):
        if config is None:
            raise ValueError("For ChatBison, config must be provided with project, location, and model details.")
        
        self.project = config.get("project")
        self.location = config.get("location")
        self.model_name = config.get("model_name")
        self.tuned_model_id = config.get("tuned_model_id")
        
        if not self.project or not self.location or not self.model_name or not self.tuned_model_id:
            raise ValueError("Missing necessary configuration for ChatBison.")
        
        vertexai_init(project=self.project, location=self.location)
        self.model = TextGenerationModel.from_pretrained(self.model_name).get_tuned_model(self.tuned_model_id)

        self.parameters = {
            "candidate_count": 1,
            "max_output_tokens": 1024,
            "temperature": 0.9,
            "top_p": 1
        }
    
    def system_message(self, message: str) -> dict:
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> dict:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> dict:
        return {"role": "assistant", "content": message}

    def submit_prompt(self, prompt, **kwargs) -> str:
        if not prompt.strip():  # Check if prompt is empty or contains only whitespace
            return "Please provide a valid prompt."
        
        response = self.model.predict(prompt, **self.parameters)
        return response.text

class MyVanna(Qdrant_VectorStore, ChatBison):
    def __init__(self, config=None):
        Qdrant_VectorStore.__init__(self, config=config)
        ChatBison.__init__(self, config=config)

@st.cache_resource(ttl=3600)
def setup_vanna():
    client = qdrant_client.QdrantClient(
        os.getenv('QDRANT_HOST'),
        api_key=os.getenv('QDRANT_API_KEY')
    )

    config = {
        "project": "151174631973",
        "location": "us-central1",
        "model_name": "text-bison@002",
        "tuned_model_id": "projects/151174631973/locations/us-central1/models/2122797412933173248"
    }

    vn = MyVanna(config={'client': client, **config})
    
    conn_details = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'akshi@09',
        'database': 'finance_data'
    }
    
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user="postgres",
        password="akshi@09",
        db="finance_data"
    )
    cursor = conn.cursor()

    def run_sql(sql: str) -> pd.DataFrame:
        with pool.connect() as conn:
            df = pd.read_sql_query(sql, conn)
        return df

    vn.run_sql = run_sql
    vn.run_sql_is_set = True

    df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
    plan = vn.get_training_plan_generic(df_information_schema)
    training_data = vn.get_training_data()
    # vn.train(plan=plan)

    return vn

@st.cache_data(show_spinner="Generating sample questions ...")
def generate_questions_cached():
    vn = setup_vanna()
    return vn.generate_questions()

@st.cache_data(show_spinner="Generating SQL query ...")
def generate_sql_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="Checking for valid SQL ...")
def is_sql_valid_cached(sql: str):
    vn = setup_vanna()
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Checking if we should generate a chart ...")
def should_generate_chart_cached(question, sql, df):
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Generating Plotly code ...")
def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code

@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)

@st.cache_data(show_spinner="Generating followup questions ...")
def generate_followup_cached(question, sql, df):
    vn = setup_vanna()
    return vn.generate_followup_questions(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="Generating summary ...")
def generate_summary_cached(question, df):
    vn = setup_vanna()
    return vn.generate_summary(question=question, df=df)
