```
CHATBOT-STREAMLIT-LANGCHAIN
├── .github/workflows/
│ └── ci.yml # CI/CD pipeline configuration
│
├── backend/
│ ├── Dockerfile # Docker image definition for backend
│ ├── main.py # Main backend logic
│ └── pydantic_models.py # Data validation models
│
├── frontend/
│ ├── Dockerfile # Docker image definition for backend
│ └── app.py # Streamlit frontend application
│
├── notebooks/
│ └── STREAMLIT_LANGCHAIN_CHATBOT_... # Jupyter notebooks (experiments/tests)
│
├── tests/
│ ├── backend/
│ │ ├── test_main.py
│ │ └── test_pydantic_models.py
│ │
│ └── frontend/
│   └── test_app.py
│
├── docker-compose.yml # Docker Compose configuration
│
├── .env # Environment variables (not tracked in git)
│
├── .gitignore # Ignored files configuration
│
├── pytest.ini # Pytest configuration
│
├── requirements.txt # Project dependencies
│
└── README.md # Project documentation
```