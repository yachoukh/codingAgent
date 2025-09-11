# FastAPI Space Travel Agency Application

This is a FastAPI web application for a space travel agency using PostgreSQL database. The application is deployable to Azure via Azure App Service and includes comprehensive CI/CD with GitHub Actions.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Environment Setup and Dependencies
**CRITICAL: NEVER CANCEL long-running commands. Follow the exact timeout guidelines below.**

1. **Initial Setup (Total time: ~60 seconds)**:
   ```bash
   # Upgrade pip (4 seconds - use 60s timeout)
   python3 -m pip install --upgrade pip
   
   # Install development dependencies (15 seconds - use 120s timeout) 
   python3 -m pip install -r requirements-dev.txt
   
   # Install application as editable package (35 seconds - use 300s timeout)
   python3 -m pip install -e src
   ```

2. **PostgreSQL Setup (Required for all operations)**:
   ```bash
   # Start PostgreSQL service if needed
   sudo service postgresql start
   
   # Setup database (if not exists)
   sudo -u postgres createdb postgres || echo "Database exists"
   sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
   
   # Set environment variables (required for all operations)
   export POSTGRES_HOST=localhost
   export POSTGRES_USERNAME=postgres  
   export POSTGRES_PASSWORD=postgres
   export POSTGRES_DATABASE=postgres
   export POSTGRES_PORT=5432
   ```

3. **Database Seeding (4 seconds - use 60s timeout)**:
   ```bash
   python3 src/fastapi_app/seed_data.py
   ```

### Running the Application

1. **Development Server (Uvicorn)**:
   ```bash
   # ALWAYS set PostgreSQL environment variables first
   python3 -m uvicorn fastapi_app:app --reload --port=8000
   ```
   - Starts immediately and serves on http://localhost:8000
   - Use for development and testing
   - Supports hot reload

2. **Production Server (Gunicorn) - WARNING: May have configuration issues**:
   ```bash
   python3 -m gunicorn fastapi_app:app --bind 0.0.0.0:8001
   ```
   - Note: Gunicorn may return 500 errors in some environments
   - Use Uvicorn for development and testing

### Testing

1. **Unit Tests (2 seconds - use 60s timeout)**:
   ```bash
   # ALWAYS set PostgreSQL environment variables first
   python3 -m pytest src/tests/local/test_gunicorn.py -v
   ```
   - Only one unit test exists currently
   - Test validates Gunicorn configuration imports

2. **Playwright Tests - WARNING: Browser installation fails**:
   ```bash
   # This command WILL FAIL in restricted environments (45+ seconds timeout)
   playwright install chromium --with-deps
   ```
   - **KNOWN ISSUE**: Playwright browser downloads fail due to network restrictions
   - Do NOT run Playwright tests until browser installation succeeds
   - Skip with: `python3 -m pytest --ignore=src/tests/local/test_playwright.py`

3. **Smoke Tests**:
   - Currently depend on Playwright tests 
   - Will not run until Playwright is working
   - Located in `src/tests/smoke/`

### Code Quality

1. **Linting (instant - use 60s timeout)**:
   ```bash
   ruff check .
   ```
   - Very fast execution
   - Will show deprecation warnings about pyproject.toml format (safe to ignore)

2. **Formatting (instant - use 60s timeout)**:
   ```bash
   ruff format .
   ```
   - Very fast execution
   - Formats all Python files

3. **ALWAYS run before committing**:
   ```bash
   ruff check . && ruff format .
   ```

## Validation Scenarios

### Manual Application Testing
After making changes, ALWAYS validate by:

1. **Start the application**:
   ```bash
   export POSTGRES_HOST=localhost POSTGRES_USERNAME=postgres POSTGRES_PASSWORD=postgres POSTGRES_DATABASE=postgres
   python3 -m uvicorn fastapi_app:app --reload --port=8000
   ```

2. **Test basic functionality**:
   ```bash
   # Test homepage loads
   curl -s http://localhost:8000/ | head -10
   ```
   - Should return HTML with "ReleCloud" content
   - Verify CSS and static files load

3. **Test API endpoints** (if applicable):
   - Navigate to http://localhost:8000 in browser
   - Verify space travel booking interface works
   - Test destination and cruise data displays correctly

### CI/CD Validation
Before pushing changes, ensure CI will pass:

1. **Run linting checks**:
   ```bash
   ruff check .
   ruff format .
   ```

2. **Run available tests**:
   ```bash
   python3 -m pytest src/tests/local/test_gunicorn.py
   ```

3. **Verify database operations work**:
   ```bash
   python3 src/fastapi_app/seed_data.py
   ```

## Build Timing Expectations

**NEVER CANCEL these operations - set appropriate timeouts:**

- **pip upgrade**: 4 seconds (use 60s timeout)
- **requirements-dev.txt installation**: 15 seconds (use 120s timeout)  
- **Application installation**: 35 seconds (use 300s timeout)
- **Database seeding**: 4 seconds (use 60s timeout)
- **Unit tests**: 2 seconds (use 60s timeout)
- **Playwright browser install**: FAILS after 15+ seconds (use 900s timeout, expect failure)
- **Ruff linting**: Instant (use 60s timeout)
- **Ruff formatting**: Instant (use 60s timeout)

## Repository Structure

### Key Files and Directories
```
├── src/
│   ├── fastapi_app/           # Main application code
│   │   ├── app.py             # FastAPI application entry point
│   │   ├── models.py          # SQLModel database models
│   │   └── seed_data.py       # Database seeding script
│   ├── requirements.txt       # Production dependencies
│   ├── tests/
│   │   ├── local/             # Local tests (unit tests)
│   │   └── smoke/             # Smoke tests (integration)
│   └── templates/             # Jinja2 HTML templates
├── requirements-dev.txt       # Development dependencies
├── pyproject.toml            # Project configuration (ruff, pytest)
└── .github/workflows/        # CI/CD workflows
```

### Common Commands Quick Reference
```bash
# Full environment setup from scratch
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-dev.txt  
python3 -m pip install -e src
export POSTGRES_HOST=localhost POSTGRES_USERNAME=postgres POSTGRES_PASSWORD=postgres POSTGRES_DATABASE=postgres
python3 src/fastapi_app/seed_data.py

# Start development server
python3 -m uvicorn fastapi_app:app --reload --port=8000

# Code quality checks
ruff check . && ruff format .

# Run tests
python3 -m pytest src/tests/local/test_gunicorn.py
```

## Known Issues and Limitations

1. **Playwright Installation**: Browser downloads fail in restricted environments
   - Skip Playwright tests until installation succeeds
   - Use `--ignore=src/tests/local/test_playwright.py` flag

2. **Gunicorn Server**: May return 500 errors in some configurations
   - Use Uvicorn for development and testing
   - Gunicorn works for deployment but may need configuration adjustments

3. **Azure CLI**: Not available in all environments
   - Azure deployment requires separate Azure CLI installation
   - Use `azd` commands when available

4. **pyproject.toml Warnings**: Ruff shows deprecation warnings
   - Safe to ignore - warnings about moving lint configuration to `lint` section
   - Does not affect functionality

## Environment Variables Required

**ALWAYS set these before any database operations:**
```bash
export POSTGRES_HOST=localhost
export POSTGRES_USERNAME=postgres
export POSTGRES_PASSWORD=postgres  
export POSTGRES_DATABASE=postgres
export POSTGRES_PORT=5432
```

**Optional for Azure monitoring:**
```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING=<connection_string>
```