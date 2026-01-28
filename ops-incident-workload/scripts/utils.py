"""
Utility functions for BO Workload Performance Report.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple


def load_excel_data(file_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load incident data and SLA criteria from Excel file.
    
    Args:
        file_path: Path to the Excel file
    
    Returns:
        Tuple of (data DataFrame, sla_criteria DataFrame)
    """
    # Load SLA criteria
    sla_df = pd.read_excel(file_path, sheet_name="SLA_Criteria")
    
    # Load incident data
    data_df = pd.read_excel(file_path, sheet_name="Data")
    
    return data_df, sla_df


def clean_data(df: pd.DataFrame, excluded_resolvers: List[str]) -> pd.DataFrame:
    """
    Clean and preprocess incident data.
    
    Args:
        df: Raw incident DataFrame
        excluded_resolvers: List of resolver names to exclude
    
    Returns:
        Cleaned DataFrame
    """
    # Make a copy
    df = df.copy()
    
    # Remove excluded resolvers
    df = df[~df["Resolver"].isin(excluded_resolvers)]
    df = df[df["Resolver"].notna()]
    df = df[df["Resolver"].str.strip() != ""]
    
    # Remove invalid resolution times
    if "Resolution Time(m)" in df.columns:
        df = df[df["Resolution Time(m)"] >= 0]
    
    # Convert date columns
    date_columns = ["Begin Date", "Resolution Date", "End Date"]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    
    # Add computed columns
    if "Resolution Time(m)" in df.columns:
        df["Resolution_Hours"] = df["Resolution Time(m)"] / 60
    
    # Extract time features
    if "Begin Date" in df.columns:
        df["DayOfWeek"] = df["Begin Date"].dt.dayofweek
        df["Hour"] = df["Begin Date"].dt.hour
        df["Month"] = df["Begin Date"].dt.to_period("M")
    
    return df


def calculate_gini_coefficient(values: np.ndarray) -> float:
    """
    Calculate Gini coefficient for measuring inequality.
    
    Args:
        values: Array of values (e.g., ticket counts per resolver)
    
    Returns:
        Gini coefficient (0 = perfect equality, 1 = complete inequality)
    """
    values = np.array(values, dtype=float)
    values = values[values > 0]  # Remove zeros
    
    if len(values) == 0:
        return 0.0
    
    # Sort values
    values = np.sort(values)
    n = len(values)
    
    # Calculate Gini
    cumsum = np.cumsum(values)
    gini = (2 * np.sum((np.arange(1, n + 1) * values))) / (n * np.sum(values)) - (n + 1) / n
    
    return max(0, min(1, gini))  # Clamp to [0, 1]


def calculate_herfindahl_index(values: np.ndarray) -> float:
    """
    Calculate Herfindahl-Hirschman Index for measuring concentration.
    
    Args:
        values: Array of counts (e.g., tickets per category)
    
    Returns:
        HHI value (0 = diverse, 1 = concentrated in one category)
    """
    values = np.array(values, dtype=float)
    total = values.sum()
    
    if total == 0:
        return 0.0
    
    shares = values / total
    hhi = np.sum(shares ** 2)
    
    return hhi


def format_duration(hours: float) -> str:
    """
    Format duration in hours to human-readable string.
    
    Args:
        hours: Duration in hours
    
    Returns:
        Formatted string (e.g., "2d 5h" or "3.5h")
    """
    if pd.isna(hours) or hours < 0:
        return "N/A"
    
    if hours >= 24:
        days = int(hours // 24)
        remaining_hours = hours % 24
        return f"{days}d {remaining_hours:.1f}h"
    else:
        return f"{hours:.1f}h"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format value as percentage string.
    
    Args:
        value: Value between 0 and 1
        decimal_places: Number of decimal places
    
    Returns:
        Formatted percentage string (e.g., "85.5%")
    """
    if pd.isna(value):
        return "N/A"
    
    return f"{value * 100:.{decimal_places}f}%"


def get_date_range(df: pd.DataFrame, date_column: str = "Begin Date") -> Tuple[datetime, datetime]:
    """
    Get the date range from a DataFrame.
    
    Args:
        df: DataFrame with date column
        date_column: Name of the date column
    
    Returns:
        Tuple of (start_date, end_date)
    """
    if date_column not in df.columns:
        return datetime.now(), datetime.now()
    
    dates = df[date_column].dropna()
    
    if len(dates) == 0:
        return datetime.now(), datetime.now()
    
    return dates.min().to_pydatetime(), dates.max().to_pydatetime()


def calculate_trend(current: float, previous: float) -> Tuple[float, str]:
    """
    Calculate trend between two values.
    
    Args:
        current: Current period value
        previous: Previous period value
    
    Returns:
        Tuple of (change percentage, trend indicator)
    """
    if previous == 0:
        if current == 0:
            return 0.0, "→"
        return float("inf"), "↑"
    
    change = (current - previous) / previous
    
    if change > 0.05:
        indicator = "↑"
    elif change < -0.05:
        indicator = "↓"
    else:
        indicator = "→"
    
    return change, indicator


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails
    
    Returns:
        Division result or default
    """
    if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
        return default
    return numerator / denominator
