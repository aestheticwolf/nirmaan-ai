# NIRMAAN.AI

**Intelligent building design, compliance evaluation, and CAD layout generation for real-estate planning.**

NIRMAAN.AI is a full-stack prototype for planning residential buildings. It brings plot and building inputs, rule-based compliance checks, AI-assisted room layouts, and DXF generation into one workflow. The current UI presents the platform as a planning system for Goa and Maharashtra.

> This is a development project. It must be run with both the Next.js frontend and the FastAPI backend started locally.

## What it does

- Admin sign-in backed by a PostgreSQL `admins` table.
- Interactive planning workspace for plot dimensions, road width, floor count, FAR, coverage, and planning zone.
- Rule-based compliance evaluation using state, authority, regulation, and rule records stored in PostgreSQL.
- Rule management API (create, read, update, and delete rules).
- Standard CAD generation and DXF download.
- Prompt-based room-layout generation, with a deterministic rule-based fallback.
- AI-assisted CAD generation and prompt-based layout edits.
- Dashboard API for project, building, layout, and compliance totals.

## Tech stack

| Area | Technology |
| --- | --- |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Backend | Python, FastAPI, Uvicorn, SQLAlchemy, Pydantic |
| Database | PostgreSQL via `psycopg2` |
| CAD export | `ezdxf` (DXF files) |
| Optional AI provider | Google Generative AI |

## Repository layout

```text
.
├── nirmaan-ui/                 # Next.js web application
│   ├── app/                    # Landing page and dashboard routes
│   ├── components/             # Landing and dashboard components
│   └── public/                 # Logo and static assets
├── nirmaan-backend/            # FastAPI service
│   ├── app/
│   │   ├── models/             # SQLAlchemy PostgreSQL models
│   │   ├── routes/             # Auth, CAD, rules, dashboard, layout APIs
│   │   ├── schemas/            # Request validation schemas
│   │   └── services/           # CAD, layout AI, and rule-engine logic
│   ├── generated/              # Generated DXF files
│   └── .env                    # Local database configuration (not committed)
└── README.md
```

## Prerequisites

- Node.js 20 or later and npm.
- Python 3.11 or later.
- PostgreSQL 14 or later, running and reachable from your machine.
- An existing PostgreSQL database containing the required application tables and initial data, including an admin record.

## Quick start

### 1. Configure the database

Create `nirmaan-backend/.env` with a PostgreSQL SQLAlchemy connection URL:

```dotenv
DATABASE_URL=postgresql+psycopg2://POSTGRES_USER:POSTGRES_PASSWORD@localhost:5432/DATABASE_NAME
```

Replace the placeholder values with your local PostgreSQL connection details. Never commit `.env` files or database passwords.

When the backend starts, it calls `Base.metadata.create_all()` and creates any registered tables that do not already exist. It does **not** seed an admin account, states, authorities, regulations, or rules. Add those records in PostgreSQL before using the associated features.

### 2. Install and run the backend

In one PowerShell terminal:

```powershell
cd A:\0\infipre\nirmaan\nirmaan-backend

# Optional: create a virtual environment if one does not exist
py -3.11 -m venv venv

# Install runtime dependencies
.\venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary python-dotenv ezdxf google-generativeai

# Start the API at http://127.0.0.1:8000
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For automatic reload while editing backend files, append `--reload` to the final command.

Confirm the backend is available at:

- API health response: `http://127.0.0.1:8000/`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 3. Install and run the frontend

In a second PowerShell terminal:

```powershell
cd A:\0\infipre\nirmaan\nirmaan-ui
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

The frontend calls the backend at `http://127.0.0.1:8000`. Keep both terminal windows running. If port 8000 is already in use, the backend is likely already running; stop the existing process or use that running instance.

## Login

The sign-in page accepts an email and password checked against the PostgreSQL `admins` table.

```sql
SELECT id, email, password_hash
FROM admins;
```

Use the row's `email` and the corresponding configured password value. No demo account or password is seeded in this repository. For local development, inspect or manage that table through pgAdmin or another PostgreSQL client.

## Application flow

1. Open the landing page and sign in.
2. Go to the planning workspace.
3. Enter plot dimensions, road width, planning details, floor count, FAR, and coverage.
4. Review local planning guidance and rule results.
5. Generate a standard DXF layout or provide a text prompt for an AI-assisted layout.
6. Download the generated `.dxf` file from the browser.

## API reference

The full, live API specification is available at `/docs` when the backend is running.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Backend status message |
| `POST` | `/login` | Validate an admin email and password |
| `POST` | `/generate-cad` | Save plot/building details, generate a DXF, return download metadata |
| `GET` | `/download/{filename}` | Download a generated DXF file |
| `POST` | `/cad/generate` | Generate a DXF layout without saving the standard request records |
| `POST` | `/generate-ai-layout` | Create a room layout from a prompt |
| `POST` | `/generate-ai-cad` | Generate a prompt-based layout and its DXF file |
| `POST` | `/layout/edit` | Apply supported prompt edits to an existing layout and regenerate DXF |
| `POST` | `/rules/evaluate` | Evaluate active rules for a state and newly created design |
| `GET` | `/rules/` | List rules |
| `POST` | `/rules/` | Create a rule |
| `PUT` | `/rules/{rule_id}` | Update a rule |
| `DELETE` | `/rules/{rule_id}` | Delete a rule |
| `GET` | `/dashboard/stats` | Return project, building, generated-layout, and compliance metrics |
| `GET` | `/dashboard/designs` | Return compliance summaries by design |
| `GET` | `/dashboard/design/{design_id}` | Return rule results for one design |
| `GET` | `/dashboard/rules` | Return active rules in a dashboard-friendly shape |

### Example: generate a DXF

```bash
curl -X POST http://127.0.0.1:8000/generate-cad \
  -H "Content-Type: application/json" \
  -d '{
    "plot": { "length": 30, "width": 20, "road_width": 12 },
    "building": { "floors": 2 }
  }'
```

The response includes a `download_url`, such as `/download/layout_<id>.dxf`.

## Database model

The application uses these PostgreSQL tables:

| Table | Role |
| --- | --- |
| `admins` | Admin login records |
| `plots` | Plot dimensions and road width |
| `buildings` | Floor count linked to a plot |
| `designs` | Design records used by rule evaluation |
| `compliance_results` | Pass/fail result for each evaluated rule |
| `states` | Supported states |
| `authorities` | Authorities linked to states |
| `regulations` | Active regulations linked to authorities |
| `rules` | Active compliance rules and JSON rule logic |
| `project_versions` | Version metadata for projects |
| `layouts` | Generated-layout metadata model |

For the compliance engine to produce results, the database needs an active chain of records:

```text
state → authority → regulation → rule
```

Rule logic is read from the `expression_logic` JSON field. It uses a left-hand context key, a comparison operator (`<=`, `>=`, `<`, `>`, or `==`), and a right-hand numeric value. Supported context keys include `plot_area`, `length`, `width`, `road_width`, `floors`, `far`, and `coverage`.

## AI layout behavior

By default, AI layout generation is deterministic and does not call an external model. It interprets prompts to choose a bedroom count and optionally include parking/garage or dining, then arranges common rooms by zone.

The optional Gemini implementation is disabled by default (`USE_AI = False` in `app/services/ai_layout.py`). To enable it, set `USE_AI` to `True` in that service and configure:

```dotenv
GEMINI_API_KEY=your_key_here
```

The current implementation imports `google-generativeai`, which emits a deprecation warning. Consider migrating the service to the supported `google-genai` SDK before production use.

## CAD output

Generated DXF files are written to `nirmaan-backend/generated/`. Exports include plot and setback boundaries, building walls, windows, doors, parking, dimensions, and a north indicator. Prompt-based layouts can additionally include room walls and labels, selected furniture, kitchen/bathroom fixtures, and stairs for multi-floor buildings.

The generated directory can grow over time. Archive or clean development exports as needed, but do not remove files still required by users.

## Development commands

### Frontend

```powershell
cd nirmaan-ui
npm run dev       # Development server
npm run lint      # ESLint
npm run build     # Production build
npm run start     # Serve production build
```

### Backend

```powershell
cd nirmaan-backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Security and production notes

- The current login route compares the submitted password directly to `admins.password_hash`; it does not hash or verify passwords securely. Replace this with a password-hashing scheme such as Argon2 or bcrypt before deployment.
- The API currently has no session or token authentication. The frontend stores a local browser flag after a successful login. Protect all dashboard and write endpoints before deploying.
- CORS is limited to local frontend origins. Configure explicit production origins for deployment.
- Validate and authorize rule changes, CAD generation, and file downloads in a production environment.
- Keep `DATABASE_URL`, `GEMINI_API_KEY`, and generated sensitive files out of Git.

## Troubleshooting

| Problem | Resolution |
| --- | --- |
| `Backend connection error` in the browser | Start the backend on `127.0.0.1:8000` and keep it running. |
| Port 8000 is already in use | A backend is already running. Use it, or stop its process before starting another instance. |
| Database connection fails | Check that PostgreSQL is running and that `DATABASE_URL` in `.env` is correct. |
| Login returns `Invalid credentials` | Verify the `admins` row in PostgreSQL. This repository does not create demo credentials. |
| Rule evaluation returns no results | Create active state, authority, regulation, and rule records with the necessary links. |
| AI/CAD generation fails | Check the request has positive plot length/width and the backend dependencies are installed. |
| Google package deprecation warning | It is non-blocking for the current code; plan a migration to `google-genai`. |

## License

No license has been specified. Add a license file before distributing or accepting external contributions.
