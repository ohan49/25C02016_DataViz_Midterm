"""Các hàm tiện ích dùng chung cho dashboard."""
import html

import plotly.graph_objects as go
import streamlit as st
from config import COLORS
from ant_icons import get_icon


def money(value, decimals=2):
    return f"{value / 1_000_000:,.{decimals}f} triệu ₫"


def money_short(value, decimals=1):
    return f"{value / 1_000_000:,.{decimals}f}M ₫"


def percent(value):
    return f"{value:.2f}%"


def section_title(title, subtitle=None, icon=None):
    icon_html = get_icon(icon, "#2675E8", 22) if icon else ""
    st.markdown(
        f'<div class="section-heading">{icon_html}<div><div class="section-title">{title}</div>'
        f'<div class="section-sub">{subtitle or ""}</div></div></div>',
        unsafe_allow_html=True,
    )


def insight_card(number, tag, title, description):
    """Insight ngắn, ưu tiên kết luận thay vì chỉ mô tả loại biểu đồ."""
    st.markdown(
        f'<div class="insight"><span class="tag">INSIGHT {number:02d} · {html.escape(str(tag))}</span>'
        f'<h3>{html.escape(str(title))}</h3><p>{html.escape(str(description))}</p></div>',
        unsafe_allow_html=True,
    )


def analytical_insight(
    tag, title, finding, evidence, implication, chart_reason=None, evaluation=None
):
    """Khối insight có phát hiện, bằng chứng, lựa chọn biểu đồ và đánh giá."""
    parts = [
        f'<div class="insight"><span class="tag">{html.escape(str(tag))}</span>',
        f'<h3>{html.escape(str(title))}</h3>',
        f'<p><b>Phát hiện:</b> {html.escape(str(finding))}</p>',
        f'<p><b>Bằng chứng:</b> {html.escape(str(evidence))}</p>',
        f'<p><b>Vì sao chọn biểu đồ:</b> {html.escape(str(chart_reason or "Biểu đồ được chọn để thể hiện trực tiếp mối quan hệ cần trả lời trong câu hỏi phân tích."))}</p>',
        f'<p><b>Đánh giá:</b> {html.escape(str(evaluation or "Kết luận chỉ áp dụng cho dữ liệu đang chọn; cần xem xét cỡ mẫu và giới hạn dữ liệu trước khi khái quát."))}</p>',
        f'<p><b>Hàm ý:</b> {html.escape(str(implication))}</p></div>',
    ]
    st.markdown("".join(parts), unsafe_allow_html=True)


def chart_layout(fig, height=360, showlegend=True, y_title=None, x_title=None):
    fig.update_layout(
        template="plotly_white", height=height,
        margin=dict(l=18, r=24, t=55, b=28),
        font=dict(family="DM Sans, sans-serif", color="#26364D", size=11),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10)),
        showlegend=showlegend, hoverlabel=dict(bgcolor=COLORS["navy"], font_color="white"),
        yaxis_title=y_title, xaxis_title=x_title,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#E7EDF6", automargin=True)
    fig.update_yaxes(gridcolor="#EDF1F7", zeroline=False, automargin=True)
    return fig


def empty_chart(message="Không có dữ liệu phù hợp với bộ lọc."):
    fig = go.Figure()
    fig.add_annotation(text=message, x=.5, y=.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(size=13, color=COLORS["muted"]))
    fig.update_layout(height=280, template="plotly_white", margin=dict(l=10, r=10, t=15, b=10))
    return fig


def correlation_text(df, x, y):
    """Trả về Pearson, p-value, Spearman và cỡ mẫu trên các cặp hợp lệ."""
    valid = df[[x, y]].dropna()
    if len(valid) < 3 or valid[x].nunique() < 2 or valid[y].nunique() < 2:
        return None
    from scipy.stats import pearsonr, spearmanr
    pearson_r, p_value = pearsonr(valid[x], valid[y])
    spearman_r, _ = spearmanr(valid[x], valid[y])
    return pearson_r, p_value, spearman_r, len(valid)
