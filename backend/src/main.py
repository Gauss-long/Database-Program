from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import auth, health, lookups, people, projects, registrations, statistics, teams


app = FastAPI(title="高校竞赛项目管理系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(lookups.router, prefix="/api/lookups", tags=["lookups"])
app.include_router(people.router, prefix="/api/people", tags=["people"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(registrations.router, prefix="/api/registrations", tags=["registrations"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
