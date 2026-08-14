from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.alert import Alert, AlertType
from app.models.user import User
from app.schemas.alert import AlertResponse
from app.security import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    unacknowledged_only: bool = False,
    alert_type: Optional[AlertType] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List System Alerts (Low stock, Out of stock, Overstock, Expired)"""
    stmt = select(Alert).options(selectinload(Alert.product), selectinload(Alert.warehouse)).order_by(Alert.timestamp.desc())
    if unacknowledged_only:
        stmt = stmt.where(Alert.is_acknowledged == False)
    if alert_type:
        stmt = stmt.where(Alert.alert_type == alert_type)

    res = await db.execute(stmt)
    return res.scalars().all()

@router.put("/{id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Acknowledge Alert"""
    stmt = select(Alert).options(selectinload(Alert.product), selectinload(Alert.warehouse)).where(Alert.id == id)
    res = await db.execute(stmt)
    alert = res.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_acknowledged = True
    await db.commit()
    await db.refresh(alert)
    return alert
