from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import navigate, session, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("UI Navigator API starting")
    yield
    print("UI Navigator API shutting down")

app = FastAPI(title="UI Navigator API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Chrome extension needs this
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(navigate.router, prefix="/v1")
app.include_router(session.router,  prefix="/v1")
app.include_router(health.router)