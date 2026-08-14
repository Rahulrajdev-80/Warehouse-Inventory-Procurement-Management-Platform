import logging
from app.tasks.celery_app import celery
from app.database import SyncSessionLocal
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder, POStatus
from app.utils.email_notifier import EmailNotifier

logger = logging.getLogger("celery.tasks.reports")

@celery.task
def calculate_supplier_performance_task():
    logger.info("Calculating supplier performance ratings...")
    session = SyncSessionLocal()
    try:
        suppliers = session.query(Supplier).all()
        updated_count = 0
        for sup in suppliers:
            total_pos = session.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == sup.id).count()
            completed_pos = session.query(PurchaseOrder).filter(
                PurchaseOrder.supplier_id == sup.id,
                PurchaseOrder.status == POStatus.COMPLETED
            ).count()

            if total_pos > 0:
                completion_rate = completed_pos / float(total_pos)
                new_rating = round(min(5.0, max(1.0, completion_rate * 5.0)), 1)
                sup.rating = new_rating
                updated_count += 1

        session.commit()
        logger.info(f"Supplier ratings updated for {updated_count} suppliers.")
        return {"status": "SUCCESS", "updated_suppliers": updated_count}
    except Exception as e:
        session.rollback()
        logger.error(f"Error calculating supplier ratings: {str(e)}")
        raise e
    finally:
        session.close()

@celery.task
def generate_daily_inventory_report_task():
    logger.info("Generating daily inventory summary report...")
    # Email daily report to management
    EmailNotifier.send_email(
        to_email="admin@warehouse.com",
        subject="Daily Inventory Summary Report",
        body="Daily automated warehouse summary report generated successfully."
    )
    return {"status": "SUCCESS", "report_sent": True}
