"""File used by Uvicorn to start the application."""

from app.app import get_application
from app.dependencies import get_settings
from app.modules.login import endpoints_login
from app.modules.reports import endpoints_reports
from app.modules.users import endpoints_users
from app.utils.fastapi import use_route_path_as_operation_ids

# The application is started with the following function call:
# We dissociate this step from the app.py file so that during tests we can initialize it with the mocked settings
app = get_application(settings=get_settings())

app.include_router(endpoints_reports.router)
app.include_router(endpoints_login.router)
app.include_router(endpoints_users.router)
use_route_path_as_operation_ids(app)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
