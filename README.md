# CodeAI Assistant

An AI-powered code assistant that helps with debugging, correcting, and generating code using Google's Gemini API.

## Features

- Debug code and identify potential issues
- Correct and improve existing code
- Generate new code based on descriptions
- Support for multiple programming languages
- Modern React frontend with Material-UI
- FastAPI backend with Gemini AI integration

## Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Google Gemini API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file:
```bash
cp .env.example .env
```

4. Add your Gemini API key to the .env file:
```
GOOGLE_API_KEY=your_api_key_here
```

5. Run the backend server:
```bash
python run.py
```

The backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## API Endpoints

- `POST /api/code` - Process code (debug/correct/generate)
- `GET /api/languages` - Get supported programming languages
- `GET /api/tasks` - Get supported tasks
- `GET /api/health` - Check API health

## Supported Languages

- Python
- JavaScript
- TypeScript
- Java
- C++
- Rust
- Go

## Contributing

Feel free to open issues and pull requests for any improvements.

## License

MIT License
