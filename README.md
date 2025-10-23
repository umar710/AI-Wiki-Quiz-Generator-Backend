# 🧠 AI Wiki Quiz Generator (Backend)

A **FastAPI** service that converts **Wikipedia articles** into **AI-generated quizzes** using **Google Gemini**, with data stored in **PostgreSQL**.

## 🚀 Features

* 📝 Scrapes Wikipedia content
* 🤖 Generates quizzes using Google Gemini
* 💾 Saves quiz history in PostgreSQL
* 🌐 RESTful FastAPI endpoints (Swagger docs included)
* 🔐 CORS enabled for frontend integration

## 🛠️ Tech Stack

**FastAPI**, **PostgreSQL/SQLite**, **SQLAlchemy**, **BeautifulSoup4**, **Gemini AI**

## 📡 API Endpoints

| Method | Endpoint          | Description                      |
| ------ | ----------------- | -------------------------------- |
| GET    | `/`               | Health check                     |
| POST   | `/generate_quiz`  | Generate quiz from Wikipedia URL |
| GET    | `/history`        | Get quiz history                 |
| GET    | `/quiz/{quiz_id}` | Get quiz by ID                   |
| GET    | `/docs`           | API Docs (Swagger UI)            |

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd ai-quiz-generator/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add `.env`

```
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=sqlite:///./quiz_history.db
```

### 3. Run Server

```bash
uvicorn main:app --reload
```

Visit → [http://localhost:8000/](http://localhost:8000/)

## 🚀 Deploy on Render

1. Push to GitHub
2. Create PostgreSQL DB on Render
3. Create a Web Service using `render.yaml`
4. Set env vars:

   * `GEMINI_API_KEY`
   * `DATABASE_URL` (auto from Render)

**Start Command:**

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 📦 Example Request

```bash
curl -X POST "https://your-backend.onrender.com/generate_quiz" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}'
```

## ⚠️ Troubleshooting

* Ensure `DATABASE_URL` starts with `postgresql://`
* Verify `GEMINI_API_KEY`
* Use valid Wikipedia URLs

---

**🧩 Backend Live Demo:** [https://ai-wiki-quiz-generator-backend.onrender.com]

**💻 Frontend Repo:** [https://ai-wiki-quiz-generator-frontend.vercel.app/]

