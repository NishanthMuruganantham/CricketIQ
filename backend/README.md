# CricketIQ Backend

This is the Django backend for the CricketIQ application, serving an AI-powered cricket analytics API.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in this directory with the following:
    ```
    GEMINI_API_KEY=<your_api_key>
    MONGO_URI=<your_mongo_uri>
    MONGO_DB=CricketIQ
    MONGO_COLLECTION_DELIVERYWISE=deliverywise_data
    MONGO_COLLECTION_MATCHWISE=matchwise_data
    DJANGO_SECRET_KEY=<your_secret_key>
    DEBUG=True
    ```

3.  **Run Server**:
    ```bash
    python manage.py runserver
    ```

## API Endpoints

-   **Get Answer**: `POST /api/chat/ask/`
-   **Health Check**: `GET /health/`
-   **Homepage**: `GET /`
