# Backend Setup with Virtual Environment

## Initial Setup (One-time)

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
.\venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Backend

### Start the Server (with virtual environment)

**Option 1: Activate first, then run**
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start server
uvicorn app.main:app --reload --port 8000
```

**Option 2: Run directly with venv Python**
```bash
# From backend directory
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**Option 3: Use full path to uvicorn**
```bash
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

## Verify Installation

Check if virtual environment is activated:
```bash
# Should show path to venv
where python
```

Check installed packages:
```bash
pip list
```

## Deactivate Virtual Environment

When you're done:
```bash
deactivate
```

## Quick Start Commands

**Start Backend (from project root):**
```bash
cd backend
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

**Start Frontend (from project root):**
```bash
cd frontend
npm run dev
```

## Troubleshooting

### Virtual environment not found
- Make sure you're in the `backend` directory
- Run `python -m venv venv` to create it

### Module not found errors
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Port already in use
- Kill the process using port 8000
- Or use a different port: `--port 8001`

### PowerShell execution policy error
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Environment Structure

```
backend/
├── venv/                    # Virtual environment (gitignored)
│   ├── Scripts/            # Windows executables
│   ├── Lib/                # Python packages
│   └── ...
├── app/                     # Application code
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Adding New Dependencies

1. Activate virtual environment
2. Install package: `pip install package-name`
3. Update requirements: `pip freeze > requirements.txt`

## Current Status

✅ Virtual environment created at `backend/venv/`
✅ Backend is currently running on http://localhost:8000
✅ Frontend is currently running on http://localhost:5173

To restart with virtual environment, stop the current backend and use:
```bash
cd backend
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```
