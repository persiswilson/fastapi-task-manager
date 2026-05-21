from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import List, Optional

from ..database import get_db
from ..models import User, Task
from ..schemas import TaskCreate, TaskUpdate, TaskResponse
from app.auth import settings
router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

# Tells FastAPI where to look for the authentication token (the /login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency that decodes the JWT token to authenticate the user for protected routes.
    Throws a 401 Unauthorized exception if validation fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token using our secret configuration
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Check if the user still exists in the database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# 1. CREATE A TASK
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Creates a new task tied strictly to the authenticated user."""
    new_task = Task(**task_data.model_dump(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# 2. VIEW ALL USER TASKS (With Filtering & Pagination)
@router.get("", response_model=List[TaskResponse])
def get_tasks(
    completed: Optional[bool] = Query(None, description="Filter tasks by completion status"),
    skip: int = Query(0, ge=0, description="Number of items to skip (for pagination)"),
    limit: int = Query(10, ge=1, le=100, description="Max number of items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all tasks belonging to the authenticated user.
    Supports filtering by ?completed=true/false and pagination using skip and limit parameters.
    """
    # Start query filtering by the current logged-in user
    query = db.query(Task).filter(Task.owner_id == current_user.id)
    
    # Apply completion filter if provided (?completed=true)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    
    # Apply pagination (skip and limit) and execute query
    tasks = query.offset(skip).limit(limit).all()
    return tasks


# 3. VIEW A SPECIFIC TASK
@router.get("/{id}", response_model=TaskResponse)
def get_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieves a single task by ID only if it belongs to the authenticated user."""
    task = db.query(Task).filter(Task.id == id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or unauthorized.")
    return task


# 4. MARK A TASK AS COMPLETED / UPDATE TASK
@router.put("/{id}", response_model=TaskResponse)
def update_task(id: int, task_update: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Updates fields or marks a task completed only if it belongs to the authenticated user."""
    task = db.query(Task).filter(Task.id == id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or unauthorized.")
    
    # Update only the fields that were actually provided in the request body
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    db.commit()
    db.refresh(task)
    return task


# 5. DELETE A TASK
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Deletes a task permanently if it belongs to the authenticated user."""
    task = db.query(Task).filter(Task.id == id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or unauthorized.")
    
    db.delete(task)
    db.commit()
    return None