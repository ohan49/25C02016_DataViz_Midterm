"""CSS và thành phần giao diện."""
import streamlit as st


def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
    .stApp{background:#F4F7FC;color:#15243B}
    .block-container{padding-top:1.25rem;padding-bottom:2.5rem;max-width:1600px}
    [data-testid="stSidebar"]{background:linear-gradient(180deg,#10264B 0%,#0B1B35 100%);border-right:1px solid rgba(255,255,255,.06)}
    [data-testid="stSidebar"]>div:first-child{padding-top:1.1rem}
    [data-testid="stSidebar"] *{font-family:'DM Sans',sans-serif}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] label{color:#EAF1FC!important}
    .brand-block{padding:10px 9px 22px}
    .brand-row{display:flex;align-items:center;gap:12px}
    .brand-mark{width:44px;height:44px;border-radius:14px;display:flex;align-items:center;justify-content:center;color:#55D6D0;background:rgba(55,190,204,.12);border:1px solid rgba(85,214,208,.2)}
    .brand-name{font-size:21px;line-height:1.12;font-weight:800;color:#fff}
    .brand-caption{font-size:9px;letter-spacing:1.35px;color:#9EB3D2;margin:9px 0 0 56px;font-weight:700}
    .sidebar-section-label{font-size:10px;letter-spacing:1.5px;font-weight:800;color:#8299BB;padding:8px 9px 9px}
    .sidebar-filter-note{color:#AFC0D9;font-size:11px;line-height:1.45;padding:0 9px 12px}
    .sidebar-divider{height:1px;background:rgba(220,233,255,.13);margin:18px 4px 13px}
    .sidebar-data-status{display:flex;align-items:center;gap:8px;margin:18px 7px 5px;padding:11px 10px;border-radius:10px;background:rgba(255,255,255,.07);color:#C5D4E9;font-size:10px}
    .status-dot{width:7px;height:7px;border-radius:50%;background:#25C69A;display:inline-block}
    [data-testid="stSidebar"] div.stButton{margin:0 0 5px}
    [data-testid="stSidebar"] div.stButton>button{min-height:42px;border-radius:10px;border:1px solid transparent;padding:8px 12px;text-align:left;font-size:12px;font-weight:650;color:#DCE7F7;background:transparent;box-shadow:none}
    [data-testid="stSidebar"] div.stButton>button:hover{color:#fff;background:rgba(255,255,255,.09);border-color:rgba(255,255,255,.10)}
    [data-testid="stSidebar"] div.stButton>button[kind="primary"]{color:#fff;background:linear-gradient(100deg,#1769D2,#2587F5);border:1px solid rgba(116,184,255,.28);box-shadow:0 7px 18px rgba(0,92,204,.20)}
    [data-testid="stSidebar"] div.stButton>button p{font-weight:650}
    [data-testid="stSidebar"] [data-testid="stMultiSelect"],[data-testid="stSidebar"] [data-testid="stDateInput"]{margin-bottom:7px}
    [data-testid="stSidebar"] [data-baseweb="select"]>div,[data-testid="stSidebar"] [data-testid="stDateInput"] input{background:rgba(255,255,255,.09)!important;border:1px solid rgba(220,233,255,.16)!important;border-radius:9px!important}
    [data-testid="stSidebar"] [data-baseweb="tag"]{background:#1F69B9!important;border-radius:6px!important}
    .hero{background:linear-gradient(110deg,#0D2245,#1C5697);border-radius:20px;padding:25px 30px;color:#fff;margin-bottom:18px;box-shadow:0 12px 30px rgba(25,61,112,.13)}
    .hero h1{font-size:29px;font-weight:800;margin:0 0 5px;color:#fff}
    .hero p{font-size:14px;color:#D9E7FA;margin:0}
    .eyebrow{font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#A9C7F5;font-weight:700;margin-bottom:7px}
    .kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:0 0 18px}
    .kpi{background:#fff;border:1px solid #E7EDF6;border-radius:15px;padding:15px 16px;min-height:116px;box-shadow:0 4px 15px rgba(28,56,100,.035)}
    .kpi-top{display:flex;align-items:center;gap:8px;margin-bottom:8px}
    .kpi-label{font-size:11px;color:#738198;font-weight:700;letter-spacing:.3px}
    .kpi-value{font-size:23px;color:#14294A;font-weight:800;line-height:1.15}
    .kpi-note{font-size:10px;color:#8491A5;margin-top:7px}
    .section-heading{display:flex;align-items:flex-start;gap:10px;margin:5px 0 12px}
    .section-heading>.ant-icon{margin-top:2px}
    .section-title{font-size:19px;font-weight:800;color:#172C4D;margin:0 0 2px}
    .section-sub{font-size:12px;color:#7A879A;margin:0}
    .insight{background:#fff;border:1px solid #E7EDF6;border-radius:15px;padding:16px 18px;margin-bottom:13px;box-shadow:0 4px 15px rgba(28,56,100,.025)}
    .insight h3{font-size:15px;color:#172C4D;margin:0 0 7px}
    .insight p{font-size:12px;color:#536177;line-height:1.55;margin:4px 0}
    .tag{display:inline-block;background:#EAF2FF;color:#1D63C5;border-radius:20px;padding:4px 9px;font-size:10px;font-weight:700;margin-bottom:8px}
    div[data-testid="stMetric"]{background:#fff;border:1px solid #E7EDF6;padding:13px 15px;border-radius:13px}
    .app-footer{text-align:center;color:#91A0B4;font-size:10px;padding:22px 0 4px;letter-spacing:.5px}
    @media(max-width:900px){.kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
    hr{border-color:#E7EDF6} footer{visibility:hidden}
    </style>
    """, unsafe_allow_html=True)


def render_hero(title, subtitle):
    st.markdown(
        f'<div class="hero"><div class="eyebrow">INTERACTIVE BUSINESS INTELLIGENCE · HCMC 2025</div>'
        f'<h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def render_kpis(df):
    from utils import money_short
    from ant_icons import get_icon
    revenue=df["Revenue"].sum()
    profit=df["Profit"].sum()
    cost=df["Cost"].sum()
    n_tx=df["Transaction_ID"].nunique()
    qty=df["Quantity"].sum()
    margin=profit/revenue*100 if revenue else 0
    avg_tx=revenue/n_tx if n_tx else 0
    items=[
        ("revenue","TỔNG DOANH THU",money_short(revenue),f"{n_tx:,} giao dịch","#2675E8"),
        ("profit","TỔNG LỢI NHUẬN",money_short(profit),f"Giá vốn {money_short(cost)}","#13A98B"),
        ("data","SẢN PHẨM ĐÃ BÁN",f"{qty:,.0f}",f"{n_tx:,} giao dịch","#8065E8"),
        ("margin","BIÊN LỢI NHUẬN",f"{margin:.2f}%",f"Giá trị đơn TB {money_short(avg_tx)}","#E59A24"),
    ]
    cards=[]
    for icon,label,value,note,color in items:
        cards.append(
            f'<div class="kpi"><div class="kpi-top">{get_icon(icon,color,19)}'
            f'<span class="kpi-label">{label}</span></div><div class="kpi-value">{value}</div>'
            f'<div class="kpi-note">{note}</div></div>'
        )
    st.markdown('<div class="kpi-grid">'+''.join(cards)+'</div>',unsafe_allow_html=True)
