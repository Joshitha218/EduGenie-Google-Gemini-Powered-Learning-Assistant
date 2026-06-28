from backend.app.routes.auth import router as auth_router
from backend.app.routes.modules import router as modules_router
from backend.app.routes.history import router as history_router
from backend.app.routes.views import router as views_router

__all__ = ["auth_router", "modules_router", "history_router", "views_router"]
