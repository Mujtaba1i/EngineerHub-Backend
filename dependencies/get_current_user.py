from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models.user import UserModel
from database import get_db
import jwt
from jwt import DecodeError, ExpiredSignatureError
from config.environment import secret

http_bearer = HTTPBearer()

def get_current_user(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(http_bearer)):
    try:
        payload = jwt.decode(token.credentials, secret, algorithms=["HS256"])
        user = db.query(UserModel).filter(UserModel.id == payload.get("sub")).first()

        if not user:
            raise HTTPException(status_code=401,detail="Invalid username or password")

    except DecodeError as e:
        raise HTTPException(status_code=403,detail=f'Could not decode token: {str(e)}')

    except ExpiredSignatureError:
        raise HTTPException(status_code=403,detail='Token has expired')

    return user
