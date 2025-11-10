# Neulbom - Seoul After-School Education Platform

서울시 늘봄 방과후 교육 프로그램 관리 플랫폼

## Project Overview

This platform manages Seoul's Neulbom after-school education program across 13 universities serving approximately 2,000 elementary students.

### Key Features

- Bulk student registration and ZEP space creation
- Instructor management and class organization
- Real-time administrator dashboard
- Automated permission configuration
- Public student portfolio showcasing

## Technology Stack

- **Backend**: Django 4.2 LTS
- **Database**: MySQL 8.0
- **Frontend**: Django Templates + Tailwind CSS
- **Deployment**: DigitalOcean + Nginx + uWSGI
- **Python**: 3.8.x

## Quick Start with Docker

### Prerequisites

- Docker
- Docker Compose

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd neulbom
```

2. Copy the environment file and configure:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the services:
```bash
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

5. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

6. Access the application:
- Application: http://localhost:8000
- Admin: http://localhost:8000/admin

### Common Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f web

# Run Django commands
docker-compose exec web python manage.py <command>

# Run migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Run tests
docker-compose exec web python manage.py test
```

## Local Development (Without Docker)

### Prerequisites

- Python 3.8.x
- MySQL 8.0
- Node.js 18+ (for Tailwind CSS)

### Setup

1. Create virtual environment:
```bash
python3.8 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

4. Create MySQL database:
```bash
mysql -u root -p
CREATE DATABASE neulbom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'neulbom_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON neulbom.* TO 'neulbom_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Project Structure

```
neulbom/
├── authentication/     # User authentication app
├── instructors/        # Instructor management app
├── students/           # Student management app
├── spaces/             # ZEP space integration app
├── neulbom/            # Project settings
├── static/             # Static files
├── templates/          # Django templates
├── logs/               # Application logs
├── docker/             # Docker configuration
├── docs/               # Project documentation
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

## Testing

Run tests:
```bash
# With Docker
docker-compose exec web python manage.py test

# Without Docker
python manage.py test
```

## Deployment

For production deployment instructions, see [docs/deployment.md](docs/deployment.md).

## License

Proprietary - Seoul Education Board

## Support

For issues and questions, contact the development team.
