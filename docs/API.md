# Data & Analytics Intelligence Agent API

## Overview

The Data & Analytics Intelligence Agent provides a natural language interface to query company sales data. Built using the Model Context Protocol (MCP), it enables employees to ask business questions in plain English and receive instant insights without SQL knowledge.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-mcp-server.railway.app`

## Authentication

Currently, no authentication is required. In production, implement API key authentication:

```javascript
headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}
```

## Endpoints

### Health Check

Check if the MCP server is running and accessible.

```http
GET /health
```

**Response:**
```json
{
    "error": "Error message describing what went wrong",
    "error_code": "QUERY_PARSING_ERROR",
    "details": {
        "query": "Original query that caused the error",
        "suggestions": [
            "Try rephrasing your question",
            "Check if the requested data exists",
            "Use more specific terms"
        ]
    },
    "timestamp": "2025-06-29T10:30:00Z"
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `QUERY_PARSING_ERROR` | Unable to understand the natural language query | Rephrase the question more clearly |
| `DATA_NOT_FOUND` | Requested data doesn't exist in the database | Check available data sources |
| `TIMEOUT_ERROR` | Query execution took too long | Simplify the query or add filters |
| `PERMISSION_DENIED` | User doesn't have access to requested data | Contact administrator |
| `SERVER_ERROR` | Internal server error | Try again later or contact support |

## Rate Limiting

- **Development**: No rate limiting
- **Production**: 100 requests per minute per IP
- **Enterprise**: 1000 requests per minute per API key

Rate limit headers included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1719662400
```

## Data Sources

The system connects to the following data sources:

### Sales Data (`sales_data.csv`)
- **Records**: ~10,000 sales transactions
- **Time Range**: 2022-2025
- **Columns**: Order details, product info, customer data, financial metrics
- **Update Frequency**: Daily

### Customer Data (`customer_data.csv`)
- **Records**: ~2,500 unique customers
- **Columns**: Customer demographics, company info, purchase history
- **Update Frequency**: Weekly

### Product Catalog (`products.csv`)
- **Records**: ~500 products
- **Columns**: Product details, categories, pricing, margins
- **Update Frequency**: As needed

## Natural Language Processing

### Supported Query Types

1. **Aggregation Queries**
   - "What's the total/average/maximum..."
   - "How many customers/orders/products..."
   - "Sum of sales by region/category/time"

2. **Comparison Queries**
   - "Compare sales this year vs last year"
   - "Which region performs better"
   - "Top 10 products by revenue"

3. **Trend Analysis**
   - "Show monthly trends"
   - "Growth rate over time"
   - "Seasonal patterns"

4. **Filtering Queries**
   - "Sales in the Pacific Northwest"
   - "Customers who bought in Q4"
   - "Products with margin > 20%"

### Query Processing Flow

1. **Natural Language Understanding**: Parse user intent and entities
2. **Query Planning**: Determine required data sources and operations
3. **SQL Generation**: Convert to optimized SQL queries
4. **Data Retrieval**: Execute queries against data sources
5. **Result Processing**: Format and summarize results
6. **Response Generation**: Create human-readable insights

## WebSocket Support (Future Feature)

For real-time analytics and streaming data:

```javascript
const ws = new WebSocket('wss://your-mcp-server.railway.app/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // Handle real-time analytics updates
};

// Subscribe to metrics
ws.send(JSON.stringify({
    type: 'subscribe',
    metrics: ['revenue', 'orders', 'customer_count']
}));
```

## SDK and Client Libraries

### JavaScript/Node.js

```javascript
npm install @company/analytics-mcp-client

import { AnalyticsClient } from '@company/analytics-mcp-client';

const client = new AnalyticsClient({
    baseUrl: 'https://your-mcp-server.railway.app',
    apiKey: 'your-api-key'
});

const result = await client.query("What's our revenue this month?");
```

### Python

```python
pip install analytics-mcp-client

from analytics_mcp import AnalyticsClient

client = AnalyticsClient(
    base_url="https://your-mcp-server.railway.app",
    api_key="your-api-key"
)

result = client.query("Show me top customers by revenue")
```

## Deployment Configuration

### Environment Variables

```bash
# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379

# API Configuration
API_KEY_SECRET=your-secret-key
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Data Sources
DATA_PATH=/app/data
CACHE_TTL=3600

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
```

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

## Performance Optimization

### Caching Strategy

- **Query Results**: Cache for 5 minutes
- **Schema Information**: Cache for 1 hour
- **Aggregated Metrics**: Cache for 15 minutes

### Query Optimization

- Automatic index suggestions
- Query plan analysis
- Result set limiting
- Parallel execution for complex queries

## Security Considerations

### Data Privacy

- No PII logging
- Query sanitization
- SQL injection prevention
- Result data masking for sensitive fields

### Access Control

- Role-based permissions
- Query complexity limits
- Resource usage monitoring
- Audit logging

## Monitoring and Analytics

### Metrics Tracked

- Query response times
- Error rates
- Popular queries
- Data source performance
- User engagement

### Health Monitoring

```http
GET /metrics
```

Returns Prometheus-compatible metrics:

```
# HELP query_duration_seconds Time spent executing queries
# TYPE query_duration_seconds histogram
query_duration_seconds_bucket{le="0.1"} 145
query_duration_seconds_bucket{le="0.5"} 234
query_duration_seconds_count 500
query_duration_seconds_sum 67.3
```

## Development and Testing

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/company/data-analytics-mcp
cd data-analytics-mcp

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env

# Run server
python server/main.py

# Run tests
pytest tests/
```

### API Testing

Use the included Postman collection or curl examples:

```bash
# Health check
curl http://localhost:8000/health

# Query execution
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are our top 5 products by revenue?"}'
```

## Support and Contributing

### Getting Help

- **Documentation**: [docs.company.com/analytics-mcp](https://docs.company.com/analytics-mcp)
- **Issues**: [GitHub Issues](https://github.com/company/data-analytics-mcp/issues)
- **Support**: support@company.com

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Changelog

#### v1.0.0 (2025-06-29)
- Initial release
- Natural language query processing
- Sales and customer analytics
- REST API implementation
- Web frontend interface
{
    "status": "healthy",
    "timestamp": "2025-06-29T10:30:00Z",
    "version": "1.0.0"
}
```

### Query Execution

Execute natural language queries against the sales database.

```http
POST /query
```

**Request Body:**
```json
{
    "query": "What's our total sales revenue this year?",
    "context": {
        "user_id": "optional",
        "department": "optional"
    }
}
```

**Response:**
```json
{
    "response": "Based on the sales data, your total revenue this year is $2,547,832.45 across all products and regions.",
    "data": [
        {
            "metric": "Total Revenue",
            "value": 2547832.45,
            "currency": "USD",
            "period": "2025 YTD"
        }
    ],
    "sql_query": "SELECT SUM(revenue) as total_revenue FROM sales WHERE YEAR(date) = 2025",
    "execution_time": 0.234,
    "data_points": 1
}
```

### Schema Information

Get information about available tables and columns.

```http
GET /schema
```

**Response:**
```json
{
    "tables": {
        "sales_data": [
            "order_id",
            "product_name",
            "category",
            "sales_rep",
            "customer_name",
            "region",
            "order_date",
            "quantity",
            "unit_price",
            "total_amount",
            "profit_margin"
        ],
        "customer_data": [
            "customer_id",
            "customer_name",
            "company",
            "industry",
            "region",
            "registration_date",
            "last_purchase_date",
            "total_orders",
            "lifetime_value"
        ]
    },
    "relationships": [
        {
            "from": "sales_data.customer_name",
            "to": "customer_data.customer_name",
            "type": "many_to_one"
        }
    ]
}
```

### Available Tools

Get list of available MCP tools and their capabilities.

```http
GET /tools
```

**Response:**
```json
{
    "tools": [
        {
            "name": "sales_analytics",
            "description": "Analyze sales performance, revenue trends, and product metrics",
            "parameters": ["time_period", "region", "product_category"]
        },
        {
            "name": "customer_analytics",
            "description": "Customer segmentation, churn analysis, and lifetime value calculations",
            "parameters": ["segment", "time_period", "metric"]
        },
        {
            "name": "financial_metrics",
            "description": "Calculate financial KPIs, profit margins, and ROI metrics",
            "parameters": ["metric_type", "comparison_period"]
        }
    ]
}
```

## Query Examples

### Sales Performance Queries

```javascript
// Revenue analysis
{
    "query": "What's our total sales revenue this year compared to last year?"
}

// Product performance
{
    "query": "Which products have the highest profit margins?"
}

// Regional analysis
{
    "query": "Show me sales performance by region for Q4"
}
```

### Customer Analytics Queries

```javascript
// Customer segmentation
{
    "query": "Who are our top 10 customers by lifetime value?"
}

// Churn analysis
{
    "query": "What's our customer churn rate this quarter?"
}

// Geographic analysis
{
    "query": "Which regions have the highest customer acquisition rates?"
}
```

### Time-based Analysis

```javascript
// Trend analysis
{
    "query": "Show me monthly sales trends for the past 6 months"
}

// Seasonal patterns
{
    "query": "How do our sales compare between Q1 and Q4 historically?"
}

// Growth metrics
{
    "query": "What's our month-over-month growth rate?"
}
```

## Response Format

All successful responses follow this structure:

```json
{
    "response": "Human-readable answer to the query",
    "data": [
        // Array of data objects relevant to the query
    ],
    "sql_query": "Generated SQL query (optional)",
    "metadata": {
        "execution_time": 0.234,
        "data_points": 150,
        "query_complexity": "medium",
        "confidence_score": 0.95
    },
    "suggestions": [
        // Array of follow-up questions
    ]
}
```

## Error Handling

### Error Response Format

```json