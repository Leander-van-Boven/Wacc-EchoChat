from fastapi import APIRouter

generic_router = APIRouter(
    tags=['generic'],
)


@generic_router.get('/healthz')
async def healthz():
    """
    Health check endpoint.
    Used by Kubernetes to check if the service is up.
    :return: `dict`
    """
    return {"status": "ok"}
