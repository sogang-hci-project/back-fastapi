### Server Repository for Deployment

#### Get Started

```bash
  uvicorn src.main:app --host 0.0.0.0 --port 13502 --reload --ssl-keyfile key.pem --ssl-certfile cert.pem

```