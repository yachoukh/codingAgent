import os
import pathlib
from typing import Annotated

from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from starlette.middleware.sessions import SessionMiddleware

from .auth import (
    authenticate_user,
    get_current_user,
    get_password_hash,
    get_user_by_email,
    get_user_by_username,
    require_authentication,
)
from .models import Cruise, Destination, InfoRequest, User, engine

if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor()

app = FastAPI()

# Add session middleware for authentication
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
parent_path = pathlib.Path(__file__).parent.parent
app.mount("/mount", StaticFiles(directory=parent_path / "static"), name="static")
templates = Jinja2Templates(directory=parent_path / "templates")
templates.env.globals["prod"] = os.environ.get("RUNNING_IN_PRODUCTION", False)
# Use relative path for url_for, so that it works behind a proxy like Codespaces
templates.env.globals["url_for"] = app.url_path_for


@app.get("/", response_class=HTMLResponse)
def index(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})


@app.get("/about", response_class=HTMLResponse)
def about(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("about.html", {"request": request, "current_user": current_user})


@app.get("/destinations", response_class=HTMLResponse)
def destinations(request: Request, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        all_destinations = session.exec(select(Destination)).all()
    return templates.TemplateResponse(
        "destinations.html", 
        {
            "request": request, 
            "destinations": all_destinations, 
            "current_user": current_user
        }
    )


@app.get("/destination/{pk}", response_class=HTMLResponse)
def destination_detail(request: Request, pk: int, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        destination = session.exec(select(Destination).where(Destination.id == pk)).first()
        return templates.TemplateResponse(
            "destination_detail.html", 
            {
                "request": request, 
                "destination": destination, 
                "cruises": destination.cruises, 
                "current_user": current_user
            }
        )


@app.get("/cruise/{pk}")
def cruise_detail(request: Request, pk: int, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        cruise = session.exec(select(Cruise).where(Cruise.id == pk)).first()
        return templates.TemplateResponse(
            "cruise_detail.html", 
            {
                "request": request, 
                "cruise": cruise, 
                "destinations": cruise.destinations, 
                "current_user": current_user
            }
        )


@app.get("/info_request/", response_class=HTMLResponse)
def info_request(request: Request, current_user: User = Depends(require_authentication)):
    with Session(engine) as session:
        all_cruises = session.exec(select(Cruise)).all()
        return templates.TemplateResponse(
            "info_request_create.html", 
            {
                "request": request, 
                "cruises": all_cruises, 
                "current_user": current_user
            }
        )


@app.post("/info_request/", response_model=InfoRequest)
def create_info_request(
    request: Request, 
    info_request: Annotated[InfoRequest, Form()], 
    current_user: User = Depends(require_authentication)
):
    with Session(engine) as session:
        session.add(info_request)
        session.commit()
        session.refresh(info_request)
        all_cruises = session.exec(select(Cruise)).all()
        return templates.TemplateResponse(
            "info_request_create.html",
            {
                "request": request,
                "cruises": all_cruises,
                "current_user": current_user,
                "message": "Information request submitted.",
            },
        )


# Authentication routes
@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request, current_user: User = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup", response_class=HTMLResponse)
def signup(
    request: Request,
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    current_user: User = Depends(get_current_user)
):
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Check if username or email already exists
    if get_user_by_username(username):
        return templates.TemplateResponse(
            "signup.html", 
            {"request": request, "error": "Username already exists"}
        )
    
    if get_user_by_email(email):
        return templates.TemplateResponse(
            "signup.html", 
            {"request": request, "error": "Email already exists"}
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Log user in
        request.session["user_id"] = user.id
        
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, current_user: User = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    current_user: User = Depends(get_current_user)
):
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid username or password"}
        )
    
    # Log user in
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
