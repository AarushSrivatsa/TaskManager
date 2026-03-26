from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.employee import router as employee_router
from routers.manager import router as manager_router
from contextlib import asynccontextmanager
from database.models import create_tables
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(
    title="Task Management API",
    version="1.0.0",
    description="Role-based task management system for managers and employees",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse("/static/index.html")

router_list = [employee_router,manager_router]

for router in router_list:
    app.include_router(router)