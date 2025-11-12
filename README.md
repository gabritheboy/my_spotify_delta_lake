# 🎧 Spotify Delta Lake — Event-Driven Lakehouse (Databricks + AWS)

> A personal data engineering project simulating an **event-driven Delta Lakehouse architecture** built with **Databricks**, **AWS**, and the **Spotify Web API**.  
> Every time new Spotify data lands in the S3 bucket, a **Lambda function triggers** a Databricks **pipeline** that flattens, cleans, and enriches the data up to the **Silver Layer**.  
> The next step will be building a **Gold Layer** and an interactive **Streamlit dashboard** for personal music insights.

---

## 🚀 Project Goals

- Simulate a **real-world, event-driven architecture** using serverless components.
- Implement **incremental & idempotent pipelines** using Delta Lake **MERGE** operations.
- Build a **dimensional model** from unique Spotify IDs (artists, albums, tracks).
- Lay the foundation for a **Gold Layer** and **Streamlit** analytics app.

---

## 🧩 Architecture Overview

```mermaid
%% Compact horizontal flowchart
flowchart LR
  A[Spotify API] -->|Pull recently played| B[Lambda: get_user_recent_played_spotify_data]
  B -->|Write JSON| C[(S3: my-raw-spotify-data/user_recent_played/)]
  C -->|New file detected| D[Lambda: Databricks Trigger]
  D -->|Call Jobs API| E[Databricks Bronze→Silver Pipeline]
  E -->|Merge by timestamp| F[Silver.user_recent_played]
  F -->|Extract unique IDs| G[Parallel Tasks: Artists • Albums • Tracks]
  G -->|Fetch new metadata| H[(Bronze Dimensional Tables)]
  H -->|Autoloader| I[Silver Dimensional Tables]
  I --> J[(Future: Gold Layer + Streamlit Dashboard)]

