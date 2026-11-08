"""Điểm khởi chạy của Urban Retail Analytics."""
import streamlit as st

from ant_icons import get_icon
from config import APP_TITLE, APP_ICON, NAVIGATION, NAV_ICONS
from data_loader import load_data, filter_data
from styles import load_css, render_hero, render_kpis
from views import overview, sales_products, stores, customer_experience, risk, reports


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)
load_css()


def reset_filters(defaults):
    """Đưa toàn bộ bộ lọc về giá trị mặc định."""
    st.session_state["filter_date_range"] = defaults["date_range"]
    st.session_state["filter_stores"] = defaults["stores"]
    st.session_state["filter_categories"] = defaults["categories"]
    st.session_state["filter_customers"] = defaults["customers"]
    st.session_state["filter_payments"] = defaults["payments"]


try:
    df_all = load_data()
except Exception as exc:
    st.error(f"Không thể đọc dữ liệu: {exc}")
    st.stop()

if df_all.empty or df_all["Date"].dropna().empty:
    st.error("Dataset không có ngày giao dịch hợp lệ.")
    st.stop()

min_date = df_all["Date"].min().date()
max_date = df_all["Date"].max().date()
default_stores = sorted(df_all["Store"].dropna().unique().tolist())
default_categories = sorted(df_all["Product_Category"].dropna().unique().tolist())
default_customers = sorted(df_all["Customer_Type"].dropna().unique().tolist())
default_payments = sorted(df_all["Payment_Method"].dropna().unique().tolist())

filter_defaults = {
    "date_range": (min_date, max_date),
    "stores": default_stores,
    "categories": default_categories,
    "customers": default_customers,
    "payments": default_payments,
}

for key, value in {
    "filter_date_range": filter_defaults["date_range"],
    "filter_stores": default_stores,
    "filter_categories": default_categories,
    "filter_customers": default_customers,
    "filter_payments": default_payments,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

if st.session_state.get("selected_page") not in NAVIGATION:
    st.session_state["selected_page"] = next(iter(NAVIGATION))


with st.sidebar:
    st.markdown(
        f'<div class="brand-block"><div class="brand-row">'
        f'<div class="brand-mark">{get_icon("overview", "#55D6D0", 25)}</div>'
        f'<div class="brand-name">URBAN RETAIL<br>ANALYTICS</div></div>'
        f'<div class="brand-caption">INSIGHTS · GROWTH · SUCCESS</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-label">WORKSPACE</div>', unsafe_allow_html=True)

    for label, page_key in NAVIGATION.items():
        active = st.session_state["selected_page"] == label
        icon_key = NAV_ICONS[page_key]
        icon_color = "#FFFFFF" if active else "#AFC0D9"
        icon_col, button_col = st.columns([0.16, 0.84])
        with icon_col:
            st.markdown(get_icon(icon_key, icon_color, 19), unsafe_allow_html=True)
        with button_col:
            if st.button(
                label,
                key=f"nav_{page_key}",
                type="primary" if active else "secondary",
                use_container_width=True,
            ):
                st.session_state["selected_page"] = label
                st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-section-label">GLOBAL FILTERS</div>'
        '<div class="sidebar-filter-note">Các bộ lọc này được áp dụng đồng bộ trên tất cả trang.</div>',
        unsafe_allow_html=True,
    )

    date_range = st.date_input(
        "Khoảng thời gian", min_value=min_date, max_value=max_date,
        key="filter_date_range",
    )
    store_filter = st.multiselect(
        "Cửa hàng", default_stores, key="filter_stores", placeholder="Chọn cửa hàng",
    )
    categories = st.multiselect(
        "Danh mục sản phẩm", default_categories, key="filter_categories", placeholder="Chọn danh mục",
    )
    customers = st.multiselect(
        "Nhóm khách hàng", default_customers, key="filter_customers", placeholder="Chọn nhóm khách hàng",
    )
    payments = st.multiselect(
        "Phương thức thanh toán", default_payments, key="filter_payments", placeholder="Chọn phương thức",
    )

    st.button(
        "↻ Đặt lại bộ lọc", key="reset_all_filters",
        type="secondary", use_container_width=True,
        on_click=reset_filters, args=(filter_defaults,),
    )
    st.markdown(
        f'<div class="sidebar-data-status"><span class="status-dot"></span>'
        f'<span>{len(df_all):,} giao dịch · HCMC · 2025</span></div>',
        unsafe_allow_html=True,
    )


df = filter_data(df_all, date_range, store_filter, categories, customers, payments)
selected_label = st.session_state["selected_page"]
page_key = NAVIGATION[selected_label]

render_hero(
    APP_TITLE,
    "5 câu hỏi phân tích · 5 phát hiện có bằng chứng trực quan · Hàm ý kinh doanh từ dữ liệu bán lẻ TP. Hồ Chí Minh.",
)

if df.empty:
    st.warning("Không có giao dịch phù hợp với bộ lọc hiện tại. Hãy điều chỉnh bộ lọc ở thanh bên.")
    st.stop()

render_kpis(df)

if page_key == "overview":
    overview.render(df)
elif page_key == "sales_products":
    sales_products.render(df)
elif page_key == "stores":
    stores.render(df)
elif page_key == "customer_experience":
    customer_experience.render(df)
elif page_key == "risk":
    risk.render(df)
elif page_key == "reports":
    reports.render(df, df_all)

st.markdown(
    '<div class="app-footer">URBAN RETAIL ANALYTICS · INTERACTIVE DATA VISUALIZATION · HCMC 2025</div>',
    unsafe_allow_html=True,
)
