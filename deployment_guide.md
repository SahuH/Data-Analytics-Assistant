# Complete Deployment Guide

## 🚀 Deployment Architecture

Since Vercel is optimized for frontend/serverless applications and doesn't support persistent backend servers, we'll use a hybrid approach:

- **Frontend**: Deploy on Vercel (static hosting)
- **MCP Server**: Deploy on Railway/Render (persistent server)
- **Data**: Store in cloud storage or embed with server

## 📁 Project Structure

```
data-analytics-mcp/
├── server/
│   ├── main.py                 # ✅ Your MCP server
│   ├── requirements.txt        # ✅ Generated
│   ├── tools/                  # Your query tools
│   └── data/                   # CSV files from Kaggle
├── frontend/
│   ├── index.html             # ✅ Your HTML file
│   ├── app.js                 # ✅ Generated
│   └── styles.css             # ✅ Generated
├── docs/
│   └── API.md                 # ✅ Generated
├── deploy/
│   ├── Dockerfile             # ✅ Generated
│   ├── docker-compose.yml     # ✅ Generated
│   └── railway.toml           # 📝 Created below
├── vercel.json                # ✅ Generated
└── README.md
```

## 🔧 Step 1: Prepare Your Data

### Option A: Embed Data (Recommended for Demo)
```bash
# Download Kaggle dataset
mkdir -p server/data
# Place your CSV files in server/data/
```

### Option B: Cloud Storage (Production)
```python
# Add to your main.py
import boto3
from io import StringIO

def load_data_from_s3():
    s3 = boto3.client('s3')
    # Load CSV from S3
    pass
```

## 🚢 Step 2: Deploy MCP Server to Railway

### Create Railway Configuration

Create `deploy/railway.toml`:
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "python server/main.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
PORT = "8000"
HOST = "0.0.0.0"
DEBUG = "false"
```

### Deploy Steps:

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
railway login
```

2. **Initialize and Deploy**:
```bash
cd data-analytics-mcp
railway init
railway up
```

3. **Set Environment Variables**:
```bash
railway variables set API_KEY_SECRET=your-secret-key
railway variables set RATE_LIMIT_REQUESTS=100
railway variables set LOG_LEVEL=info
```

4. **Get Your Railway URL**:
```bash
railway status
# Note the URL: https://your-app.railway.app
```

## 🎯 Step 3: Deploy Frontend to Vercel

### Update Configuration

1. **Update `frontend/app.js`**:
```javascript
// Replace the serverUrl in MCPClient constructor
this.serverUrl = process.env.NODE_ENV === 'production' 
    ? 'https://your-app.railway.app'  // Your Railway URL
    : 'http://localhost:8000';
```

2. **Update `vercel.json`**:
```json
{
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-app.railway.app/$1"
    }
  ]
}
```

### Deploy to Vercel:

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Deploy**:
```bash
cd data-analytics-mcp
vercel --prod
```

3. **Configure Domain** (Optional):
```bash
vercel domains add your-domain.com
```

## 🐳 Alternative: Docker Deployment

### For Single Server Deployment:

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:80
# API: http://localhost:8000
# Grafana: http://localhost:3000
```

## ☁️ Alternative Cloud Platforms

### Deploy to Render:

1. **Create `render.yaml`**:
```yaml
services:
  - type: web
    name: analytics-mcp-server
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python server/main.py
    envVars:
      - key: PORT
        value: 8000
```

2. **Deploy**:
```bash
# Connect your GitHub repo to Render
# Auto-deploys on push
```

### Deploy to Google Cloud Run:

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/analytics-mcp
gcloud run deploy --image gcr.io/PROJECT_ID/analytics-mcp --platform managed
```

## 🔐 Step 4: Environment Variables

### Railway Environment Variables:
```bash
PORT=8000
HOST=0.0.0.0
DEBUG=false
API_KEY_SECRET=your-secret-key-here
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
DATA_PATH=/app/server/data
CACHE_TTL=3600
LOG_LEVEL=info
```

### Vercel Environment Variables:
```bash
NODE_ENV=production
MCP_SERVER_URL=https://your-app.railway.app
```

## 📊 Step 5: Data Hosting Options

### Option 1: Embed with Server (Simple)
```bash
# Place CSV files in server/data/
server/data/
├── sales_data.csv
├── customer_data.csv
├── products.csv
└── regions.csv
```

### Option 2: AWS S3 (Recommended)
```python
# Add to requirements.txt
boto3>=1.34.0

# In your server code
import boto3
import pandas as pd
from io import StringIO

class DataLoader:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket = 'your-analytics-data'
    
    def load_csv(self, key):
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        return pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))
```

### Option 3: Google Cloud Storage
```python
from google.cloud import storage
import pandas as pd

def load_from_gcs(bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return pd.read_csv(blob.open())
```

## 🔍 Step 6: Testing Your Deployment

### Test Railway Server:
```bash
curl https://your-app.railway.app/health
curl -X POST https://your-app.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are our top 5 products?"}'
```

### Test Vercel Frontend:
1. Visit your Vercel URL
2. Try example queries
3. Check browser console for errors

## 📈 Step 7: Monitoring and Maintenance

### Railway Monitoring:
```bash
# View logs
railway logs

# Monitor metrics
railway status
```

### Set up Alerts:
```bash
# Railway automatically monitors:
# - Memory usage
# - CPU usage
# - Response times
# - Error rates
```

## 🚨 Troubleshooting

### Common Issues:

1. **CORS Errors**:
```python
# Add to your FastAPI server
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Railway Build Failures**:
```bash
# Check Python version in Dockerfile
FROM python:3.11-slim

# Verify requirements.txt
pip install -r requirements.txt --dry-run
```

3. **Data Loading Issues**:
```python
# Add error handling
try:
    df = pd.read_csv('data/sales.csv')
except FileNotFoundError:
    print("Data file not found")
```

## 🔄 CI/CD Pipeline

### GitHub Actions for Auto-Deploy:

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-railway:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: railway/cli@v2
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}
      - run: railway up

  deploy-vercel:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## 💰 Cost Estimation

### Railway (MCP Server):
- **Hobby Plan**: $5/month (512MB RAM, 1GB storage)
- **Pro Plan**: $20/month (8GB RAM, 100GB storage)

### Vercel (Frontend):
- **Hobby Plan**: Free (100GB bandwidth)
- **Pro Plan**: $20/month (1TB bandwidth)

### Total Monthly Cost: $5-40 depending on usage

## 🎉 Final Checklist

- [ ] Railway server deployed and healthy
- [ ] Vercel frontend deployed and accessible
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] Data loading working
- [ ] Sample