from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import google.generativeai as genai
from typing import Optional, List
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY environment variable is not set")
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    logger.info("Successfully configured Gemini API")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")
    raise

app = FastAPI(
    title="CodeAI Assistant API",
    description="An AI-powered code assistant using Google's Gemini API",
    version="1.0.0"
)

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str
    language: str
    task: str  # debug/correct/generate

    class Config:
        schema_extra = {
            "example": {
                "code": "def fibonacci(n):\n    return fibonacci(n-1) + fibonacci(n-2)",
                "language": "python",
                "task": "debug"
            }
        }

class CodeResponse(BaseModel):
    result: str
    explanation: Optional[str] = None

SUPPORTED_LANGUAGES = ["python", "javascript", "typescript", "java", "cpp", "rust", "go"]
SUPPORTED_TASKS = ["debug", "correct", "generate"]

def validate_request(request: CodeRequest) -> bool:
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language. Supported languages are: {', '.join(SUPPORTED_LANGUAGES)}")
    if request.task not in SUPPORTED_TASKS:
        raise HTTPException(status_code=400, detail=f"Unsupported task. Supported tasks are: {', '.join(SUPPORTED_TASKS)}")
    return True

def create_prompt(request: CodeRequest) -> str:
    prompts = {
        "debug": f"""Analyze this {request.language} code and provide a detailed debugging report:
1. Identify any bugs, logical errors, or potential issues
2. Explain each problem found
3. Provide the corrected code
4. Add explanatory comments for the fixes

Code to debug:
```{request.language}
{request.code}
```""",
        
        "correct": f"""Review and improve this {request.language} code:
1. Fix any bugs or issues
2. Improve code efficiency and readability
3. Apply best practices
4. Add helpful comments
5. Provide the improved code with explanations

Original code:
```{request.language}
{request.code}
```""",
        
        "generate": f"""Generate {request.language} code based on this description:
1. Create efficient and well-structured code
2. Follow best practices and conventions
3. Include error handling
4. Add comprehensive comments
5. Ensure the code is production-ready

Requirements:
{request.code}"""
    }
    return prompts[request.task]

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

@app.post("/api/code", response_model=CodeResponse)
async def process_code(request: CodeRequest):
    """
    Process code based on the specified task (debug/correct/generate).
    Returns the AI-generated response with explanations and improvements.
    """
    try:
        logger.info(f"Processing {request.task} request for {request.language}")
        validate_request(request)
        prompt = create_prompt(request)
        
        try:
            response = model.generate_content(prompt)
            logger.info("Successfully generated response from Gemini API")
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate response from AI model")
        
        return CodeResponse(
            result=response.text,
            explanation="Code processing completed successfully"
        )
    except HTTPException as he:
        logger.error(f"HTTP exception in process_code: {str(he)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {"languages": SUPPORTED_LANGUAGES}

@app.get("/api/tasks")
async def get_supported_tasks():
    """Get list of supported tasks"""
    return {"tasks": SUPPORTED_TASKS}

@app.get("/api/health")
async def health_check():
    """Check if the API is running and Gemini API is configured"""
    try:
        # Test Gemini API with a simple prompt
        model.generate_content("Test connection")
        api_status = "configured and working"
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        api_status = "error"

    return {
        "status": "healthy",
        "gemini_api": api_status,
        "supported_languages": len(SUPPORTED_LANGUAGES),
        "supported_tasks": len(SUPPORTED_TASKS)
    } 