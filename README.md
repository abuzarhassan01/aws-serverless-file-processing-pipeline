
<img width="1024" height="396" alt="image" src="https://github.com/user-attachments/assets/35bf0499-55af-450b-a5e5-9a821b08046f" />

# 🚀 Event-Driven Serverless File Processing Pipeline on AWS

A robust, production-grade, event-driven data ingestion and processing pipeline built on AWS using **Amazon S3, AWS Lambda (Python), IAM Least Privilege Security, Amazon CloudWatch Observability, and Amazon SNS Alarming**.

---

## 🏗️ Architecture & Flow


1. **Ingestion:** Raw JSON (`test.json`) or multi-row CSV batch datasets (`raw_user_events_500.csv`) are uploaded into the S3 `input/` folder[cite: 6].
2. **Trigger:** S3 Event Notifications automatically push an event payload to invoke an **AWS Lambda** function.
3. **Processing & Normalization:** The Python Lambda function validates file types, cleans and sanitizes data fields, injects audit metadata, and persists the standardized output into the `processed/` folder.
4. **Observability & Alerting:** Execution logs and metrics feed into **Amazon CloudWatch**. A custom Metric Alarm monitors error rates (`Errors >= 1`) and instantly dispatches emergency email notifications via **Amazon SNS** upon unhandled failures.

---

## 🔒 Security & Least Privilege
* **IAM Policy Scoping:** Avoided broad wildcard permissions (`*`). The Lambda execution role is locked down using custom inline policies restricting access exclusively to:
  * `s3:GetObject` strictly on `input/*`
  * `s3:PutObject` strictly on `processed/*`
* **Blast Radius Minimization:** Ensures that even if compute credentials were compromised, operations are restricted solely to designated project folders, preventing unauthorized data mutation.

---

## 📊 Key Performance Metrics
* **Execution Latency:** ~452 ms average processing time for 500-record CSV batches.
* **Resource Footprint:** 98 MB peak memory utilization against a 128 MB allocated limit.
* **Cost Model:** 100% serverless, operating within the **AWS Free Tier** with zero idle compute costs.

---
