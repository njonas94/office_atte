# Employee Attendance Dashboard

A comprehensive web application for monitoring and analyzing employee attendance compliance based on Oracle database records.

## Features

- **Dashboard Overview**: Real-time statistics and compliance metrics
- **Monthly Reports**: Detailed compliance reports with Excel export
- **Employee Details**: Individual employee analysis with weekly patterns
- **Data Quality Monitoring**: Detection and alerting of attendance record issues
- **Flexible Rules Engine**: Supports 6-day monthly attendance with flexible weekly distribution
- **Data Caching**: Redis-based caching for optimal performance
- **Automated Refresh**: Scheduled data updates twice daily

## Architecture

- **Backend**: FastAPI (Python) with Oracle database connectivity
- **Frontend**: React with modern UI components and charts
- **Database**: Oracle 11.2 with read-only access
- **Caching**: Redis for performance optimization
- **Containerization**: Docker and Docker Compose

## Business Rules

### Attendance Requirements
- **Monthly Minimum**: 6 days per month
- **Weekly Distribution**: Flexible but constrained:
  - Valid: 2 weeks of 2 days + 2 weeks of 1 day (or variations)
  - Invalid: Any week with more than 2 days
- **Daily Hours**: Minimum 9 hours per day (including lunch breaks)
- **Compliance Evaluation**: Days and hours evaluated separately

### Data Quality Monitoring
- Detects missing entry/exit records
- Identifies multiple entries per day
- Alerts users to data inconsistencies
- Provides detailed issue tracking

## Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Oracle database access
- TNS configuration (if applicable)

### Quick Start

1. **Clone and Configure**
   ```bash
   git clone <repository>
   cd employee-attendance-dashboard
   cp .env.example .env
   # Edit .env with your Oracle database credentials
   ```

2. **Oracle Configuration**
   - Place your `tnsnames.ora` file in the project root
   - Update environment variables in `.env`

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Access Application**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Environment Variables

```bash
# Oracle Database
ORACLE_HOST=your_oracle_host
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=your_service_name
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
ORACLE_TNS=your_tns_alias

# Application
REDIS_HOST=redis
REDIS_PORT=6379
```

## Database Schema

### Required Tables

#### CRONOS.FICHADA_PROCESO
- `ID_PERSONA` (INT): Employee ID
- `FECHA_FICHADA` (TIMESTAMP): Check-in/out timestamp
- `PRIORIDAD` (INT): Priority field (optional)
- `IGNORAR` (INT): Flag to ignore records (0/NULL = include)

#### CRONOS.EMPLEADOS (Employee table)
- `ID_PERSONA` (INT): Employee ID (Primary Key)
- `NOMBRE` (VARCHAR): First Name
- `APELLIDO` (VARCHAR): Last Name
- `DEPARTAMENTO` (VARCHAR): Department
- `EMAIL` (VARCHAR): Email Address

## API Endpoints

### Dashboard
- `GET /api/dashboard-stats` - Overall dashboard statistics
- `GET /api/employees` - List all employees

### Reports
- `GET /api/monthly-compliance/{year}/{month}` - Monthly compliance report
- `GET /api/export/monthly-report/{year}/{month}` - Export Excel report

### Employee Analysis
- `GET /api/employee-stats/{id}/{year}/{month}` - Individual employee stats
- `GET /api/weekly-patterns/{id}/{year}/{month}` - Weekly attendance patterns
- `GET /api/trends/{id}` - Employee attendance trends

### Data Quality
- `GET /api/data-quality-issues` - Data quality issues
- `GET /api/department-stats/{year}/{month}` - Department statistics

## Usage Guide

### Dashboard Overview
- Monitor real-time compliance metrics
- View compliance distribution charts
- Track data quality issues
- Access quick statistics

### Monthly Reports
- Select month/year for analysis
- View detailed employee compliance
- Export comprehensive Excel reports
- Filter by compliance status

### Employee Details
- Select individual employees
- Analyze weekly attendance patterns
- View daily entry/exit times
- Track compliance trends

### Data Quality Monitoring
- Automatic issue detection
- Missing entry/exit alerts
- Invalid record identification
- Detailed issue descriptions

## Development

### Project Structure
```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection & queries
│   ├── models.py            # Pydantic data models
│   ├── attendance_analyzer.py # Business logic
│   ├── report_generator.py  # Report generation
│   ├── scheduler.py         # Data refresh scheduler
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   └── components/      # React components
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

### Adding New Features

1. **Backend**: Add endpoints in `main.py`, logic in `attendance_analyzer.py`
2. **Frontend**: Create React components, add routes
3. **Database**: Extend queries in `database.py`

### Testing
- Backend: `pytest` tests for business logic
- Frontend: `npm test` for React components
- Integration: Test API endpoints with sample data

## Troubleshooting

### Common Issues

1. **Oracle Connection Errors**
   - Verify TNS configuration
   - Check network connectivity
   - Validate credentials

2. **Data Quality Issues**
   - Review attendance record completeness
   - Check for system clock synchronization
   - Validate entry/exit pairing logic

3. **Performance Issues**
   - Monitor Redis cache hit rates
   - Review database query performance
   - Consider data archiving for old records

### Monitoring
- Check container logs: `docker-compose logs [service]`
- Monitor Redis cache: Connect to Redis CLI
- Database performance: Review slow query logs

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Create Pull Request

## License

[Your License Here]

## Support

For technical support or feature requests:
- Create GitHub issues for bugs/features
- Contact system administrator for database access
- Review logs for troubleshooting