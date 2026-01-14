# Month-End Close Automator

## Description
This is a Minimum Viable Product (MVP) built to automate the process of gathering and reading accounting data. The goal is to save time during the month-end close process and reduce the risk of human error.

## The 'Mentor' Approach
This project follows a "modular" approach to coding, which is a key best practice. Instead of putting everything in one big file, we split the code into separate, organized files:
*   **`processor.py`**: This file handles specific tasks like reading the data.
*   **`app.py`**: This is the main entry point that runs the application in the terminal.
*   **`main.py`**: This runs the Web API server using FastAPI.
*   **`requirements.txt`**: Keeps track of all the external tools we are using.
*   **`reporter.py`**: Generates styled Excel reports.

This keeps the project clean, organized, and easier to manage as it grows.

## Installation
To get started, you need to install a few tools. Open your terminal or command prompt and run:

```bash
python -m pip install -r requirements.txt
```

## Usage
To run the application and see your transaction data, type the following into your terminal:

```bash
python app.py
```

### Web UI (Browser)
To use the modern web interface for uploading files and generating reports:

1.  Run the server:
    ```bash
    python -m uvicorn main:app --reload
    ```
2.  Open your browser (Chrome/Edge) to: `http://127.0.0.1:8000`
3.  **Upload**: Click "Choose File" and select your transactions CSV.
4.  **Process**: Click "Upload & Process".
5.  **Download**: Click the "Download Report" button to get your styled Excel file.

### REST API
You can also access the raw JSON data directly:
*   `GET /transactions`: Triggers manual report generation from default file.
