"""SVG icon set inspired by Ant Design; no React or external icon package required."""

ICON_PATHS = {
    "overview": '<rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="5" rx="1.5"/><rect x="13" y="10" width="8" height="11" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/>',
    "sales": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 7-8"/><path d="M16 6h5v5"/>',
    "stores": '<path d="M3 10 5 3h14l2 7"/><path d="M4 10v11h16V10"/><path d="M9 21v-7h6v7"/>',
    "customers": '<circle cx="9" cy="8" r="4"/><path d="M2 21c0-3.9 3.1-7 7-7s7 3.1 7 7"/><path d="M16 4.5a4 4 0 0 1 0 7.1M18 14c2.4.9 4 3.2 4 6"/>',
    "risk": '<path d="M12 3 22 20H2L12 3Z"/><path d="M12 9v5M12 17h.01"/>',
    "reports": '<path d="M6 3h9l5 5v13H6z"/><path d="M15 3v5h5M9 13h8M9 17h8"/>',
    "revenue": '<path d="M4 19V5M4 19h17"/><path d="m7 15 4-4 3 3 6-7"/>',
    "profit": '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6"/>',
    "margin": '<circle cx="12" cy="12" r="9"/><path d="M8 15 16 9M8.5 8.5h.01M15.5 15.5h.01"/>',
    "trend": '<path d="M3 17 9 11l4 4 8-9"/><path d="M15 6h6v6"/>',
    "category": '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>',
    "discount": '<path d="m4 4 16 16M7 7h.01M17 17h.01"/><circle cx="7" cy="7" r="3"/><circle cx="17" cy="17" r="3"/>',
    "delivery": '<path d="M3 6h11v12H3zM14 10h4l3 3v5h-7z"/><circle cx="7.5" cy="18" r="1.5"/><circle cx="17.5" cy="18" r="1.5"/>',
    "alert": '<path d="M12 3 22 20H2L12 3Z"/><path d="M12 9v5M12 17h.01"/>',
    "data": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v7c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12v7c0 1.7 3.6 3 8 3s8-1.3 8-3v-7"/>',
}

def get_icon(name, color="#64748B", size=20, stroke_width=1.8):
    """Return inline SVG HTML."""
    paths = ICON_PATHS.get(name, '<circle cx="12" cy="12" r="8"/>')
    return (
        f'<span class="ant-icon" style="color:{color};width:{size}px;height:{size}px;'
        f'display:inline-flex;align-items:center;justify-content:center;flex:0 0 {size}px;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg></span>'
    )
