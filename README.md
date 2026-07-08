# TalentFlow Recruitment SaaS

**TalentFlow** is a modern, full-stack recruitment SaaS platform that revolutionizes candidate tracking, job board management, and HR operational workloads. Driven by AI and built for ease, TalentFlow provides beautiful dashboards, smart parsing for applicant resumes, and granular communication pipelines out of the box.

## 🚀 Features

*   **Customizable Recruitment Workflows**: Define your unique hiring stages dynamically when creating new jobs.
*   **AI Resume Analysis**: Parses uploaded PDFs into matched skills, weaknesses, and a dynamic "Match Score" against the job's requirements (powered by Groq Llama 3).
*   **Bulk Status Operations**: Easily filter applicants on your board and promote or reject batches of candidates asynchronously, reducing manual clicks.
*   **Smart Action Overlays**: Review, format, and customize email templates directly within a popup overlay before they fire off during a status change or interview scheduling. 
*   **Interviews & Scheduling**: Book candidate interviews directly within their profile with personalized Zoom/Meet invites and calendar dates.
*   **Beautiful Interfaces**: Crafted using vanilla React/CSS utilizing a modern "Futuristic Minimalist Light" design language with animations, neon accents, and smooth glassmorphism.
*   **Public 'Apply' Job Boards**: Instantly deploy application pages that accept direct candidate resumes into the backend.
*   **Role-based Architecture**: Includes robust recruiter login, registration, dashboard analytics, and job poster generation.

## 🛠 Tech Stack

**Frontend**:
*   React 18 + Vite
*   React Router DOM
*   Recharts (Analytics)
*   Lucide React (Icons)
*   Vanilla CSS Modules using modern `var()` tokenization

**Backend**:
*   Python 3 & FastAPI
*   MongoDB (Motor AsyncIO)
*   JWT Bearer Authentication
*   Python-Jose & Bcrypt (Security)
*   Groq API (AI Llama Model)
*   Cloudinary (Resume PDF Media hosting)
*   SMTP Email Dispatch Services

## 🏁 Getting Started

These instructions will get your copy of the project up and running on your local machine for development and testing purposes.

### 1. Prerequisites
Ensure you have the following installed on your system:
*   [Node.js (18+ recommended)](https://nodejs.org/)
*   [Python (3.9+ recommended)](https://www.python.org/downloads/)
*   [MongoDB Atlas Account](https://www.mongodb.com/atlas/database)
*   [Cloudinary Account](https://cloudinary.com)
*   [Groq API Key](https://console.groq.com/keys)

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Virtual Environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the `backend/` directory based on this template:
   ```env
   # Database Configuration
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0...
   DB_NAME=talentflow

   # Security
   JWT_SECRET=generate_your_own_secure_key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60

   # AI Integration
   GROQ_API_KEY=your_groq_llama_key

   # SMTP Configuration (For Google Accounts, use 16-character App Password)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password

   # Storage Media
   CLOUDINARY_CLOUD_NAME=your_cloud
   CLOUDINARY_API_KEY=your_key
   CLOUDINARY_API_SECRET=your_secret
   UPLOAD_DIR=uploads
   ```
5. *(Optional)* Turn on **PDF delivery** in your Cloudinary Dashboard under *Settings > Security*.
6. Start the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --port 8000 --reload
   ```

### 3. Frontend Setup
1. Open a new terminal instance and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Create a `.env` file in the `frontend/` directory (or copy from `.env.example`):
   ```env
   # Backend API URL
   VITE_API_URL=http://localhost:8000
   ```
   > In development, Vite's built-in proxy forwards `/api` requests to this URL. In production builds, `VITE_API_URL` is baked into the bundle and used directly by the API client.

3. Install NodeJS packages:
   ```bash
   npm install
   ```
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
5. Visit `http://localhost:3000` in your web browser.

## 📦 Deployment (Production)

To deploy the application to a live internet server, keep note that the backend is distinct from the frontend:

1. **Frontend**: The `frontend/` directory can be connected to Vercel, Netlify, or Render out-of-the-box. Ensure your production settings use generic `.env` strings directing Vite router to your final backend IP/Domain.
2. **Backend**: Host the FastAPI server on platforms like Heroku, Render, AWS EC2, or DigitalOcean. Configure your hosting platform to securely house the exact variables found in your `.env`.

> **Important Security Notice:** Local test implementations using `USE_CLOUDINARY=False` will crash ephemeral backend servers in production. Ensure Cloudinary PDF restriction limits are deactivated on your Cloudinary dashboard in production instances so resumes are correctly served over the cloud.

---

*Designed by the TalentFlow recruitment software team.*
