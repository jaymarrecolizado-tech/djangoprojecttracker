# Django Project Tracking Management System v2.0

> **A modern, scalable full-stack application for tracking government infrastructure projects across different regions with geospatial visualization, real-time updates, and comprehensive analytics.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-3178C6.svg)](https://www.typescriptlang.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Quick Start

Choose your setup method:

### Option 1: Docker Setup (Recommended for Development)

```bash
# 1. Clone the repository
git clone <repository-url>
cd djangoProject

# 2. Copy environment file
cp .env.example .env
# Edit .env with your settings

# 3. Start all services with Docker
docker-compose up -d

# 4. Run database migrations
docker-compose exec backend python manage.py migrate

# 5. Create superuser
docker-compose exec backend python manage.py createsuperuser

# 6. Seed reference data
docker-compose exec backend python manage.py seed_data

# 7. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1/
# Admin Panel: http://localhost:8000/admin/
```

### Option 2: WAMP Setup (Windows with WAMP Server)

```cmd
:: 1. Clone the repository
git clone <repository-url>
cd djangoProject

:: 2. Run the setup script
scripts\setup_windows.bat

:: 3. Follow the prompts to:
::    - Create database in WAMP MySQL
::    - Install Python dependencies
::    - Install Node.js dependencies
::    - Configure environment files
::    - Run migrations

:: 4. Start the application
scripts\start_windows.bat

:: 5. Access the application
:: Frontend: http://localhost:3000
:: Backend API: http://localhost:8000/api/v1/
:: Admin Panel: http://localhost:8000/admin/
```

📖 **For detailed WAMP setup instructions, see [SETUP_WAMP.md](SETUP_WAMP.md)**

---

## 📋 Features

### Core Features
- ✅ **Dashboard** - Statistics, charts, and recent projects at a glance
- 🗺️ **Interactive Map** - WebGL-based visualization with MapLibre GL JS
- 📋 **Project Management** - Full CRUD operations with advanced filtering
- 📁 **CSV Import/Export** - Bulk data operations with validation and progress tracking
- 📈 **Reports & Analytics** - Comprehensive reporting with multiple export formats
- 🔍 **Advanced Filtering** - Filter by location, status, type, date range
- 📍 **Geospatial Search** - Find projects within bounds or proximity
- 🔔 **Real-time Updates** - WebSocket-based live collaboration
- 👥 **User Management** - Role-based access control (RBAC)
- 📝 **Audit Logging** - Comprehensive operation tracking

### Technical Features
- ⚡ **Performance** - Sub-second API responses, optimized rendering
- 🔒 **Security** - Session-based auth, CSRF protection, RBAC
- 📱 **Responsive** - Mobile, tablet, and desktop support
- 🐳 **Docker Support** - Full containerization with Docker Compose
- 🪟 **Windows/WAMP Support** - Native Windows development environment
- 🔄 **Background Tasks** - Celery for CSV imports and exports
- 📊 **Caching** - Redis-based query and session caching
- 🎨 **Modern UI** - shadcn/ui components with Tailwind CSS
- 🧪 **Testing** - Comprehensive test coverage (pytest, Vitest, Playwright)
- 📚 **API Documentation** - Auto-generated OpenAPI/Swagger docs

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| [React](https://react.dev/) | 18.3+ | UI Framework |
| [TypeScript](https://www.typescriptlang.org/) | 5.3+ | Type Safety |
| [Vite](https://vitejs.dev/) | 5.4+ | Build Tool |
| [Tailwind CSS](https://tailwindcss.com/) | 3.4+ | Styling |
| [shadcn/ui](https://ui.shadcn.com/) | latest | UI Components |
| [React Router](https://reactrouter.com/) | 6.20+ | Routing |
| [Zustand](https://github.com/pmndrs/zustand) | 4.4+ | State Management |
| [TanStack Query](https://tanstack.com/query/latest) | 5.12+ | Server State |
| [React Hook Form](https://react-hook-form.com/) | 7.48+ | Forms |
| [Zod](https://zod.dev/) | 3.22+ | Validation |
| [MapLibre GL JS](https://maplibre.org/) | 4.1+ | Maps |
| [Recharts](https://recharts.org/) | 2.10+ | Charts |
| [Axios](https://axios-http.com/) | 1.6+ | HTTP Client |

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| [Python](https://www.python.org/) | 3.11+ | Runtime |
| [Django](https://www.djangoproject.com/) | 5.0+ | Web Framework |
| [Django REST Framework](https://www.django-rest-framework.org/) | 3.14+ | API Framework |
| [MySQL](https://www.mysql.com/) | 8.0+ | Database |
| [Django Channels](https://channels.readthedocs.io/) | 4.0+ | WebSockets |
| [Celery](https://docs.celeryq.dev/) | 5.3+ | Background Tasks |
| [Redis](https://redis.io/) | 7.2+ | Caching & Queues |
| [Pandas](https://pandas.pydata.org/) | 2.1+ | Data Processing |
| [GeoDjango](https://docs.djangoproject.com/en/stable/ref/contrib/gis/) | 5.0+ | Geospatial |
| [drf-spectacular](https://drf-spectacular.readthedocs.io/) | 0.27+ | API Docs |

---

## 📁 Project Structure

```
djangoProject/
├── README.md                    # This file
├── SETUP_WAMP.md               # Windows/WAMP setup guide
├── scripts/                    # Utility scripts
│   ├── setup_windows.bat       # Windows automated setup
│   ├── start_windows.bat       # Windows start script
│   └── setup_database.sql      # MySQL database setup
│
├── docs/                       # Complete documentation
│   ├── SPECIFICATION.md        # Functional/NFR requirements
│   ├── ARCHITECTURE.md         # System architecture
│   ├── DATABASE.md             # Django models and schema
│   ├── API.md                  # API documentation
│   ├── SETUP.md                # Docker setup guide
│   ├── TESTING.md              # Testing strategy
│   ├── SECURITY.md             # Security implementation
│   ├── DEPLOYMENT.md           # Production deployment
│   ├── BACKEND_GUIDE.md        # Django development guide
│   ├── FRONTEND_GUIDE.md       # React development guide
│   └── TROUBLESHOOTING.md      # Common issues
│
├── backend/                    # Django application
│   ├── apps/                   # Django apps (9 apps)
│   │   ├── accounts/           # User management & auth
│   │   ├── projects/           # Project CRUD operations
│   │   ├── locations/          # Location hierarchy (PH)
│   │   ├── geo/                # Geospatial services
│   │   ├── import_export/      # CSV import/export
│   │   ├── reports/            # Analytics & reports
│   │   ├── audit/              # Audit logging
│   │   ├── notifications/      # WebSocket notifications
│   │   └── common/             # Shared utilities
│   ├── config/                 # Settings, URLs, ASGI/WSGI
│   ├── media/                  # User uploads
│   ├── static/                 # Static files
│   ├── logs/                   # Application logs
│   ├── manage.py               # Django management
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── auth/           # Authentication components
│   │   │   ├── dashboard/      # Dashboard widgets
│   │   │   ├── layout/         # Layout components
│   │   │   ├── map/            # Map components
│   │   │   ├── projects/       # Project components
│   │   │   └── ui/             # shadcn/ui components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API layer
│   │   ├── stores/             # Zustand stores
│   │   ├── hooks/              # Custom hooks
│   │   ├── types/              # TypeScript types
│   │   └── lib/                # Utilities
│   ├── public/                 # Static assets
│   └── package.json            # NPM dependencies
│
└── docker/                     # Docker configurations
    ├── docker-compose.yml
    ├── Dockerfile.backend
    ├── Dockerfile.frontend
    └── nginx.conf
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SETUP_WAMP.md](SETUP_WAMP.md) | **Windows/WAMP setup guide** |
| [docs/SPECIFICATION.md](docs/SPECIFICATION.md) | Complete functional and non-functional requirements |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture with diagrams |
| [docs/DATABASE.md](docs/DATABASE.md) | Django models, migrations, indexes |
| [docs/API.md](docs/API.md) | Complete API reference with examples |
| [docs/SETUP.md](docs/SETUP.md) | Docker setup guide |
| [docs/TESTING.md](docs/TESTING.md) | Testing strategy and guidelines |
| [docs/SECURITY.md](docs/SECURITY.md) | Security implementation guide |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment guide |
| [docs/BACKEND_GUIDE.md](docs/BACKEND_GUIDE.md) | Django-specific development guide |
| [docs/FRONTEND_GUIDE.md](docs/FRONTEND_GUIDE.md) | React + TypeScript development guide |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, configuration, all CRUD operations |
| **Manager** | Read/write projects, view reports, manage users, import/export data |
| **Editor** | Read/write projects, import data, view projects and reports |
| **Viewer** | Read-only access to projects and reports |

### Default Login Credentials

After setup, you can login with:
- **Username**: `admin`
- **Password**: `admin123`

**Note**: Change the default password immediately after first login!

---

## 🎯 Key Goals

1. **Modern UI/UX** - Contemporary, responsive design with smooth animations
2. **Performance** - Sub-second API responses, optimized rendering
3. **Scalability** - Support for 10x growth in users and projects
4. **Developer Experience** - Type-safe, automated testing, modern tooling
5. **Cross-Platform** - Works on Docker (Linux/Mac) and WAMP (Windows)

---

## 🔄 Development Workflow

### Branching Strategy
```
main (production)
├── develop (integration)
│   ├── feature/auth
│   ├── feature/projects-api
│   ├── feature/map-integration
│   └── bugfix/csv-import
```

### Commit Conventions
- `feat: add user authentication`
- `fix: resolve CSV import timeout`
- `docs: update API documentation`
- `test: add project CRUD tests`
- `refactor: optimize map rendering`

---

## 🖥️ Development Setup

### Prerequisites

| Requirement | Docker | WAMP |
|-------------|--------|------|
| Docker Desktop | ✅ 4.0+ | ❌ |
| Python | ❌ | ✅ 3.11+ |
| Node.js | ❌ | ✅ 18+ |
| WAMP Server | ❌ | ✅ 3.3+ |
| MySQL | ✅ 8.0 (container) | ✅ 8.0 (WAMP) |
| Redis | ✅ (container) | Optional |

### Manual Setup (Without Scripts)

<details>
<summary>Click to expand manual setup instructions</summary>

#### 1. Clone Repository
```bash
git clone <repository-url>
cd djangoProject
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate.bat
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed data
python manage.py seed_data

# Start server
python manage.py runserver
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

#### 4. Access Application
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs/

</details>

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest

# With coverage
pytest --cov=apps --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 📊 System Statistics

- **Lines of Code**: ~30,000+
- **Test Coverage**: >80%
- **API Endpoints**: 50+
- **Django Apps**: 9
- **React Components**: 60+
- **Documentation Pages**: 150+
- **Database Tables**: 15+

---

## 🤝 Contributing

1. Create feature branch from `develop`
2. Implement feature with tests
3. Ensure test coverage >80%
4. Update documentation
5. Submit pull request to `develop`

### Development Guidelines

- Follow [PEP 8](https://pep8.org/) for Python code
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) for TypeScript
- Write tests for new features
- Update documentation for API changes

---

## 🔒 Security

- Session-based authentication with CSRF protection
- Role-based access control (RBAC)
- SQL injection prevention via Django ORM
- XSS protection via React's automatic escaping
- Input validation using Zod schemas
- Audit logging for all data modifications

---

## 🚀 Deployment

### Production Checklist

- [ ] Change default admin password
- [ ] Update `SECRET_KEY` to a cryptographically secure value
- [ ] Set `DEBUG=False` in production
- [ ] Configure production database credentials
- [ ] Set up SSL/TLS certificates
- [ ] Configure email backend for notifications
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - Web framework
- [React](https://react.dev/) - UI library
- [shadcn/ui](https://ui.shadcn.com/) - UI components
- [MapLibre](https://maplibre.org/) - Maps library
- [Philippine Standard Geographic Code](https://psa.gov.ph/classification/psgc/) - Location data

---

## 📞 Support

For issues and questions:
1. Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Search existing issues
3. Create a new issue with detailed description

---

**Built with ❤️ using Django + React + TypeScript**
