from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    try:
        revenue_data = await get_revenue_summary(property_id, tenant_id)
    except Exception:
        raise HTTPException(status_code=503, detail="Revenue data is temporarily unavailable")
    
    return {
        "property_id": revenue_data['property_id'],
        # Sent as a decimal string; floats lose cents.
        "total_revenue": revenue_data['total'],
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
