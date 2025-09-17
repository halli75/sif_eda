# SIF_EDA – Polymarket Trader Explorer

This repository contains all of the scaffolding needed to build a full‑stack
exploratory data analysis (EDA) platform for the Polymarket trader dataset.
It combines a PostgreSQL data warehouse, a FastAPI backend, a Next.js
frontend, and a written report explaining the methodology and key insights.

The dataset you provided has been split into three Git LFS files (located in
`data/`), each representing roughly one third of the original `traders.csv`.
Due to the size of the files, only pointer files are checked in here. To
replicate the analysis end‑to‑end you will need to download the CSV parts
locally (see the `data/README.md` for details) and load them into the
database using the scripts provided.

## Contents

* **`db/`** – SQL scripts for defining the raw and typed tables as well as
  computed materialized views. Running these scripts on an empty Postgres
  database will set up the schema described in the proposal.
* **`backend/`** – A FastAPI application exposing REST endpoints that
  operate on the pre‑aggregated tables. Endpoints include summaries,
  label audits, footprint‑edge scatter data, topic analyses and archetype
  groupings. The backend uses async SQLAlchemy and serves JSON.
* **`frontend/`** – A Next.js scaffolding using Tailwind CSS and shadcn/ui.
  This skeleton defines pages for the five hero views and includes
  placeholder components where charts will later be integrated.
* **`analysis/essay.md`** – A narrative report explaining the goals,
  methodology and high level findings of the EDA. The same content is
  reproduced below in the body of the chat for convenience.

## Quickstart

1. **Install dependencies**

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create a Postgres database** and apply the schema:

   ```bash
   createdb polymarket
   psql -d polymarket -f ../db/create_tables.sql
   psql -d polymarket -f ../db/compute_metrics.sql
   ```

3. **Load the CSV data**. Copy your three CSV parts into a directory on
   your machine and run the ETL script:

   ```bash
   python backend/etl.py --db-url postgresql://user:pass@localhost/polymarket \
                        --csv-dir /path/to/csv_parts
   ```

4. **Run the backend**:

   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

5. **Run the frontend** (requires Node.js installed):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Then open `http://localhost:3000` in your browser to explore the
   application. You can adjust the API base URL in `frontend/utils/api.ts`
   if you are serving the backend on a different port or host.

## Notes

* The provided SQL scripts create materialized views that pre‑aggregate
  expensive computations (such as entropy and z‑scores). You can refresh
  these views on demand via `REFRESH MATERIALIZED VIEW CONCURRENTLY ...`.
* Since the original dataset is stored via Git LFS, the actual data
  contents are not tracked in this repository. Make sure to run
  `git lfs pull` after cloning to retrieve the CSVs, or download them
  manually if you’re working outside of Git.
* The frontend currently contains placeholder components for the charts.
  To enable interactive graphs you will need to integrate a chart library
  such as Recharts, Victory, or ECharts. The scaffolding is ready for
  React and Tailwind; you only need to import the library and pass data
  from the API.

Happy exploring!