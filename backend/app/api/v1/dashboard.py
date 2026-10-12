from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()


def _require_tenant(current_user) -> str:
    tenant_id = getattr(current_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User is not assigned to a tenant")
    return tenant_id


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = _require_tenant(current_user)

    if (month is None) != (year is None):
        raise HTTPException(status_code=400, detail="month and year must be provided together")

    try:
        revenue_data = await get_revenue_summary(property_id, tenant_id, month, year)
    except Exception:
        raise HTTPException(status_code=503, detail="Revenue data is temporarily unavailable")
    
    return {
        "property_id": revenue_data['property_id'],
        # Sent as a decimal string; floats lose cents.
        "total_revenue": revenue_data['total'],
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
