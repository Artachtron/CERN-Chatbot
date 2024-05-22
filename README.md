# CERN Chatbot
<img src="https://raw.githubusercontent.com/Unstructured-IO/unstructured-api-tools/main/img/unstructured_logo.png" title="Unstructured.io" width="25" /><img src="https://devblogs.microsoft.com/azure-sql/wp-content/uploads/sites/56/2024/02/langchain.png" title="LangChain" width="25" />
<img src="https://bookface-images.s3.amazonaws.com/logos/ee60f430e8cb6ae769306860a9c03b2672e0eaf2.png" title="Ollama" width="25" />
<img src="https://d11a6trkgmumsb.cloudfront.net/original/4X/8/1/1/811ef156e2525559c859ecdb7a5cd26d5e459e46.png" title="Weaviate" width="25" />
<img src="https://cdn-lfs.huggingface.co/repos/96/a2/96a2c8468c1546e660ac2609e49404b8588fcf5a748761fa72c154b2836b4c83/942cad1ccda905ac5a659dfd2d78b344fccfb84a8a3ac3721e08f488205638a0?response-content-disposition=inline%3B+filename*%3DUTF-8%27%27hf-logo.svg%3B+filename%3D%22hf-logo.svg%22%3B&response-content-type=image%2Fsvg%2Bxml&Expires=1716474473&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTcxNjQ3NDQ3M319LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2RuLWxmcy5odWdnaW5nZmFjZS5jby9yZXBvcy85Ni9hMi85NmEyYzg0NjhjMTU0NmU2NjBhYzI2MDllNDk0MDRiODU4OGZjZjVhNzQ4NzYxZmE3MmMxNTRiMjgzNmI0YzgzLzk0MmNhZDFjY2RhOTA1YWM1YTY1OWRmZDJkNzhiMzQ0ZmNjZmI4NGE4YTNhYzM3MjFlMDhmNDg4MjA1NjM4YTA%7EcmVzcG9uc2UtY29udGVudC1kaXNwb3NpdGlvbj0qJnJlc3BvbnNlLWNvbnRlbnQtdHlwZT0qIn1dfQ__&Signature=Emd1ceDud-3eDpOi32qIKc9j53%7Evc5hfFdKteUqWsaNvz6mJr5bw52rbGhIR1OHFF-l7T0RTUpwy-Tw1AhNUPHbxmA0oSzU8ztz80HlToHs5ugdm8y1DYJTnaMCbmkMD1n-BTxMd7h9kjTcOqRt8u-WJtPaobnAAPlWNU7L8jrNGVi3r4YOxwnjgyq0-U9qGdW4kROdpiRgPduihgtyIzrg7kPryOlySmdfNpUoH-YPyUIOtMAT9oVThHyIF88s-EPW6ylOsbSdsCY35suloqHeotA2Ps--iw7pZ8M0fSAZ6LwMRYKN2oNEmwXJWOK1%7Enj-oBzOnQU31UlMBizOOzA__&Key-Pair-Id=KVTP0A1DKRTAX" title="HuggingFace" width="25" />
<img src="https://asset.brandfetch.io/idfDTLvPCK/idfkFVkJdH.png" title="CohereAI" width="25" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/fastapi/fastapi-original.svg" title="FastAPI" width="25" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/nextjs/nextjs-original.svg" title="Next.js" width="25" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/react/react-original.svg" title="React" width="25" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/materialui/materialui-original.svg" title="Material-UI" width="25" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/docker/docker-original.svg" title="Docker" width="25" />

![Preview](docs/preview.gif)

## Description
This project features a custom-built chatbot designed specifically for inquiries related to the Large Hadron Collider (LHC). Leveraging data from the 'LHC The Guide' brochure, I meticulously curated and converted it into a database for rapid retrieval. The chatbot excels in delivering accurate responses by efficiently fetching pertinent information from its database. With its intuitive interface and streamlined operation, users can expect swift and reliable answers to their inquiries regarding the LHC. Explore the world of particle physics effortlessly with our LHC Inquiry Chatbot!

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)

## Installation

To install and set up this project, follow these steps:

### Frontend

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Artachtron/CERN-Chatbot.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd CERN-Chatbot
    ```

3. **Frontend Setup:**

    ```bash
    # Go to frontend directory
    cd frontend
    
    # Install dependencies
    # Note: npm (Node Package Manager) is required to manage dependencies. 
    # If you don't have npm installed, follow the installation guide at https://docs.npmjs.com/downloading-and-installing-node-js-and-npm
    npm install
    ```

### Backend

1. **Navigate to the backend directory:**

    ```bash
    cd ../backend
    ```

2. **Install dependencies:**

    ```bash
    # Note: Poetry is required to manage dependencies. 
    # If you don't have Poetry installed, follow the installation guide at https://python-poetry.org/docs/#installation
    poetry install
    ```

After completing these steps, your project's frontend and backend will be set up with all necessary dependencies installed.

## Usage

To use this project, follow these steps:

### From Terminal
To run this project from a terminal, follow these steps:

#### Backend

1. **Navigate to the backend directory:**

    ```bash
    cd backend/src
    ```

2. **Run the backend API:**

    ```bash
    poetry run python api/main.py
    ```

#### Frontend

1. **Navigate to the frontend directory:**

    ```bash
    cd frontend/src
    ```

2. **Run the frontend application:**

    ```bash
    npm run dev
    ```

3. **Access Homepage:**

   Open your web browser and navigate to [http://localhost:3000/](http://localhost:3000/)


After completing these steps, you should have both the backend API and frontend application running. You can upload CT scan images through the frontend interface and obtain diagnostic results.

### From Container
To use this project from a Docker container, follow these steps:

1. **Ensure Docker is installed and running on your system.**

2. **Navigate to the root folder of the project:**

3. **Run Docker Compose:**

    ```bash
    # Note: Docker and Docker Compose are necessary.
    docker-compose up
    ```
4. **Access Homepage:**

   Open your web browser and navigate to [http://localhost:3000/](http://localhost:3000/)

After completing these steps, your project's frontend and backend will be set up and running in Docker containers, ready for use.
