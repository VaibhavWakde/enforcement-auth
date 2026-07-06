from fastapi import APIRouter, Depends
from app.dependencies.auth_dependencies import get_current_user
from app.models.enf_user import User

# This router has dependencies specified at the router level.
# ALL endpoints within this router are automatically protected.
router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/dashboard")
def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """
    Protected endpoint: accesses current user information.
    """
    return {
        "status": "SUCCESS",
        "message": "Welcome to the admin dashboard!",
        "user_email": current_user.email
    }


@router.get("/settings")
def get_admin_settings():
    """
    Protected endpoint: does not access user info, but requires authentication.
    """
    return {
        "status": "SUCCESS",
        "settings": {
            "maintenance_mode": False,
            "allow_signup": True
        }
    }
