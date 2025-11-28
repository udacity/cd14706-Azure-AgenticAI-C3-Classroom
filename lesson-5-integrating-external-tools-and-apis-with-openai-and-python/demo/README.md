# Lesson 5 Demo: Sports Analyst Agent with External APIs

This demo showcases a sports analyst agent that integrates with external APIs to provide real-time sports information.

## Features

- **Semantic Kernel Setup**: Configures Semantic Kernel with Azure OpenAI services.
- **External API Integration**: Connects to the [NewsAPI](https://newsapi.org/) for sports news and the [Ball Don't Lie API](https://balldontlie.io/) for NBA player statistics.
- **Mock Data Fallback**: Includes mock data for sports scores and team standings, and provides a fallback for the player stats API if it fails.
- **Structured Output**: Uses Pydantic models to ensure the agent's responses are in a structured JSON format.

## Setup Instructions

1.  **Install Dependencies**: Install all the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables**:
    -   Copy the `.env.example` file to a new file named `.env`.
    -   Open the `.env` file and fill in your specific credentials for the following services.

### Required API Keys

This demo requires API keys for two external services to function fully.

#### NewsAPI (for Sports News)

-   Go to [https://newsapi.org/](https://newsapi.org/) and register for a free developer account.
-   Once registered, you will find your API key on your account dashboard.
-   Copy this key into the `.env` file for the `NEWSAPI_KEY` variable.

#### Ball Don't Lie API (for NBA Player Stats)

-   The `balldontlie` API is used to fetch live NBA player statistics. Without a valid API key, this tool will rely on its internal mock data as a fallback.
-   Go to [https://balldontlie.io/](https://balldontlie.io/) and sign up for an account.
-   You can find your API key in your account settings after signing in.
-   Copy this key into the `.env` file for the `BALLDONTLIE_API_KEY` variable.

3.  **Run the Demo**: Execute the `main.py` script to see the agent in action.
    ```bash
    python main.py
    ```