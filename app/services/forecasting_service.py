from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from datetime import datetime, timedelta

from app.models.product import Product
from app.models.inventory import Inventory, InventoryHistory, TransactionType
from app.schemas.inventory import ForecastResponse

class ForecastingService:
    @staticmethod
    async def get_product_forecast(db: AsyncSession, product_id: int) -> ForecastResponse:
        prod_res = await db.execute(select(Product).where(Product.id == product_id))
        product = prod_res.scalars().first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Total available stock across all warehouses
        stock_res = await db.execute(
            select(func.coalesce(func.sum(Inventory.available_quantity), 0)).where(Inventory.product_id == product_id)
        )
        total_stock = stock_res.scalar_one()

        # Calculate total stock out in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        history_res = await db.execute(
            select(func.coalesce(func.sum(InventoryHistory.change_quantity), 0)).where(
                InventoryHistory.product_id == product_id,
                InventoryHistory.transaction_type.in_([TransactionType.STOCK_OUT, TransactionType.TRANSFER_OUT]),
                InventoryHistory.timestamp >= thirty_days_ago
            )
        )
        # change_quantity for stock out is negative
        total_out = abs(history_res.scalar_one())

        avg_daily_demand = max(total_out / 30.0, 1.0) # default min 1 unit/day if new
        predicted_30_days = avg_daily_demand * 30.0
        recommended_reorder = max(0, int(predicted_30_days - total_stock))
        days_remaining = total_stock / avg_daily_demand if avg_daily_demand > 0 else 999.0

        return ForecastResponse(
            product_id=product.id,
            product_sku=product.sku,
            product_name=product.name,
            current_total_stock=total_stock,
            average_daily_demand=round(avg_daily_demand, 2),
            predicted_demand_30_days=round(predicted_30_days, 2),
            recommended_reorder_quantity=recommended_reorder,
            days_of_supply_remaining=round(days_remaining, 1)
        )
