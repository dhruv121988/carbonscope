"""
CarbonScope 2.0 - Data Preprocessing: Validation Engine
Validates schemas, data types, physical constraints, and identifies anomalies
in raw and processed EDGAR climate datasets.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple


class DataValidator:
    """Rigorous scientific data validator for EDGAR climate observations."""

    @staticmethod
    def validate_totals_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate schema of raw GHG totals sheet."""
        issues = []
        expected_id_cols = ['EDGAR Country Code', 'Country']
        for col in expected_id_cols:
            if col not in df.columns:
                issues.append(f"Missing required identifier column: '{col}'")

        year_cols = [c for c in df.columns if str(c).isdigit()]
        if len(year_cols) < 50:
            issues.append(f"Expected at least 50 continuous year columns, found {len(year_cols)}")

        # Check for 1970 and 2025 boundary years
        if 1970 not in year_cols and '1970' not in year_cols:
            issues.append("Expected start year 1970 missing from dataset.")
        if 2025 not in year_cols and '2025' not in year_cols:
            issues.append("Expected terminal year 2025 missing from dataset.")

        is_valid = len(issues) == 0
        return is_valid, issues

    @staticmethod
    def validate_sector_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate schema of raw GHG by sector sheet."""
        issues = []
        expected_cols = ['Substance', 'Sector', 'EDGAR Country Code', 'Country']
        for col in expected_cols:
            if col not in df.columns:
                issues.append(f"Missing required sector breakdown column: '{col}'")

        year_cols = [c for c in df.columns if str(c).isdigit()]
        if len(year_cols) < 50:
            issues.append(f"Sector sheet has fewer year columns than expected: {len(year_cols)}")

        return len(issues) == 0, issues

    @staticmethod
    def validate_numeric_ranges(df: pd.DataFrame, value_col: str = "Emissions", allow_negative: bool = False) -> Dict[str, Any]:
        """
        Validate physical plausibility of emissions values.
        Gross territorial GHG emissions must be strictly non-negative (>= 0).
        Negative emissions are only scientifically valid for carbon sink activities (e.g. LULUCF afforestation).
        """
        if value_col not in df.columns:
            return {"valid": False, "error": f"Column '{value_col}' not found."}

        vals = pd.to_numeric(df[value_col], errors='coerce')
        nan_count = vals.isnull().sum()
        inf_count = np.isinf(vals).sum()

        negatives = vals[vals < 0]
        negative_count = len(negatives)

        is_physically_sound = True
        notes = []

        if inf_count > 0:
            is_physically_sound = False
            notes.append(f"Found {inf_count} infinite numeric values.")

        if not allow_negative and negative_count > 0:
            is_physically_sound = False
            notes.append(f"Found {negative_count} negative emission observations in non-sink categories (min: {negatives.min()}).")

        return {
            "valid": is_physically_sound,
            "nan_count": int(nan_count),
            "inf_count": int(inf_count),
            "negative_count": int(negative_count),
            "min_value": float(vals.min()) if len(vals.dropna()) > 0 else None,
            "max_value": float(vals.max()) if len(vals.dropna()) > 0 else None,
            "mean_value": float(vals.mean()) if len(vals.dropna()) > 0 else None,
            "notes": notes
        }

    @staticmethod
    def detect_suspicious_jumps(series: pd.Series, max_annual_multiplier: float = 5.0) -> List[int]:
        """
        Detect sudden non-physical multi-fold spikes in historical time series
        that might indicate data transposition errors or sensor corruption.
        """
        suspicious_indices = []
        pct_change = series.pct_change().abs()
        spikes = pct_change[pct_change > max_annual_multiplier]
        return spikes.index.tolist()


validator = DataValidator()

