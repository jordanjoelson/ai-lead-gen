# Lovable Lead Gen 🚀

A powerful lead generation API that scrapes Google Maps for business information and enriches it with email addresses using Hunter.io.

## Features

- **Google Maps Scraping**: Extract business information from Google Maps
- **Email Enrichment**: Find email addresses using Hunter.io API
- **Multiple Export Formats**: Export to CSV, JSON, and Google Sheets
- **Fast & Scalable**: Built with FastAPI and async operations
- **Data Validation**: Built-in data quality checks
- **Rate Limiting**: Respectful scraping with proper delays

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd lovable-leadgen

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Run the API

```bash
# Start the server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### Core Endpoints

#### 1. Scrape Leads

```http
POST /scrape
```

**Request Body:**

```json
{
  "query": "restaurants",
  "location": "New York, NY",
  "max_results": 50
}
```

**Response:**

```json
{
  "scrape_id": "abc123",
  "leads": [...],
  "total_found": 50,
  "status": "success"
}
```

#### 2. Enrich with Emails

```http
POST /enrich
```

**Request Body:**

```json
{
  "scrape_id": "abc123",
  "hunter_api_key": "your-hunter-api-key"
}
```

#### 3. Export Data

```http
POST /export
```

**Request Body:**

```json
{
  "scrape_id": "abc123",
  "format": "csv",
  "filename": "my_leads.csv"
}
```

### Utility Endpoints

- `GET /leads/{scrape_id}` - Get stored leads
- `DELETE /leads/{scrape_id}` - Delete stored leads
- `GET /health` - Health check

## Usage Examples

### Python Client Example

```python
import requests
import json

# Base URL
base_url = "http://localhost:8000"

# 1. Scrape leads
scrape_data = {
    "query": "dentists",
    "location": "Los Angeles, CA",
    "max_results": 30
}

response = requests.post(f"{base_url}/scrape", json=scrape_data)
scrape_result = response.json()
scrape_id = scrape_result["scrape_id"]

print(f"Scraped {scrape_result['total_found']} leads")

# 2. Enrich with emails
enrich_data = {
    "scrape_id": scrape_id,
    "hunter_api_key": "your-hunter-api-key"
}

response = requests.post(f"{base_url}/enrich", json=enrich_data)
enrich_result = response.json()

print(f"Enriched {enrich_result['enrichment_count']} leads with emails")

# 3. Export to CSV
export_data = {
    "scrape_id": scrape_id,
    "format": "csv",
    "filename": "dentists_la.csv"
}

response = requests.post(f"{base_url}/export", json=export_data)
export_result = response.json()

print(f"Exported to: {export_result['file_path']}")
```

### cURL Examples

```bash
# Scrape leads
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"query": "pizza", "location": "Chicago, IL", "max_results": 20}'

# Enrich leads
curl -X POST "http://localhost:8000/enrich" \
  -H "Content-Type: application/json" \
  -d '{"scrape_id": "your-scrape-id", "hunter_api_key": "your-api-key"}'

# Export to CSV
curl -X POST "http://localhost:8000/export" \
  -H "Content-Type: application/json" \
  -d '{"scrape_id": "your-scrape-id", "format": "csv", "filename": "leads.csv"}'
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Optional: Set default Hunter.io API key
HUNTER_API_KEY=your-hunter-api-key

# Optional: Set export directory
EXPORT_DIR=exports

# Optional: Set log level
LOG_LEVEL=INFO
```

### Hunter.io Setup

1. Sign up for a free account at [Hunter.io](https://hunter.io)
2. Get your API key from the dashboard
3. Use the API key in enrichment requests

## Data Models

### Lead Object

```json
{
  "name": "Business Name",
  "address": "123 Main St, City, State",
  "phone": "+1-555-123-4567",
  "email": "contact@business.com",
  "website": "https://business.com",
  "category": "Restaurant",
  "rating": 4.5,
  "reviews_count": 120,
  "google_maps_url": "https://maps.google.com/...",
  "place_id": "ChIJ...",
  "coordinates": { "lat": 40.7128, "lng": -74.006 }
}
```

## Advanced Features

### Data Quality Validation

The system includes built-in data validation:

- Email format validation
- Phone number format checks
- Website URL validation
- Missing data detection

### Export Formats

1. **CSV**: Standard comma-separated values
2. **JSON**: Structured JSON format
3. **Google Sheets**: CSV format for easy import

### Rate Limiting

The scraper includes respectful rate limiting:

- 0.5-1 second delays between requests
- Hunter.io API rate limit compliance
- Configurable delays

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright
RUN playwright install chromium

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Database Integration

For production, replace the in-memory storage with a database:

```python
# Add to requirements.txt
# sqlalchemy
# psycopg2-binary  # for PostgreSQL
# alembic  # for migrations

# Example database model
from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LeadModel(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    # ... other fields
```

## Monitoring & Logging

The system includes comprehensive logging:

```python
# View logs
tail -f logs/leadgen.log

# Log levels: DEBUG, INFO, WARNING, ERROR
```

## Troubleshooting

### Common Issues

1. **Playwright Browser Not Found**

   ```bash
   playwright install chromium
   ```

2. **Rate Limiting Errors**

   - Increase delays in scraper
   - Check Hunter.io API limits

3. **Memory Issues**

   - Implement database storage
   - Add pagination for large datasets

4. **Scraping Blocked**
   - Rotate user agents
   - Use residential proxies
   - Implement CAPTCHA solving

### Debug Mode

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the troubleshooting section

## Roadmap

- [ ] Database integration
- [ ] User authentication
- [ ] Webhook support
- [ ] More export formats (Excel, PDF)
- [ ] Advanced filtering options
- [ ] Bulk operations
- [ ] Real-time progress tracking
- [ ] Integration with CRM systems

---

**Note**: This tool is for legitimate business use only. Always respect robots.txt and terms of service when scraping websites.
