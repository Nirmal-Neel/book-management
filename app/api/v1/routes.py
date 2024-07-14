from fastapi.routing import APIRouter

from .books.routes import book_route
from .recommendations.routes import recommendation_route
from .summary.routes import summary_route


v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(book_route)
v1_router.include_router(recommendation_route)
v1_router.include_router(summary_route)

