import logging
from app.tasks.celery_app import celery
from app.database import SyncSessionLocal
from app.models.inventory import Inventory, InventoryHistory
from sqlalchemy import func

logger = logging.getLogger("celery.tasks.inventory")

@celery.task
def reconcile_inventory_task():
    logger.info("Executing automated inventory reconciliation task...")
    session = SyncSessionLocal()
    try:
        inventories = session.query(Inventory).all()
        reconciled = 0
        for inv in inventories:
            # sum change_quantity from history
            history_sum = session.query(func.coalesce(func.sum(InventoryHistory.change_quantity), 0)).filter(
                InventoryHistory.inventory_id == inv.id
            ).scalar()
            
            # If mismatch, correct available quantity or log discrepancy
            if history_sum != inv.available_quantity:
                logger.warning(
                    f"Discrepancy found for Inventory ID {inv.id}. Recorded: {inv.available_quantity}, Calculated: {history_sum}"
                )
                reconciled += 1
        session.commit()
        logger.info(f"Inventory reconciliation completed. Discrepancies flagged: {reconciled}")
        return {"status": "SUCCESS", "discrepancies": reconciled}
    except Exception as e:
        session.rollback()
        logger.error(f"Error during inventory reconciliation: {str(e)}")
        raise e
    finally:
        session.close()
