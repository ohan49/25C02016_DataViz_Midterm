"""Đọc, kiểm tra, làm sạch và tạo biến dẫn xuất từ dữ liệu bán lẻ."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path(__file__).parent / "data" / "urban_retail_sales_hcmc_2025_240.csv"

REQUIRED_COLUMNS = [
    "Transaction_ID", "Date", "Store", "Product_Category", "Product",
    "Customer_Type", "Payment_Method", "Quantity", "Unit_Price",
    "Discount", "Revenue", "Cost", "Profit"
]

@st.cache_data(show_spinner=False)
def load_data():
    """Tự động đọc dataset cố định trong thư mục data/ khi ứng dụng khởi chạy."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy dataset tại {DATA_PATH}. "
            "Hãy đặt file urban_retail_sales_hcmc_2025_240.csv vào thư mục data/."
        )
    df = pd.read_csv(DATA_PATH)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError("CSV thiếu cột bắt buộc: " + ", ".join(missing))

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    numeric_cols = [
        "Quantity", "Unit_Price", "Discount", "Revenue", "Cost",
        "Profit", "Customer_Rating", "Delivery_Days"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Month_Number"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    df["Profit_Margin"] = np.where(
        df["Revenue"].ne(0), df["Profit"] / df["Revenue"] * 100, np.nan
    )
    df["Is_Loss"] = df["Profit"] < 0

    # Gắn cờ bất thường trên toàn bộ dataset gốc trước khi áp dụng bộ lọc.
    features = ["Quantity", "Unit_Price", "Discount", "Revenue", "Cost", "Profit"]
    X = df[features].replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True))
    if len(df) >= 10:
        X_scaled = StandardScaler().fit_transform(X)
        model = IsolationForest(
            n_estimators=200, contamination=0.05, random_state=42
        )
        df["Anomaly_Label"] = model.fit_predict(X_scaled)
    else:
        df["Anomaly_Label"] = 1

    df["Anomaly_Status"] = df["Anomaly_Label"].map({
        1: "Thông thường",
        -1: "Bất thường tiềm năng"
    })
    return df


def filter_data(df, date_range, stores, categories, customers, payments):
    """Áp dụng các bộ lọc do người dùng chọn."""
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    else:
        start = pd.Timestamp(df["Date"].min().date())
        end = pd.Timestamp(df["Date"].max().date())

    mask = (
        df["Date"].between(start, end)
        & df["Store"].isin(stores)
        & df["Product_Category"].isin(categories)
        & df["Customer_Type"].isin(customers)
        & df["Payment_Method"].isin(payments)
    )
    return df.loc[mask].copy()
