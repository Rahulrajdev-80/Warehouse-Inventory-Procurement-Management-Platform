import logging
from app.tasks.celery_app import celery
from app.database import SyncSessionLocal
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.alert import Alert, AlertType
from app.utils.email_notifier import EmailNotifier

logger = logging.getLogger("celery.tasks.alerts")

@celery.task
def check_expired_and_low_stock_task():
    logger.info("Executing automated low stock & expired product check task...")
    session = SyncSessionLocal()
    try:
        inventories = session.query(Inventory).all()
        alerts_created = 0
        for inv in inventories:
            product = session.query(Product).filter(Product.id == inv.product_id).first()
            if not product:
                continue

            if inv.available_quantity <= product.reorder_level:
                # Check if unacknowledged alert already exists
                existing = session.query(Alert).filter(
                    Alert.product_id == inv.product_id,
                    Alert.warehouse_id == inv.warehouse_id,
                    Alert.is_acknowledged == False
                ).first()

                if not existing:
                    alert_type = AlertType.OUT_OF_STOCK if inv.available_quantity == 0 else AlertType.LOW_STOCK
                    alert = Alert(
                        product_id=inv.product_id,
                        warehouse_id=inv.warehouse_id,
                        alert_type=alert_type,
                        current_quantity=inv.available_quantity,
                        threshold_quantity=product.reorder_level,
                        message=f"Automated Scan: Product '{product.name}' (SKU: {product.sku}) stock ({inv.available_quantity}) below reorder level ({product.reorder_level})"
                    )
                    session.add(alert)
                    alerts_created += 1

                    EmailNotifier.send_email(
                        to_email="manager@warehouse.com",
                        subject=f"Low Stock Alert: {product.name}",
                        body=f"Product {product.name} (SKU: {product.sku}) current stock is {inv.available_quantity}."
                    )

        session.commit()
        logger.info(f"Check completed. New alerts generated: {alerts_created}")
        return {"status": "SUCCESS", "new_alerts": alerts_created}
    except Exception as e:
        session.rollback()
        logger.error(f"Error checking low stock: {str(e)}")
        raise e
    finally:
        session.close()
