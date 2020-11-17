from fastapi import APIRouter

rfm_router = APIRouter()


@rfm_router.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "Foo"}, {"username": "Bar"}]
