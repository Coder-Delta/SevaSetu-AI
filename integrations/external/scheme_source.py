import logging
import pandas as pd
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class SchemeSourceCSV:
    """
    Loads government scheme details from local CSV dataset file.
    """
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Scheme dataset CSV not found at {csv_path}")

    def load_schemes(self) -> List[Dict]:
        """
        Parse CSV entries and map to application Scheme model properties.
        """
        logger.info(f"Loading scheme dataset from {self.csv_path}...")
        df = pd.read_csv(self.csv_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Replace NaN values with empty strings or None
        df = df.where(pd.notnull(df), None)
        
        schemes = []
        for index, row in df.iterrows():
            # Mandatory fields mapping
            scheme_name = row.get("scheme_name")
            slug = row.get("slug")
            
            # If slug is not provided, generate from index or scheme_name
            if not scheme_name:
                continue
                
            if not slug:
                slug = f"scheme-{index}"
                
            scheme = {
                "scheme_name": str(scheme_name),
                "slug": str(slug),
                "details": str(row.get("details", "")) if row.get("details") else "",
                "benefits": str(row.get("benefits", "")) if row.get("benefits") else "",
                "eligibility": str(row.get("eligibility", "")) if row.get("eligibility") else "",
                "application_process": str(row.get("application", "")) if row.get("application") else "",
                "documents_required": str(row.get("documents", "")) if row.get("documents") else "",
                "level": str(row.get("level", "Central")) if row.get("level") else "Central",
                "scheme_category": str(row.get("schemeCategory", "")) if row.get("schemeCategory") else "",
                "tags": str(row.get("tags", "")) if row.get("tags") else ""
            }
            schemes.append(scheme)
            
        logger.info(f"Loaded {len(schemes)} schemes from CSV")
        return schemes

class SchemeSourceStub:
    """
    Mock external API integration fetching schemes.
    """
    async def fetch_schemes(self) -> List[Dict]:
        logger.warning("STUB: SchemeSourceStub.fetch_schemes() called — returning empty list")
        return []
