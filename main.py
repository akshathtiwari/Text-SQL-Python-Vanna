import streamlit as st
import sqlite3
import os
import qdrant_client
import pandas as pd
from qdrant_client import QdrantClient
import sqlalchemy
from google.cloud.sql.connector import Connector
from vertexai.language_models import TextGenerationModel
from vertexai import init as vertexai_init
from vanna.qdrant import Qdrant_VectorStore
from vanna.base import VannaBase  # Adjust this import according to your project structure

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Set environment variables for Qdrant and Google Cloud
QDRANT_HOST = os.getenv('QDRANT_HOST')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
INSTANCE_CONNECTION_NAME = os.getenv('INSTANCE_CONNECTION_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
GCP_LOCATION = os.getenv('GCP_LOCATION')
GCP_MODEL_NAME = os.getenv('GCP_MODEL_NAME')
GCP_TUNED_MODEL_ID = os.getenv('GCP_TUNED_MODEL_ID')

# Initialize the Google Cloud SQL connector
connector = Connector()

def getconn():
    """
    Function to return the database connection object using Google Cloud SQL connector.

    Returns:
        sqlalchemy.engine.base.Connection: Database connection object.
    """
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn

# Create connection pool with 'creator' argument to our connection object function
pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

class ChatBison(VannaBase):
    """
    Class to interact with the Google Vertex AI for text generation.

    Attributes:
        project (str): Google Cloud project ID.
        location (str): Google Cloud location.
        model_name (str): Name of the model.
        tuned_model_id (str): ID of the tuned model.
        model (TextGenerationModel): Text generation model instance.
        parameters (dict): Parameters for text generation.
    """
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
        """
        Create a system message dictionary.

        Args:
            message (str): The system message content.

        Returns:
            dict: The system message dictionary.
        """
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> dict:
        """
        Create a user message dictionary.

        Args:
            message (str): The user message content.

        Returns:
            dict: The user message dictionary.
        """
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> dict:
        """
        Create an assistant message dictionary.

        Args:
            message (str): The assistant message content.

        Returns:
            dict: The assistant message dictionary.
        """
        return {"role": "assistant", "content": message}

    def submit_prompt(self, prompt, **kwargs) -> str:
        """
        Submit a prompt to the text generation model and get the response.

        Args:
            prompt (str): The prompt to be submitted.

        Returns:
            str: The generated response text.
        """
        if not prompt.strip():  # Check if prompt is empty or contains only whitespace
            return "Please provide a valid prompt."
        
        response = self.model.predict(prompt, **self.parameters)
        return response.text

class MyVanna(Qdrant_VectorStore, ChatBison):
    """
    Class that integrates Qdrant vector store with the ChatBison model.
    """
    def __init__(self, config=None):
        Qdrant_VectorStore.__init__(self, config=config)
        ChatBison.__init__(self, config=config)

@st.cache_resource(ttl=3600)
def setup_vanna():
    """
    Setup the Vanna instance by initializing Qdrant and ChatBison.

    Returns:
        MyVanna: An instance of MyVanna class.
    """
    client = qdrant_client.QdrantClient(
        QDRANT_HOST,
        api_key=QDRANT_API_KEY
    )

    config = {
        "project": GCP_PROJECT_ID,
        "location": GCP_LOCATION,
        "model_name": GCP_MODEL_NAME,
        "tuned_model_id": GCP_TUNED_MODEL_ID
    }

    vn = MyVanna(config={'client': client, **config})
    
    conn_details = {
        'host': 'localhost',
        'port': 5432,
        'user': DB_USER,
        'password': DB_PASS,
        'database': DB_NAME
    }
    
    def run_sql(sql: str) -> pd.DataFrame:
        """
        Run the provided SQL query and return the result as a DataFrame.

        Args:
            sql (str): The SQL query to be executed.

        Returns:
            pd.DataFrame: The result of the SQL query as a DataFrame.
        """
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
    """
    Generate sample questions using the Vanna instance.

    Returns:
        list: A list of generated sample questions.
    """
    vn = setup_vanna()
    return vn.generate_questions()

@st.cache_data(show_spinner="Generating SQL query ...")
def generate_sql_cached(question: str):
    """
    Generate SQL query based on the provided question.

    Args:
        question (str): The user's question.

    Returns:
        str: The generated SQL query.
    """
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="Checking for valid SQL ...")
def is_sql_valid_cached(sql: str):
    """
    Check if the provided SQL query is valid.

    Args:
        sql (str): The SQL query to be checked.

    Returns:
        bool: True if the SQL query is valid, False otherwise.
    """
    vn = setup_vanna()
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str):
    """
    Run the provided SQL query and return the result.

    Args:
        sql (str): The SQL query to be executed.

    Returns:
        pd.DataFrame: The result of the SQL query as a DataFrame.
    """
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Checking if we should generate a chart ...")
def should_generate_chart_cached(question, sql, df):
    """
    Determine if a chart should be generated based on the question, SQL, and DataFrame.

    Args:
        question (str): The user's question.
        sql (str): The generated SQL query.
        df (pd.DataFrame): The result of the SQL query.

    Returns:
        bool: True if a chart should be generated, False otherwise.
    """
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Generating Plotly code ...")
def generate_plotly_code_cached(question, sql, df):
    """
    Generate Plotly code based on the question, SQL, and DataFrame.

    Args:
        question (str): The user's question.
        sql (str): The generated SQL query.
        df (pd.DataFrame): The result of the SQL query.

    Returns:
        str: The generated Plotly code.
    """
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code

@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df):
    """
    Generate a Plotly figure based on the Plotly code and DataFrame.

    Args:
        code (str): The generated Plotly code.
        df (pd.DataFrame): The result of the SQL query.

    Returns:
        plotly.graph_objs._figure.Figure: The generated Plotly figure.
    """
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)

@st.cache_data(show_spinner="Generating followup questions ...")
def generate_followup_cached(question, sql, df):
    """
    Generate follow-up questions based on the question, SQL, and DataFrame.

    Args:
        question (str): The user's question.
        sql (str): The generated SQL query.
        df (pd.DataFrame): The result of the SQL query.

    Returns:
        list: A list of generated follow-up questions.
    """
    vn = setup_vanna()
    return vn.generate_followup_questions(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="Generating summary ...")
def generate_summary_cached(question, df):
    """
    Generate a summary based on the question and DataFrame.

    Args:
        question (str): The user's question.
        df (pd.DataFrame): The result of the SQL query.

    Returns:
        str: The generated summary.
    """
    vn = setup_vanna()
    return vn.generate_summary(question=question, df=df)
