# Setup Guide for Windows with WAMP

This guide provides step-by-step instructions for setting up the Project Tracking Management System (PTMS) on Windows using WAMP Server with MySQL.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Step-by-Step Setup](#step-by-step-setup)
- [Database Configuration](#database-configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [First Login](#first-login)

---

## 🔧 Prerequisites

### Required Software

Before starting, ensure you have the following installed:

| Software | Version | Download Link | Notes |
|----------|---------|---------------|-------|
| **WAMP Server** | 3.3+ | [wampserver.com](https://www.wampserver.com/) | Includes Apache, MySQL, PHP |
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) | Check "Add Python to PATH" during install |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) | LTS version recommended |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) | For cloning repository |

### System Requirements

- **OS**: Windows 10 or Windows 11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB free space
- **Ports**: 3000 (frontend), 8000 (backend), 3306 (MySQL)

### WAMP Installation Notes

1. Download WAMP from the official website
2. Choose the version with MySQL 8.0+ (not MariaDB if possible)
3. Install to `C:\wamp64` (default location)
4. During installation, you may need to install Visual C++ Redistributables

---

## 🚀 Step-by-Step Setup

### Step 1: Start WAMP Server

1. Launch WAMP Server from your desktop or Start Menu
2. Wait for the WAMP icon in the system tray to turn **GREEN**
   - 🔴 Red = Not running
   - 🟠 Orange = Some services running
   - 🟢 Green = All services running (Apache + MySQL)
3. If it stays orange, check that ports 80 and 3306 are not in use by other applications

### Step 2: Create the Database

#### Option A: Using phpMyAdmin (Recommended for beginners)

1. Open your browser and go to: `http://localhost/phpmyadmin`
2. Click on **"New"** in the left sidebar
3. Enter database name: `project_tracking`
4. Select **"utf8mb4_unicode_ci"** from the collation dropdown
5. Click **"Create"**

#### Option B: Using MySQL CLI

1. Open Command Prompt as Administrator
2. Navigate to WAMP's MySQL bin directory:
   ```cmd
   cd C:\wamp64\bin\mysql\mysql8.x.x\bin
   ```
3. Login to MySQL:
   ```cmd
   mysql -u root -p
   ```
   (Enter your MySQL root password when prompted, default is blank)

4. Run the setup script:
   ```sql
   source C:/wamp64/www/Projects/djangoProject/scripts/setup_database.sql
   ```

#### Option C: Using the Setup Script

1. Open Command Prompt
2. Navigate to your project directory:
   ```cmd
   cd C:\wamp64\www\Projects\djangoProject
   ```
3. Run the automated setup:
   ```cmd
   scripts\setup_windows.bat
   ```
   When prompted about database creation, type `Y` and press Enter

### Step 3: Configure Python Environment

1. Verify Python installation:
   ```cmd
   python --version
   ```
   Should output: `Python 3.11.x` or higher

2. Create a virtual environment:
   ```cmd
   cd C:\wamp64\www\Projects\djangoProject\backend
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```cmd
   venv\Scripts\activate.bat
   ```
   You should see `(venv)` at the beginning of your command prompt

4. Install Python dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
   This may take 5-10 minutes depending on your internet connection

### Step 4: Configure Environment Variables

1. Copy the example environment file:
   ```cmd
   cd C:\wamp64\www\Projects\djangoProject\backend
   copy .env.example .env
   ```

2. Open `.env` in a text editor (Notepad++, VS Code, etc.)

3. Update the database settings:
   ```env
   DB_NAME=project_tracking
   DB_USER=ptms_user
   DB_PASSWORD=ptms_password
   DB_HOST=localhost
   DB_PORT=3306
   ```
   
   If you didn't create the `ptms_user`, use:
   ```env
   DB_USER=root
   DB_PASSWORD=your_mysql_root_password
   ```

4. Generate a new SECRET_KEY (optional but recommended):
   ```cmd
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
   Copy the output and replace `SECRET_KEY` in `.env`

### Step 5: Configure Frontend Environment

1. Navigate to the frontend directory:
   ```cmd
   cd C:\wamp64\www\Projects\djangoProject\frontend
   ```

2. Copy the example environment file:
   ```cmd
   copy .env.example .env
   ```

3. The default settings should work, but verify:
   ```env
   VITE_API_URL=http://localhost:8000/api/v1/
   VITE_WS_URL=ws://localhost:8000/ws/
   ```

4. Install frontend dependencies:
   ```cmd
   npm install
   ```
   This may take 5-10 minutes

### Step 6: Run Database Migrations

1. Make sure your virtual environment is activated (you see `(venv)`)

2. Navigate to the backend directory:
   ```cmd
   cd C:\wamp64\www\Projects\djangoProject\backend
   ```

3. Run migrations:
   ```cmd
   python manage.py migrate
   ```

   You should see output like:
   ```
   Operations to perform:
     Apply all migrations: accounts, admin, auth, contenttypes, ...
   Running migrations:
     Applying accounts.0001_initial... OK
     Applying projects.0001_initial... OK
     ...
   ```

### Step 7: Create Admin User

Create a superuser account for accessing the admin panel:

```cmd
python manage.py createsuperuser
```

When prompted:
- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123`
- Confirm password: `admin123`

### Step 8: Seed Reference Data

Populate the database with initial data (provinces, municipalities, project types):

```cmd
python manage.py seed_data
```

This will create:
- Philippine provinces
- Municipalities and barangays (sample data)
- Project types
- Sample projects

---

## 🗄️ Database Configuration

### MySQL Connection Settings

The standard Django MySQL settings for WAMP:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'project_tracking',
        'USER': 'ptms_user',
        'PASSWORD': 'ptms_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### Troubleshooting Connection Issues

| Error | Solution |
|-------|----------|
| `Access denied for user` | Check username/password in `.env`. If using root, ensure password is correct |
| `Unknown database` | Create database in phpMyAdmin or run `setup_database.sql` |
| `Can't connect to MySQL` | Ensure WAMP MySQL service is running (green icon) |
| `2003, Can't connect to MySQL server` | MySQL service not started. Check WAMP tray icon |
| `django.db.utils.OperationalError` | Database credentials incorrect or MySQL not running |

### Managing MySQL via WAMP

1. **Restart MySQL**:
   - Left-click WAMP icon → MySQL → Service → Restart Service

2. **MySQL Console**:
   - Left-click WAMP icon → MySQL → MySQL Console

3. **phpMyAdmin**:
   - Left-click WAMP icon → phpMyAdmin

---

## ▶️ Running the Application

### Quick Start (Using Batch Script)

The easiest way to start both servers:

```cmd
cd C:\wamp64\www\Projects\djangoProject
scripts\start_windows.bat
```

This will:
- Start Django backend server on port 8000
- Start Vite frontend server on port 3000
- Open two separate command windows

### Manual Start (Separate Terminals)

#### Terminal 1: Backend

```cmd
cd C:\wamp64\www\Projects\djangoProject\backend
venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```

#### Terminal 2: Frontend

```cmd
cd C:\wamp64\www\Projects\djangoProject\frontend
npm run dev
```

### Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend App | http://localhost:3000 | Main application UI |
| Backend API | http://localhost:8000/api/v1/ | REST API endpoints |
| Admin Panel | http://localhost:8000/admin/ | Django admin interface |
| API Docs | http://localhost:8000/api/v1/docs/ | Swagger/OpenAPI docs |

### Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Error: That port is already in use`

**Solution**:
```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F
```

Or change the port:
```cmd
python manage.py runserver 0.0.0.0:8001
```

#### 2. MySQL Access Denied

**Error**: `Access denied for user 'ptms_user'@'localhost'`

**Solution**:
1. Reset the MySQL user password:
   ```sql
   -- In MySQL console
   ALTER USER 'ptms_user'@'localhost' IDENTIFIED BY 'ptms_password';
   FLUSH PRIVILEGES;
   ```

2. Or use root user temporarily:
   ```env
   DB_USER=root
   DB_PASSWORD=your_root_password
   ```

#### 3. Virtual Environment Issues

**Error**: `The system cannot find the path specified`

**Solution**:
```cmd
# Remove existing venv
rmdir /s /q backend\venv

# Recreate
python -m venv backend\venv
backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt
```

#### 4. GDAL/GEOS Not Found (GeoDjango)

**Error**: `OSError: [WinError 126] The specified module could not be found`

**Solution**:
1. Download OSGeo4W from https://trac.osgeo.org/osgeo4w/
2. Install to `C:\OSGeo4W`
3. Add to system PATH or set in `.env`:
   ```env
   GDAL_LIBRARY_PATH=C:/OSGeo4W/bin/gdal309.dll
   GEOS_LIBRARY_PATH=C:/OSGeo4W/bin/geos_c.dll
   ```

#### 5. Node Modules Issues

**Error**: `Cannot find module` or build errors

**Solution**:
```cmd
cd frontend
rmdir /s /q node_modules
del package-lock.json
npm install
```

#### 6. CORS Errors in Browser

**Error**: `Access to XMLHttpRequest has been blocked by CORS policy`

**Solution**:
1. Check backend `.env`:
   ```env
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   CORS_ALLOW_CREDENTIALS=True
   ```

2. Restart backend server after changes

### Getting Help

If you encounter issues not covered here:

1. Check the logs:
   - Backend: `backend/logs/django.log`
   - Frontend: Browser console (F12)

2. Verify all services are running:
   ```cmd
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   netstat -ano | findstr :3306
   ```

3. Consult the documentation in the `docs/` folder

---

## 🔐 First Login

### Using the Default Admin Account

1. Open http://localhost:3000 in your browser
2. Click "Login" 
3. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
4. You now have full access to the system

### Creating Additional Users

1. Go to http://localhost:8000/admin/
2. Login with admin credentials
3. Navigate to **Accounts → Users**
4. Click **"Add user"**
5. Fill in the details and select a role:
   - **Admin**: Full system access
   - **Manager**: Can manage projects and users
   - **Editor**: Can create and edit projects
   - **Viewer**: Read-only access

---

## 📝 Useful Commands

### Backend Commands

```cmd
# Activate virtual environment
backend\venv\Scripts\activate.bat

# Run migrations
cd backend && python manage.py migrate

# Create superuser
cd backend && python manage.py createsuperuser

# Reset database (Caution: Deletes all data!)
cd backend && python manage.py flush

# Run tests
cd backend && pytest

# Django shell
cd backend && python manage.py shell

# Check system
cd backend && python manage.py check

# Collect static files (for production)
cd backend && python manage.py collectstatic
```

### Frontend Commands

```cmd
# Start development server
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Preview production build
cd frontend && npm run preview

# Run linter
cd frontend && npm run lint

# Type checking
cd frontend && npm run typecheck
```

### MySQL Commands

```sql
-- Login
mysql -u root -p

-- Show databases
SHOW DATABASES;

-- Use database
USE project_tracking;

-- Show tables
SHOW TABLES;

-- Describe table
DESCRIBE projects_projectsite;

-- Backup database
mysqldump -u root -p project_tracking > backup.sql

-- Restore database
mysql -u root -p project_tracking < backup.sql
```

---

## ✅ Verification Checklist

After setup, verify everything is working:

- [ ] WAMP icon is green in system tray
- [ ] Can access http://localhost/phpmyadmin
- [ ] Database `project_tracking` exists
- [ ] Virtual environment activated
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] `.env` files configured
- [ ] Migrations applied successfully
- [ ] Superuser created
- [ ] Seed data loaded
- [ ] Backend server starts on port 8000
- [ ] Frontend server starts on port 3000
- [ ] Can login at http://localhost:3000
- [ ] API docs accessible at http://localhost:8000/api/v1/docs/

---

**Congratulations!** Your Project Tracking Management System is now ready to use on Windows with WAMP.
