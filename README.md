# Text-SQL Assistant

This repository contains a Streamlit application that allows users to interact with their databases using natural language questions. The app converts these questions into SQL queries, executes them, and returns the results in various forms such as tables, charts, and summaries.

## Prerequisites

Make sure you have the following installed on your machine:
- Python 3.7 or higher
- `pip` (Python package installer)

## Setup Instructions

Follow these steps to set up and run the application:

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/text-sql-assistant.git
cd text-sql-assistant
```

### 2. Create a Virtual Environment and Install Dependencies

Create a virtual environment to manage dependencies and activate it:

```sh
python -m venv venv
source venv/bin/activate    # On Windows, use `venv\Scripts\activate`
```

Install the required dependencies:

```sh
pip install -r requirements.txt
```

### 3. Create a `.env` File

Create a `.env` file in the root directory of the project to store sensitive keys and configuration variables. Add the following content to the `.env` file:

```env
qdrant_host=your_qdrant_host
qdrant_key=your_qdrant_api_key
gemini_key=your_google_gemini_key
gemini_model=your_google_gemini_model
postgres_db=your_postgres_db_name
postgres_user=your_postgres_username
postgres_pass=your_postgres_password
```

Replace `your_qdrant_host`, `your_qdrant_api_key`, `your_google_gemini_key`, `your_google_gemini_model`, `your_postgres_db_name`, `your_postgres_username`, and `your_postgres_password` with your actual credentials and configuration details.

### 4. Configure Database Connection

In the `main.py` file, configure your Postgres database connection by updating the `POSTGRES_HOST` and `POSTGRES_PORT` variables if necessary. The default values are set to connect to a local Postgres instance.

### 5. Run the Application

Start the Streamlit application by running:

```sh
streamlit run app.py
```

This command will open the application in your web browser.

## Using the Application

1. **Ask a Question**: Enter a question about your data in the input box provided on the main page.
2. **View SQL Query**: If enabled in the sidebar, view the generated SQL query.
3. **View Data Table**: If enabled in the sidebar, view the resulting data table from the SQL query.
4. **View Plotly Code**: If enabled in the sidebar, view the generated Plotly code for visualization.
5. **View Chart**: If enabled in the sidebar, view the generated chart based on the Plotly code.
6. **View Summary**: If enabled in the sidebar, view the summary of the data.
7. **View Follow-up Questions**: If enabled in the sidebar, view suggested follow-up questions.

## Sidebar Settings

Use the sidebar to customize the output:
- **Show SQL**: Display the generated SQL query.
- **Show Table**: Display the resulting data table.
- **Show Plotly Code**: Display the generated Plotly code.
- **Show Chart**: Display the generated chart.
- **Show Summary**: Display the summary of the data.
- **Show Follow-up Questions**: Display suggested follow-up questions.
- **Reset**: Clear the current question and start over.

## Additional Notes

- The application uses cached data and computations to optimize performance. If you need to refresh the data, restart the Streamlit application.
- Ensure that your database schema is properly indexed and optimized for best performance when running complex SQL queries.

## Troubleshooting

- If you encounter issues with database connectivity, verify your credentials and connection settings in the `.env` file and `main.py`.
- Check the console output for any error messages that can provide insights into what might be going wrong.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

For any further questions or support, please open an issue in the GitHub repository or contact the maintainers.