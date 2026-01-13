# Month-End Close Automator

## Description
This is a Minimum Viable Product (MVP) built to automate the process of gathering and reading accounting data. The goal is to save time during the month-end close process and reduce the risk of human error.

## The 'Mentor' Approach
This project follows a "modular" approach to coding, which is a key best practice. Instead of putting everything in one big file, we split the code into separate, organized files:
*   **`processor.py`**: This file handles specific tasks like reading the data.
*   **`app.py`**: This is the main entry point that runs the application in the terminal.
*   **`main.py`**: This runs the Web API server using FastAPI.
*   **`requirements.txt`**: Keeps track of all the external tools we are using.

This keeps the project clean, organized, and easier to manage as it grows.

## Installation
To get started, you need to install a few tools. Open your terminal or command prompt and run:

```bash
pip install -r requirements.txt
```

## Usage
To run the application and see your transaction data, type the following into your terminal:

```bash
python app.py
```

### Web API
To run the web server and access the data as JSON:

1.  Run the server:
    ```bash
    python -m uvicorn main:app --reload
    ```
2.  Open your browser to: `http://127.0.0.1:8000/transactions`

