"""
CarbonScope 2.0 - Data Loader Module
Reads and provides access to raw EDGAR 2026 workbooks and official report PDF.
Preserves original data intact without modifying source files.
"""

import os
import pandas as pd
import openpyxl
from typing import Dict, Any, List, Optional
try:
    import pypdf
except ImportError:
    pypdf = None

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

GHG_FILE = os.path.join(RAW_DATA_DIR, "EDGAR_2026_GHG_booklet_2026.xlsx")
FOSSIL_FILE = os.path.join(RAW_DATA_DIR, "EDGAR_2026_GHG_booklet_2026_fossilCO2only.xlsx")
PDF_FILE = os.path.join(RAW_DATA_DIR, "GHG_emissions_of_all_world_countries_booklet_2026report.pdf")


class EdgarDataLoader:
    """Encapsulates loading and accessing official EDGAR 2026 climate datasets."""

    def __init__(self, ghg_path: str = GHG_FILE, fossil_path: str = FOSSIL_FILE, pdf_path: str = PDF_FILE):
        self.ghg_path = ghg_path
        self.fossil_path = fossil_path
        self.pdf_path = pdf_path
        self._cache: Dict[str, pd.DataFrame] = {}

    def get_sheet_names(self, file_type: str = "ghg") -> List[str]:
        """Return available sheet names in the requested workbook."""
        target = self.ghg_path if file_type == "ghg" else self.fossil_path
        wb = openpyxl.load_workbook(target, read_only=True)
        names = wb.sheetnames
        wb.close()
        return names

    def load_sheet(self, sheet_name: str, file_type: str = "ghg", use_cache: bool = True) -> pd.DataFrame:
        """Load a specific sheet from the workbook with in-memory caching."""
        cache_key = f"{file_type}:{sheet_name}"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key].copy()

        target = self.ghg_path if file_type == "ghg" else self.fossil_path
        if not os.path.exists(target):
            raise FileNotFoundError(f"Workbook '{target}' does not exist.")

        df = pd.read_excel(target, sheet_name=sheet_name)
        if use_cache:
            self._cache[cache_key] = df
        return df.copy()

    def load_ghg_totals(self) -> pd.DataFrame:
        """Load total greenhouse gas emissions by country (Sheet: GHG_totals_by_country)."""
        return self.load_sheet("GHG_totals_by_country", file_type="ghg")

    def load_ghg_sectors(self) -> pd.DataFrame:
        """Load greenhouse gas emissions broken down by sector and country (Sheet: GHG_by_sector_and_country)."""
        return self.load_sheet("GHG_by_sector_and_country", file_type="ghg")

    def load_ghg_per_capita(self) -> pd.DataFrame:
        """Load per capita GHG emissions by country (Sheet: GHG_per_capita_by_country)."""
        return self.load_sheet("GHG_per_capita_by_country", file_type="ghg")

    def load_ghg_per_gdp(self) -> pd.DataFrame:
        """Load emission intensity per GDP (Sheet: GHG_per_GDP_by_country)."""
        return self.load_sheet("GHG_per_GDP_by_country", file_type="ghg")

    def load_lulucf_countries(self) -> pd.DataFrame:
        """Load Land Use, Land-Use Change, and Forestry emissions by country (Sheet: LULUCF_countries)."""
        return self.load_sheet("LULUCF_countries", file_type="ghg")

    def load_fossil_co2_totals(self) -> pd.DataFrame:
        """Load fossil CO2 totals by country (Sheet: fossil_CO2_totals_by_country)."""
        return self.load_sheet("fossil_CO2_totals_by_country", file_type="fossil")

    def load_fossil_co2_sectors(self) -> pd.DataFrame:
        """Load fossil CO2 emissions by sector and country (Sheet: fossil_CO2_by_sector_country_su)."""
        return self.load_sheet("fossil_CO2_by_sector_country_su", file_type="fossil")

    def load_pdf_report_metadata(self) -> Dict[str, Any]:
        """Extract metadata and introductory text from the official EDGAR 2026 report PDF."""
        if not os.path.exists(self.pdf_path) or pypdf is None:
            return {
                "available": False,
                "error": "PDF file missing or pypdf not installed.",
                "page_count": 0
            }

        try:
            reader = pypdf.PdfReader(self.pdf_path)
            page_count = len(reader.pages)
            info = reader.metadata or {}

            # Extract title / summary from first 3 pages
            sample_text = ""
            for p_num in range(min(3, page_count)):
                sample_text += f"\n--- Page {p_num + 1} ---\n" + reader.pages[p_num].extract_text()[:600]

            return {
                "available": True,
                "filepath": self.pdf_path,
                "filename": os.path.basename(self.pdf_path),
                "page_count": page_count,
                "title": info.get("/Title", "GHG emissions of all world countries - 2026 Report"),
                "author": info.get("/Author", "European Commission, Joint Research Centre (JRC)"),
                "sample_text": sample_text.strip()
            }
        except Exception as e:
            return {"available": False, "error": str(e), "page_count": 0}

    def get_summary_inventory(self) -> Dict[str, Any]:
        """Produce an inventory summary of all loaded sheets, row counts, and column counts."""
        ghg_sheets = self.get_sheet_names("ghg")
        fossil_sheets = self.get_sheet_names("fossil")
        pdf_meta = self.load_pdf_report_metadata()

        return {
            "ghg_workbook": {
                "filename": os.path.basename(self.ghg_path),
                "sheets": ghg_sheets,
                "sheet_count": len(ghg_sheets)
            },
            "fossil_workbook": {
                "filename": os.path.basename(self.fossil_path),
                "sheets": fossil_sheets,
                "sheet_count": len(fossil_sheets)
            },
            "report_pdf": pdf_meta
        }


# Global singleton instance for clean access
loader = EdgarDataLoader()

if __name__ == "__main__":
    print("Testing EdgarDataLoader...")
    inv = loader.get_summary_inventory()
    print("GHG sheets:", inv["ghg_workbook"]["sheets"])
    print("Fossil sheets:", inv["fossil_workbook"]["sheets"])
    print("PDF page count:", inv["report_pdf"]["page_count"])
    df_t = loader.load_ghg_totals()
    print("GHG totals shape:", df_t.shape)

