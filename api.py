"""FastAPI entry point (optional)."""

from typing import Optional
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import JSONResponse
import json

app = FastAPI(title="Hiring Agent Workflow API")


@app.get("/")
async def root():
    return {"message": "Hiring Agent Workflow API", "version": "1.0.0"}


@app.post("/analyze")
async def analyze(
    input_type: str = Form(...),
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    jd_text: Optional[str] = Form(None)
):
    """Analyze candidate or project input."""
    from workflow.graph import run_workflow

    # Get input text
    if file:
        content = await file.read()
        input_text = content.decode("utf-8")
    elif text:
        input_text = text
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "请提供 text 或 file 参数"}
        )

    # Run workflow
    result = run_workflow(input_text, input_type=input_type, jd_text=jd_text)

    return result


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)