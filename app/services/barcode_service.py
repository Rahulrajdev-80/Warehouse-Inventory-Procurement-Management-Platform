import io
import barcode
from barcode.writer import ImageWriter, SVGWriter

class BarcodeService:
    @staticmethod
    def generate_sku_barcode_svg(sku: str) -> str:
        """Generate SVG barcode representation for SKU"""
        try:
            code128 = barcode.get('code128', sku, writer=SVGWriter())
            fp = io.BytesIO()
            code128.write(fp)
            return fp.getvalue().decode('utf-8')
        except Exception:
            # Fallback simple SVG representation
            return f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="80"><text x="10" y="40" font-family="monospace">{sku}</text></svg>'
