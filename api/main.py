from fastapi import FastAPI
from app.auth import router as auth_router
from app.feedback import router as feedback_router
from app.model import router as model_router
from app.user import router as user_router

app = FastAPI(title="NYC Taxi Prediction API", version="1.0.0")

app.include_router(auth_router.router)
app.include_router(feedback_router.router)
app.include_router(model_router.router)
app.include_router(user_router.router) 