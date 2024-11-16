from fastapi import APIRouter

from app.api.routes import items, login, users, utils, companies, patents, infringement

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(patents.router, prefix="/patents", tags=["patents"])
api_router.include_router(infringement.router, prefix="/infringement", tags=["infringement"])
