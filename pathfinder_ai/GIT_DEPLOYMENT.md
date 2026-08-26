# Git Setup & Deployment Guide

## Git Repository Setup

### 1. Initialize Git Repository (First Time)

```bash
# Navigate to project root
cd pathfinder_ai

# Initialize git
git init

# Check status
git status
```

### 2. Configure Git (if not already done)

```bash
# Set your identity
git config --global user.name "Bhabana Kalita"
git config --global user.email "bhabana@example.com"

# Verify
git config --list
```

### 3. Create .gitignore

```bash
# Create .gitignore in pathfinder_ai root
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Environment variables
.env
.env.local
.env.*.local

# Databases
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# OS
Thumbs.db
.DS_Store
EOF

# Verify gitignore
git status
```

### 4. Initial Commit

```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Complete AI/ML module for PathFinder

- Skill gap analysis with career-to-skill mapping
- Resource ranking and recommendation engine
- Learning path generation with prerequisite handling
- Adaptive learning with progress tracking
- Comprehensive unit tests (40+ tests)
- Full documentation and examples
- Integration guide for FastAPI backend"

# View commit
git log
```

### 5. Create Branches for Team

```bash
# Create feature branch
git checkout -b feature/custom-careers

# Switch back to main
git checkout main

# Push to remote (if you have a remote)
git push origin main
```

## Collaboration Setup

### Push to Remote Repository

```bash
# Add remote (GitHub, GitLab, etc.)
git remote add origin https://github.com/yourusername/pathfinder-ai.git

# Push main branch
git push -u origin main

# Push all branches
git push --all
```

### Team Members Cloning

```bash
# Clone the repository
git clone https://github.com/yourusername/pathfinder-ai.git

# Install dependencies
cd pathfinder_ai
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

## Feature Development Workflow

### 1. Start New Feature

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/new-career-support
```

### 2. Make Changes

```bash
# Edit files
# Run tests
python -m pytest tests/

# Stage changes
git add pathfinder_ai/config/careers.py
git add tests/

# Commit with clear message
git commit -m "feat: Add support for new career paths

- Added 5 new career definitions
- Updated skill importance weights
- Added unit tests for new careers"
```

### 3. Push & Create Pull Request

```bash
# Push feature branch
git push origin feature/new-career-support

# Create PR on GitHub/GitLab
# Fill in PR template with description of changes
```

### 4. After Approval, Merge

```bash
# Switch to main
git checkout main
git pull origin main

# Merge feature
git merge feature/new-career-support

# Push merged code
git push origin main

# Delete feature branch
git branch -d feature/new-career-support
git push origin -d feature/new-career-support
```

## Versioning

### Semantic Versioning

```
version = MAJOR.MINOR.PATCH

MAJOR: Breaking changes
MINOR: New features (backward compatible)
PATCH: Bug fixes
```

### Create Version Tags

```bash
# Create tag for v0.1.0
git tag -a v0.1.0 -m "Release version 0.1.0: Initial production release"

# Push tag
git push origin v0.1.0

# List tags
git tag -l

# View specific tag
git show v0.1.0
```

## Deployment

### Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run examples
python examples.py
```

### Production Environment

#### Option 1: Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY pathfinder_ai ./pathfinder_ai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from pathfinder_ai import analyze_skill_gap; print('OK')"

# Run application (FastAPI server)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build image
docker build -t pathfinder-ai:0.1.0 .

# Run container
docker run -p 8000:8000 pathfinder-ai:0.1.0

# Push to registry
docker tag pathfinder-ai:0.1.0 yourregistry/pathfinder-ai:0.1.0
docker push yourregistry/pathfinder-ai:0.1.0
```

#### Option 2: Direct Installation

```bash
# On production server
git clone https://github.com/yourusername/pathfinder-ai.git
cd pathfinder_ai

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start FastAPI server (with your backend)
cd /path/to/fastapi_backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
# AI/ML Module Settings
CACHE_ENABLED=true
RECOMMENDATION_TOP_N=10
LEARNING_PATH_MAX_LENGTH=20

# LLM Integration
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-4

# Database
DATABASE_URL=postgresql://user:password@localhost/pathfinder

# Server
DEBUG=false
LOG_LEVEL=INFO
EOF

# Load in Python
from dotenv import load_dotenv
import os

load_dotenv()
debug_mode = os.getenv("DEBUG", "false") == "true"
```

### Testing Before Deployment

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=pathfinder_ai

# Run specific test module
python -m pytest tests/test_skill_gap.py -v

# Generate coverage report
pytest --cov=pathfinder_ai --cov-report=html
# Open htmlcov/index.html in browser
```

### Performance Verification

```bash
# Profile code
python -m cProfile -s cumtime examples.py

# Memory usage
pip install memory_profiler
python -m memory_profiler examples.py

# Timing
python -m timeit "from pathfinder_ai import analyze_skill_gap"
```

## CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest tests/ -v --cov=pathfinder_ai
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### GitLab CI Example

```yaml
# .gitlab-ci.yml
image: python:3.11

stages:
  - test
  - deploy

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/ -v --cov=pathfinder_ai
  coverage: '/TOTAL.*\s+(\d+%)$/'

deploy:
  stage: deploy
  script:
    - docker build -t pathfinder-ai:latest .
    - docker push registry.example.com/pathfinder-ai:latest
  only:
    - main
```

## Monitoring & Logging

### Application Logging

```python
# In your FastAPI app
import logging
from pathfinder_ai import analyze_skill_gap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/recommendations")
def get_recommendations(profile):
    try:
        logger.info(f"Getting recommendations for {profile.user_id}")
        gap = analyze_skill_gap(profile)
        logger.debug(f"Found {len(gap.missing_skills)} missing skills")
        return ...
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise
```

### Performance Monitoring

```python
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@measure_time
def analyze_skill_gap_monitored(profile):
    return analyze_skill_gap(profile)
```

## Rollback Procedures

### If Deployment Fails

```bash
# View deployment history
git log --oneline

# Revert to previous version
git revert HEAD

# Or reset hard (use with caution)
git reset --hard <commit-hash>

# Push rollback
git push origin main
```

### Database Rollback

```bash
# If using Alembic for migrations
alembic downgrade -1

# View migration history
alembic current
```

## Maintenance

### Regular Tasks

```bash
# Update dependencies (monthly)
pip list --outdated
pip install --upgrade -r requirements.txt

# Clean cache (when issues arise)
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Update tests and documentation
python -m pytest tests/ -v
grep -r "TODO\|FIXME" pathfinder_ai/
```

### Backup Procedures

```bash
# Backup entire module
tar -czf pathfinder_ai_backup_$(date +%Y%m%d).tar.gz pathfinder_ai/

# Backup git history
git bundle create pathfinder_ai.bundle --all
```

## Common Commands Reference

```bash
# Check what files changed
git diff

# Check status
git status

# View commit history
git log --oneline -10

# Create new branch
git checkout -b feature/feature-name

# Switch branch
git checkout main

# Merge branch
git merge feature/feature-name

# Delete branch
git branch -d feature/feature-name

# Stash changes (temporary)
git stash
git stash pop

# See who changed what
git blame file.py
```

## Troubleshooting

### Merge Conflicts

```bash
# During merge, if conflicts occur:
# 1. Edit conflicted files (<<<<<<, ======, >>>>>>)
# 2. Resolve manually or use tool:
git mergetool

# 3. Mark as resolved
git add <resolved-file>
git commit -m "Resolve merge conflict"
```

### Undo Last Commit

```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

### Check What's in a Commit

```bash
git show <commit-hash>
git show <commit-hash>:pathfinder_ai/config/careers.py
```

## Release Checklist

- [ ] Update version in `__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Run all tests: `pytest tests/`
- [ ] Update README.md if needed
- [ ] Commit with message: "Release v0.X.X"
- [ ] Create tag: `git tag -a v0.X.X -m "Release v0.X.X"`
- [ ] Push commits: `git push origin main`
- [ ] Push tags: `git push origin v0.X.X`
- [ ] Create release notes on GitHub
- [ ] Deploy to production
- [ ] Monitor for errors

---

**Created by**: Bhabana Kalita
**Last Updated**: 2026-08-27
