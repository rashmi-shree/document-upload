from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal
from app.models import User
from passlib.hash import bcrypt
from pydantic import BaseModel
import logging

# Enhanced logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", status_code=201)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    try:
        logger.debug(f"Attempting to create user: {request.username}")
        
        # Check if the user exists
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            logger.warning(f"User already exists: {request.username}")
            raise HTTPException(status_code=400, detail="Username already exists")

        # Create new user
        hashed_password = bcrypt.hash(request.password)
        new_user = User(
            username=request.username,
            password_hash=hashed_password
        )
        
        try:
            db.add(new_user)
            db.flush()  # Flush to get the ID without committing
            logger.debug(f"User added to session with ID: {new_user.id}")
            
            db.commit()
            logger.info(f"User committed to database: {new_user.username} (ID: {new_user.id})")
            
            db.refresh(new_user)
            
            # Verify user was actually saved
            saved_user = db.query(User).filter(User.id == new_user.id).first()
            logger.debug(f"Verified saved user: {saved_user.username if saved_user else 'Not Found'}")
            
            return {
                "message": "Signup successful",
                "user_id": new_user.id,
                "username": new_user.username
            }
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during signup: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/login")
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try:
        logger.debug(f"Login attempt for user: {request.username}")
        
        # Check if user exists
        user = db.query(User).filter(User.username == request.username).first()
        logger.debug(f"Found user: {user.username if user else 'Not Found'}")
        
        if not user:
            logger.warning(f"User not found: {request.username}")
            raise HTTPException(status_code=404, detail="User not found")

        # Log password verification attempt
        is_password_valid = bcrypt.verify(request.password, user.password_hash)
        logger.debug(f"Password verification result: {is_password_valid}")

        if not is_password_valid:
            logger.warning(f"Invalid password for user: {request.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        logger.info(f"Successful login for user: {user.username}")
        
        return {
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/debug/users")
async def list_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        logger.debug(f"Found {len(users)} users in database")
        return [{
            "id": user.id,
            "username": user.username,
            "password_hash_length": len(user.password_hash) if user.password_hash else 0
        } for user in users]
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing users: {str(e)}"
        )

@router.get("/check/{username}")
async def check_user(username: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == username).first()
        result = {
            "exists": user is not None,
            "username": username,
            "user_details": {
                "id": user.id,
                "password_hash_present": bool(user.password_hash)
            } if user else None
        }
        logger.debug(f"User check result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error checking user existence: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking user: {str(e)}"
        )

# Add a test database connection endpoint
@router.get("/debug/db-test")
async def test_db(db: Session = Depends(get_db)):
    try:
        # Test basic query
        result = db.execute("SELECT 1").scalar()
        users_count = db.query(User).count()
        return {
            "database_connected": True,
            "test_query_result": result,
            "users_count": users_count
        }
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        return {
            "database_connected": False,
            "error": str(e)
        }