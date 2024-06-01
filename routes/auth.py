from fastapi import APIRouter, Body, Request
from src.auth.auth_handler import signJWT, hash_password, check_user
from src.database.interaction import create_user_db, get_users_as_dicts
from src.auth.auth_bearer import JWTBearer
import src.database.init as db
from fastapi import Depends, HTTPException, status
import models.auth as mauth


router = APIRouter()


@router.post("/user/signup", tags=["auth"])
async def create_user(request: Request, user: mauth.UserSchema = Body(...)):
    """create user, signs a JWT token as result"""
    if not db.check_connection(engine=request.app.state.engine):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="connection to db failed"
        )
    create_user_db(
        request.app.state.engine,
        user.fullname,
        user.email,
        hash_password(user.password),
    )
    return signJWT(user.email)


# TODO[] deve essere un errore quello che esce da questa route, non un 200, ma un 403
@router.post("/user/login", tags=["auth"])
async def user_login(request: Request, user: mauth.UserLoginSchema = Body(...)):
    """user this when the JWT has expired, recreate the token"""
    if not db.check_connection(engine=request.app.state.engine):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="connection to db failed"
        )
    if check_user(request.app.state.engine, user):
        return signJWT(user.email)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Wrong login details!"
    )


@router.get("/user/all", tags=["auth"], dependencies=[Depends(JWTBearer())])
async def get_user(
    request: Request,
):
    if not db.check_connection(engine=request.app.state.engine):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="connection to db failed"
        )
    """THIS FUNCTION SHOULD NOT EXIST. DO NOT PUSH IT IN PRODUCTION"""
    return {"users": get_users_as_dicts(request.app.state.engine)}
