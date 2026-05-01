from fastapi import APIRouter,Depends,HTTPException,status
from .database import get_db
from .models import User
from schemas import UserResponse,UserCreate
from sqlalchemy.orm import Session
from sqlalchemy import select
from .auth import hash_password,verify_password,create_access_token,require_roles

router = APIRouter(
    tags=["Register and Login"]
)


@router.post("/register",response_model=UserResponse)
def register(user : UserCreate,db:Session = Depends(get_db))-> UserResponse:

    #normalize email so that there will be no same email with capital and small letter
    email = user.email.lower()

    #check user exists?
    stmt = select(User).where(user.email == email)
    existing_user = db.execute(stmt).scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Already Exists")
    
    #hashed_password
    hashed_password = hash_password(user.password)

    #create_user
    new_user = User(
        email = email,
        hashed_password = hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):

    email = user.email.lower()

    db_user = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": db_user.email
    })

    return {"access_token": token, "token_type": "bearer"}


@router.get("/admin")
def admin_route(
    current_user: User = Depends(require_roles(["admin"]))):
    return {"msg": "Admin only"}