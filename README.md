# Text-SQL Assistant
# README

## Overview
This project is a demonstration of integrating Google Vertex AI, Qdrant, and Google Cloud SQL with a Streamlit interface. It involves setting up a LLM for text generation and running SQL queries on a database to generate insights and visualizations.

## Requirements
- Python 3.7 or above
- Streamlit
- Qdrant
- Google Cloud SQL
- Vertex AI
- PostgreSQL
- Environment variables setup

## Setup

### Step 1: Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables
Create a `.env` file in the root directory of your project and add the following environment variables:

```plaintext
QDRANT_HOST=your_qdrant_host
QDRANT_API_KEY=your_qdrant_api_key
INSTANCE_CONNECTION_NAME=your_instance_connection_name
DB_USER=your_database_user
DB_PASS=your_database_password
DB_NAME=your_database_name
GCP_PROJECT_ID=your_google_cloud_project_id
GCP_LOCATION=your_google_cloud_location
GCP_MODEL_NAME=your_google_cloud_model_name
GCP_TUNED_MODEL_ID=your_google_cloud_tuned_model_id
```

### Step 4: Set Up Google Cloud Credentials
Ensure you have the Google Cloud credentials JSON file and set the environment variable to its path:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

### Step 5: Running the Application
Run the Streamlit application:

```bash
streamlit run main.py
```

To run the fine-tuned tests, use:

```bash
python test_fine_tuned.py
```

## Files and Structure

### main.py
This file sets up the Streamlit application, integrates with Google Vertex AI for text generation, and interacts with Google Cloud SQL to fetch data and generate visualizations.

#### Key Functions:
- `setup_vanna()`: Initializes the Vanna instance with Qdrant and Vertex AI.
- `generate_questions_cached()`: Generates sample questions using the Vanna instance.
- `generate_sql_cached(question)`: Generates SQL queries based on user questions.
- `is_sql_valid_cached(sql)`: Checks the validity of the SQL query.
- `run_sql_cached(sql)`: Runs the provided SQL query and returns the result.
- `should_generate_chart_cached(question, sql, df)`: Determines if a chart should be generated.
- `generate_plotly_code_cached(question, sql, df)`: Generates Plotly code for visualization.
- `generate_plot_cached(code, df)`: Generates a Plotly figure based on the code.
- `generate_followup_cached(question, sql, df)`: Generates follow-up questions.
- `generate_summary_cached(question, df)`: Generates a summary of the data.

### test_fine_tuned.py
This file contains tests for the fine-tuned model integration, focusing on ensuring that the integration with Qdrant and Vertex AI works as expected.

#### Key Classes and Functions:
- `ChatBison(config)`: Initializes the ChatBison model with Vertex AI.
- `MyVanna(config)`: Integrates Qdrant vector store with the ChatBison model.
- `setup_vanna()`: Initializes the Vanna instance with necessary configurations.
- `generate_questions_cached()`: Generates sample questions using the Vanna instance.
- `generate_sql_cached(question)`: Generates SQL queries based on user questions.
- `is_sql_valid_cached(sql)`: Checks the validity of the SQL query.
- `run_sql_cached(sql)`: Runs the provided SQL query and returns the result.
- `should_generate_chart_cached(question, sql, df)`: Determines if a chart should be generated.
- `generate_plotly_code_cached(question, sql, df)`: Generates Plotly code for visualization.
- `generate_plot_cached(code, df)`: Generates a Plotly figure based on the code.
- `generate_followup_cached(question, sql, df)`: Generates follow-up questions.
- `generate_summary_cached(question, df)`: Generates a summary of the data.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
Please read [CONTRIBUTING](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## Acknowledgments
- Streamlit
- Google Cloud
- Qdrant

## Contact
For any questions or issues, please contact the project maintainer.

---

This README provides a structured overview of the project, setup instructions, file descriptions, and key functionalities, making it easier for other developers to understand and use the code.
