import csv
import io
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
from app.models.product import Product
from app.models.supplier import Supplier, SupplierStatus
from app.services.inventory_service import InventoryService

class CSVService:
    @staticmethod
    async def import_products_csv(db: AsyncSession, file: UploadFile) -> dict:
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        imported_count = 0
        for row in reader:
            sku = row.get("sku")
            name = row.get("name")
            if not sku or not name:
                continue
            
            prod = Product(
                sku=sku,
                name=name,
                category=row.get("category", "General"),
                brand=row.get("brand", "Generic"),
                unit=row.get("unit", "pcs"),
                cost_price=float(row.get("cost_price", 0.0)),
                selling_price=float(row.get("selling_price", 0.0)),
                reorder_level=int(row.get("reorder_level", 10)),
                barcode=row.get("barcode", sku)
            )
            db.add(prod)
            imported_count += 1
        
        await db.commit()
        return {"imported_count": imported_count, "status": "Success"}

    @staticmethod
    async def import_suppliers_csv(db: AsyncSession, file: UploadFile) -> dict:
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        imported_count = 0
        for row in reader:
            email = row.get("email")
            name = row.get("name")
            if not email or not name:
                continue

            sup = Supplier(
                name=name,
                contact_person=row.get("contact_person", "N/A"),
                email=email,
                phone=row.get("phone", "0000000000"),
                gst_number=row.get("gst_number", "GST000"),
                address=row.get("address", "N/A"),
                rating=float(row.get("rating", 5.0)),
                status=SupplierStatus.ACTIVE
            )
            db.add(sup)
            imported_count += 1

        await db.commit()
        return {"imported_count": imported_count, "status": "Success"}

    @staticmethod
    async def import_inventory_csv(db: AsyncSession, file: UploadFile, user_id: int) -> dict:
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        imported_count = 0
        for row in reader:
            product_id = int(row.get("product_id", 0))
            warehouse_id = int(row.get("warehouse_id", 0))
            quantity = int(row.get("quantity", 0))

            if product_id > 0 and warehouse_id > 0 and quantity > 0:
                await InventoryService.stock_in(
                    db=db,
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    quantity=quantity,
                    reference_id="CSV-IMPORT",
                    user_id=user_id
                )
                imported_count += 1

        return {"imported_count": imported_count, "status": "Success"}
