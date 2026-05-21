# Full-Stack Task Manager Application

A modern, secure, full-stack Task Management application featuring a decoupled architecture with a FastAPI production backend engine and an interactive, clean vanilla JavaScript/HTML frontend.

## 🔗 Live Deployments
* **Live Frontend Website:** https://fastapi-task-manager-7yxub5gwv-persis-w-s-projects.vercel.app/
* **Production API Documentation:** https://fastapi-task-manager-rxqc.onrender.com/docs

---

## 🚀 Project Overview
This application provides a complete task tracking solution equipped with secure user authorization.
* **Backend:** Built using **FastAPI** utilizing a modular router architecture. It handles user authentication, automated request validation, and object persistence.
* **Frontend:** A responsive **Single Page Application (SPA)** that handles client-side state management, asynchronous fetch requests, and dynamic DOM manipulation.
* **Security:** Implements **native bcrypt** password hashing alongside secure **JWT (JSON Web Tokens)** for stateless session management.
* **Database:** Structured data storage using **SQLAlchemy ORM** interacting with a SQLite database.

---

## 🛠️ Tech Stack
* **Frontend:** HTML5, CSS3 (Modern Flexbox/Grid), Vanilla JavaScript (ES6+)
* **Backend:** Python 3.10+, FastAPI, Uvicorn
* **Database & ORM:** SQLite, SQLAlchemy
* **Security & Auth:** Native Bcrypt, PyJWT / Python-Jose

---

## 🔑 Environment Variables

The backend engine requires the following configurations. For local development, create a `.env` file inside the `backend/` directory:

```env
SECRET_KEY=your_super_secret_jwt_signing_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30