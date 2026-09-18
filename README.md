# SmartMail AI

SmartMail AI is a full-stack newsletter platform that helps users create, send, and track email campaigns from one place. The main idea is simple: instead of writing a newsletter from scratch, an AI assistant creates the first draft, the user reviews and edits it, and the campaign can then be sent to a real subscriber list.

The project was built as a proper web application rather than a single script. The frontend, API, database, background workers, AI services, email provider, and webhook tracking all work together.

---

## What the project does

A typical campaign goes through this flow:

```text
User logs in
    ↓
Adds / manages subscribers
    ↓
Creates a campaign
    ↓
AI generates the newsletter draft
    ↓
User reviews and edits the draft
    ↓
Campaign is saved
    ↓
Campaign is queued for sending
    ↓
Celery worker sends the email through Brevo
    ↓
Subscriber receives the email
    ↓
Brevo sends delivery / engagement events back
    ↓
Webhook updates campaign delivery records
    ↓
Analytics are shown in the dashboard
    ↓
AI can analyze campaign performance
```

The human review step is intentional. AI generates the content, but the final decision to send it stays with the user.

---

## Main features

### Authentication

- User registration and login
- Password hashing with `pwdlib`
- JWT-based authentication
- Protected API routes
- User-specific campaign and subscriber data

### Subscriber management

- Add subscribers
- Edit subscriber details
- Delete subscribers
- Activate / deactivate subscribers
- Search subscribers
- Filter by status
- Paginated subscriber list

### AI newsletter generation

Users provide a topic, target audience, tone, length, and key points. The backend sends that information to the AI service and receives a structured newsletter containing:

- Subject
- Preview text
- Newsletter content
- Call-to-action text

The current setup uses Gemini as the primary AI provider and Groq as the fallback provider.

### Campaign management

- Create campaigns
- Save drafts
- Edit drafts
- Delete campaigns
- Send campaigns
- View campaign status
- View campaign analytics

Campaigns move through states such as:

```text
Draft → Sending → Sent
```

Failed campaigns can be handled separately and retried according to the backend rules.

### Email delivery

SmartMail AI uses Brevo for transactional email delivery. The application does not send large batches directly from the browser or through a personal Gmail SMTP account.

The backend places the work on a background queue, and Celery handles the actual sending task.

### Email tracking

Brevo can send webhook events such as:

- Sent
- Delivered
- Opened
- Clicked
- Bounced
- Complained
- Unsubscribed

These events are received by the FastAPI webhook endpoint and used to update the delivery records in PostgreSQL.

### Campaign analytics

Each campaign can show:

- Total recipients
- Sent
- Delivered
- Opened
- Clicked
- Bounced
- Complaints
- Unsubscribes
- Failed deliveries
- Delivery rate
- Open rate
- Click rate
- Bounce rate
- Complaint rate
- Unsubscribe rate

### AI campaign analysis

After a campaign has data, SmartMail AI can generate a short performance analysis containing:

- Summary
- Strengths
- Issues
- Recommendations

This is based on the actual campaign metrics stored by the application.

---

## Technology stack

### Frontend

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Recharts
- Lucide React

### Backend

- Python
- FastAPI
- Pydantic / Pydantic Settings
- SQLAlchemy
- PostgreSQL
- JWT authentication
- `pwdlib` for password hashing

### AI

- Google Gemini
- Groq fallback

### Background processing

- Celery
- Redis
- Upstash Redis for the hosted Redis instance

### Email

- Brevo transactional email API
- Brevo webhooks for delivery and engagement events

### Development / local infrastructure

- Uvicorn
- Cloudflare Quick Tunnel for exposing the local webhook during development
- Git / GitHub

---

## Architecture

```text
                         ┌─────────────────────┐
                         │      React UI       │
                         │  localhost:5173     │
                         └──────────┬──────────┘
                                    │ HTTP / JSON
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │  localhost:8000     │
                         └──────┬──────┬───────┘
                                │      │
                    ┌───────────┘      └──────────────┐
                    ▼                                  ▼
             ┌─────────────┐                    ┌─────────────┐
             │ PostgreSQL  │                    │ Gemini /    │
             │ application │                    │ Groq        │
             │ data        │                    │ AI services │
             └─────────────┘                    └─────────────┘
                    ▲
                    │
             ┌──────┴──────┐
             │  Webhook    │
             │  endpoint   │
             └──────▲──────┘
                    │
               Cloudflare Tunnel
                    ▲
                    │
             ┌──────┴──────┐
             │    Brevo    │
             │ email +     │
             │ webhooks    │
             └─────────────┘

               Background sending

        FastAPI → Redis → Celery worker → Brevo
```

### Why Redis and Celery are used

Sending a campaign can involve more than one recipient and should not block an HTTP request while the server is working through every email.

Instead, FastAPI creates the background task:

```text
FastAPI
   ↓
Redis queue
   ↓
Celery worker
   ↓
Brevo
```

The API can respond quickly while the worker handles the actual delivery work.

---

## Project structure

A simplified view of the repository looks like this:

```text
SmartMail-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── ai.py
│   │   │       ├── auth.py
│   │   │       ├── campaigns.py
│   │   │       ├── emails.py
│   │   │       ├── health.py
│   │   │       ├── subscribers.py
│   │   │       ├── webhooks.py
│   │   │       └── router.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   │
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tasks/
│   │   └── main.py
│
│   ├── .env
│   └── myenv/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   │   └── api.ts
│   │   ├── pages/
│   │   ├── types.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env
│
└── README.md
```

The exact repository can contain additional files, migrations, utilities, or configuration files depending on the current development version.

---

## Database overview

The application uses PostgreSQL for persistent data.

The important entities are:

```text
User
 │
 ├── Campaign
 │      │
 │      └── CampaignDelivery
 │                │
 │                └── Subscriber
 │
 └── Subscriber
```

### Users

Stores application accounts and authentication-related data.

### Subscribers

Stores the audience that receives newsletters. Subscriber records belong to a user account.

### Campaigns

Stores newsletter drafts and sent campaigns, including subject, content, CTA, audience information, status, and timestamps.

### Campaign deliveries

Stores the delivery state for each subscriber in a campaign. This is the table that lets the application turn Brevo webhook events into campaign analytics.

---

## API overview

The backend is mounted under:

```text
/api/v1
```

### Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
```

### Subscribers

```text
POST   /api/v1/subscribers
GET    /api/v1/subscribers
GET    /api/v1/subscribers/{subscriber_id}
PUT    /api/v1/subscribers/{subscriber_id}
DELETE /api/v1/subscribers/{subscriber_id}
```

The list endpoint supports pagination, search, and status filtering.

### Campaigns

```text
POST   /api/v1/campaigns
GET    /api/v1/campaigns
GET    /api/v1/campaigns/{campaign_id}
PUT    /api/v1/campaigns/{campaign_id}
DELETE /api/v1/campaigns/{campaign_id}
POST   /api/v1/campaigns/{campaign_id}/send
GET    /api/v1/campaigns/{campaign_id}/analytics
```

### AI

```text
POST /api/v1/ai/generate
POST /api/v1/ai/analyze-campaign/{campaign_id}
```

### Webhook

```text
POST /api/v1/webhooks/brevo
```

This endpoint is called by Brevo rather than by the frontend.

### Health

```text
GET /api/v1/health
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Environment variables

Create a `.env` file inside `backend/`.

A typical setup includes:

```env
PROJECT_NAME=SmartMail AI
VERSION=1.0.0
API_V1_STR=/api/v1
DEBUG=True
ENVIRONMENT=development

CORS_ORIGINS=http://localhost:5173

DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=smartmail_ai
DATABASE_USER=postgres
DATABASE_PASSWORD=your_database_password

JWT_SECRET_KEY=your_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

AI_PRIMARY_PROVIDER=gemini
AI_FALLBACK_PROVIDER=groq

GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=your_gemini_model

GROQ_API_KEY=your_groq_key
GROQ_MODEL=your_groq_model

EMAIL_PROVIDER=brevo
BREVO_API_KEY=your_brevo_api_key
BREVO_SENDER_NAME=SmartMail AI
BREVO_SENDER_EMAIL=your_verified_sender@example.com
EMAIL_TEST_RECIPIENT=your_test_email@example.com
BREVO_WEBHOOK_TOKEN=your_webhook_secret

REDIS_URL=your_upstash_redis_url
```

Do not commit `.env` to GitHub.

The frontend can use a Vite environment variable for the API base URL, for example:

```env
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

---

## Running the project locally

The application is easiest to run with four terminals.

### Terminal 1 — FastAPI

```powershell
cd C:\Users\HP\OneDrive\Desktop\SmartMail-AI\backend
.\myenv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### Terminal 2 — Celery

```powershell
cd C:\Users\HP\OneDrive\Desktop\SmartMail-AI\backend
.\myenv\Scripts\Activate.ps1
celery -A app.celery_app:celery_app worker --loglevel=info --pool=solo
```

The worker should eventually report that it is ready.

### Terminal 3 — Cloudflare tunnel

During local webhook development, expose the FastAPI server through Cloudflare:

```powershell
cloudflared tunnel --url http://localhost:8000
```

Copy the generated `trycloudflare.com` URL and use it as the base for the Brevo webhook endpoint:

```text
https://YOUR-TUNNEL.trycloudflare.com/api/v1/webhooks/brevo
```

A Quick Tunnel URL can change when the process is restarted. When that happens, the Brevo webhook destination needs to be updated.

### Terminal 4 — React

```powershell
cd C:\Users\HP\OneDrive\Desktop\SmartMail-AI\frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Brevo webhook setup

The webhook is important because email delivery happens outside the application.

The relationship is:

```text
Brevo
  ↓
POST /api/v1/webhooks/brevo
  ↓
FastAPI
  ↓
campaign_deliveries
  ↓
Analytics API
  ↓
React dashboard
```

### Authentication

The webhook uses a shared Bearer token.

The same secret must exist in both places:

```text
BREVO_WEBHOOK_TOKEN=your_secret
```

and in the Brevo webhook authentication settings.

### Local development

Because Brevo cannot call `localhost:8000` directly, Cloudflare is used to expose the webhook endpoint temporarily.

For production, the webhook should point directly to a stable HTTPS backend instead of a temporary Quick Tunnel URL.

---

## Using the application

### 1. Create an account

Open:

```text
http://localhost:5173
```

Register and log in.

### 2. Add subscribers

Open **Subscribers**, then add one or more real email addresses that you can access.

Avoid using placeholder addresses such as `user@example.com` when testing delivery.

### 3. Create a campaign

Open **AI Builder** and provide:

- Topic
- Audience
- Tone
- Length
- Key points

Generate the newsletter and review the returned subject, preview text, content, and CTA.

### 4. Edit and save

Make any manual changes you want and save the result as a draft.

### 5. Send

Open **Campaigns** and send a draft campaign.

The application queues the work instead of keeping the HTTP request busy while every email is being processed.

### 6. Check the inbox

Open the test recipient's inbox. If the message is not visible, also check spam / junk.

### 7. Check analytics

After Brevo sends the webhook events back, open the campaign analytics page. Delivery and engagement counters should update as events arrive.

### 8. Analyze the campaign

Use **Analyze with AI** to generate a human-readable summary of the campaign results.

---

## Security decisions

Several basic security measures are built into the backend:

- Passwords are stored as hashes, not plaintext passwords.
- JWTs are used for authenticated API requests.
- Protected resources are scoped to the logged-in user.
- Webhook requests use a separate shared secret.
- API keys stay on the backend.
- Subscriber and campaign ownership is checked in the backend rather than trusted from the frontend.
- Background email delivery is separated from the request/response cycle.
- The frontend never needs direct database credentials, AI API keys, or Brevo API keys.

For a production deployment, environment variables, HTTPS, a stable domain, stricter CORS, proper host configuration, logging, rate limiting, and secret rotation should be configured for the deployed environment.

---

## Common development issues

### White screen after login

A frontend page can fail if the API response shape does not match what the React component expects. For example, the subscribers endpoint returns a paginated object containing `items`, not a raw array.

### Brevo webhook shows failures

Check these first:

1. The Cloudflare tunnel is running.
2. The Brevo webhook URL points to the current tunnel URL.
3. The path is exactly `/api/v1/webhooks/brevo`.
4. The webhook token matches `BREVO_WEBHOOK_TOKEN`.
5. FastAPI is running on port `8000`.

### Email was sent but analytics are still zero

Email sending and webhook tracking are separate flows:

```text
Celery → Brevo → Recipient

and independently:

Brevo → Webhook → FastAPI → PostgreSQL
```

An email can be delivered even if the webhook is failing.

### Frontend cannot reach the API

Check that FastAPI is running and that the frontend API URL points to:

```text
http://127.0.0.1:8000/api/v1
```

### Celery is not processing messages

Check that Redis is reachable and that the Celery worker is running with the correct application import.

---

## Development notes

This project was built with a clear separation of responsibilities:

- React handles the user interface.
- FastAPI handles business logic and API access.
- PostgreSQL stores persistent application data.
- Redis holds queue-related data for background processing.
- Celery runs background tasks.
- Gemini / Groq handle AI operations.
- Brevo handles email delivery and event generation.
- Cloudflare is only used locally to expose the webhook during development.

That separation makes it easier to replace individual services later without rewriting the whole application.

---

## Future improvements

Possible next steps include:

- Stable production deployment with HTTPS
- Custom sending domain and email authentication
- Scheduled campaign execution
- Reusable newsletter templates
- Audience segmentation
- Import subscribers from CSV
- Rich HTML email templates
- More detailed click tracking
- Campaign comparison and historical reporting
- Redis-backed rate limiting and caching
- Automated tests and CI/CD

---

## License

This project is currently intended as a personal / academic project. Add a formal license here if you plan to publish the code for reuse.
