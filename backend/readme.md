<!-- @format -->

# Email Classification Backend

This backend service is responsible for handling email classification tasks. It is built using FastAPI and can be run using Uvicorn.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed Python 3.7 or higher.
- You have installed Uvicorn.
- You have installed FastAPI.

## Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/email-classification.git
```

2. Navigate to the backend directory:

````sh
cd email-classification/backend

3. Create a virtual environment:

```sh
python -m venv venv
````

4. Activate the virtual environment:

- On Windows:
  ```sh
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```sh
  source venv/bin/activate
  ```

5. Install the required dependencies:

```sh
pip install -r requirements.txt
```

## Running the Server

To start the server, run the following command:

```sh
python uvicorn_config.py
```

The server will start on `http://127.0.0.1:8000`.

## Usage

Once the server is running, you can access the API documentation at `http://127.0.0.1:8000/docs`.
