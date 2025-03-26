<!-- @format -->

# Email Classification Frontend

This repository contains the frontend code for the Email Classification project.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed [Node.js](https://nodejs.org/) (v14 or later).
- You have a running instance of the backend server. Refer to the backend repository for setup instructions.

## Updating Backend API Context

To ensure the frontend communicates correctly with the backend, update the backend API context by creating a `.env` file in the frontend root level:

1. Create a `.env` file in the `email-classification/frontend` directory.
2. Add the following line to the `.env` file, replacing `your-backend-server-url` with the actual backend server URL:

```
VITE_API_BASE_URL=http://your-backend-server-url
```

## Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/email-classification.git
```

2. Navigate to the frontend directory:

```sh
cd email-classification/frontend
```

3. Install the dependencies:

```sh
npm install
```

## Running the Application

1. Start the development server:

```sh
npm run dev
```

2. Open your browser and navigate to `http://localhost:3000`.

## Building for Production

To create a production build, run:

```sh
npm run build
```
