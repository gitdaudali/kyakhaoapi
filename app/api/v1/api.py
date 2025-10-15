from fastapi import APIRouter

from app.api.v1.admin.api import router as admin_router
from app.api.v1.endpoints import auth, content, streaming, users, stripe, subscriptions, user_policy, faq, policy

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(streaming.router, prefix="/streaming", tags=["streaming"])
api_router.include_router(stripe.router, prefix="/stripe", tags=["stripe-billing"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(user_policy.router, prefix="/policies", tags=["user-policies"])
api_router.include_router(policy.router, prefix="/policy", tags=["policy"])
api_router.include_router(faq.router, prefix="/faq", tags=["faq"])

# Include admin router
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
