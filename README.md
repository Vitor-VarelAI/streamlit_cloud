# 🧠 Reddit Insights Tool

An internal research tool to explore real user problems, questions, and discussions from Reddit.

It fetches **recent posts**, classifies them using **OpenAI**, and optionally summarizes full discussions with **Firecrawl**.
Great for idea validation, niche exploration, and building better content or products.

---

## ✨ Features

- 🔍 Search any keyword or subreddit
- 🧠 Classify Reddit posts by intent (question, pain point, advice, etc.)
- 📝 Summarize full Reddit threads via Firecrawl (when link is pasted)
- 🧪 Validate ideas using Perplexity (optional)
- ⚡ Built with Streamlit for fast UI
- 🔐 API keys stored securely via Streamlit Secrets

---

## 📦 Tech Stack

- Python + Streamlit
- [PRAW](https://praw.readthedocs.io/) (Reddit API)
- [OpenAI](https://platform.openai.com/)
- [Firecrawl](https://firecrawl.dev/)
- [Perplexity API](https://docs.perplexity.ai/)

---

## 🔐 Required API Keys / Secrets

This application requires API keys for Reddit, OpenAI, and Firecrawl to function fully. Perplexity is optional.

**Configuration:**

Keys must be configured using **Streamlit Secrets**. When running locally, you can create a file named `.streamlit/secrets.toml`.

**Format for `secrets.toml` (or Streamlit Cloud Dashboard):**

```toml
[reddit]
client_id = "YOUR_REDDIT_CLIENT_ID"
client_secret = "YOUR_REDDIT_CLIENT_SECRET"
user_agent = "python:your_app_name:v1.0 (by /u/your_username)"
# username = "YOUR_REDDIT_USERNAME" # Optional, needed only if not using read-only
# password = "YOUR_REDDIT_PASSWORD" # Optional, needed only if not using read-only

[openai]
api_key = "sk-YOUR_OPENAI_API_KEY"

[firecrawl]
api_key = "fc-YOUR_FIRECRAWL_API_KEY"

# [perplexity] # Optional
# api_key = "pplx-YOUR_PERPLEXITY_API_KEY"
```

**Note:** Ensure you replace the placeholder values with your actual keys. For deployment on Streamlit Cloud, enter these secrets directly into the application settings dashboard.

---

## 🚀 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Vitor-VarelAI/streamlit_cloud.git
    cd streamlit_cloud
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate  # Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Secrets:**
    Create a file `.streamlit/secrets.toml` and add your API keys as shown in the format above.

5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

---

## ✅ Example Use Cases

- Find real problems in niche communities
- Research how people talk about a product
- Generate content ideas based on actual discussions
- Validate assumptions before building

---

## 📌 Roadmap (Potential Ideas)

- Export insights to Notion/CSV
- Filter by intent (question, rant, etc.) more explicitly
- Pagination and "load more" for search results
- Highlight common pain points by frequency

---

## 🧑‍💻 Author

Built by [@Vit0rVarela](https://x.com/Vit0rVarela) — because paying for insight tools is cool,
but building your own is smarter. 