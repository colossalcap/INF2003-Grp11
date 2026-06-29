"""
============================================================
INF2003 Group 11 — ER Diagram Generator
Generates a high-resolution ER diagram image for the final report.
============================================================
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc
import matplotlib.lines as mlines
import numpy as np

OUTPUT_PATH = "c:/Users/tdmca/OneDrive/Desktop/Database/INF2003-Grp11/docs/ER_Diagram.png"

# ── Color Scheme ──────────────────────────────────────────
PG_COLOR = '#1976D2'       # Blue for PostgreSQL tables
PG_HEADER = '#0D47A1'      # Dark blue for headers
MONGO_COLOR = '#2E7D32'    # Green for MongoDB collections
MONGO_HEADER = '#1B5E20'   # Dark green
TRIGGER_COLOR = '#E65100'  # Orange for triggers
CDC_COLOR = '#7B1FA2'      # Purple for CDC
BG_COLOR = '#FAFAFA'       # Light background
TEXT_COLOR = '#212121'      # Almost black

# ── Table Definitions ─────────────────────────────────────
PG_TABLES = [
    ("users", [
        "PK user_id       INT",
        "   username      VARCHAR(50)",
        "   email         VARCHAR(100)",
        "   password_hash VARCHAR(255)",
        "   display_name  VARCHAR(100)",
        "   role          VARCHAR(20)",
        "   created_at    TIMESTAMP",
    ]),
    ("customers", [
        "PK customer_id   UUID",
        "   registration_date TIMESTAMP",
        "   country_code  VARCHAR(3)",
        "   opt_in_status BOOLEAN",
    ]),
    ("products", [
        "PK product_id    VARCHAR(50)",
        "   category      VARCHAR(100)",
        "   unit_price    DOUBLE PREC.",
        "   stock_quantity INTEGER",
        "CHECK (stock_quantity >= 0)",
    ]),
    ("orders", [
        "PK order_id      UUID",
        "FK customer_id   UUID",
        "   order_date    TIMESTAMP",
        "   total_amount  DOUBLE PREC.",
        "   status        VARCHAR(20)",
    ]),
    ("order_items", [
        "PK item_id       SERIAL",
        "FK order_id      UUID",
        "FK product_id    VARCHAR(50)",
        "   quantity      INTEGER",
        "CHECK (quantity > 0)",
    ]),
    ("outbox", [
        "PK event_id      SERIAL",
        "   aggregate_id  VARCHAR(255)",
        "   event_type    VARCHAR(100)",
        "   payload       JSONB",
        "   created_at    TIMESTAMP",
        "   processed     BOOLEAN",
    ]),
    ("order_audit_log", [
        "PK audit_id      SERIAL",
        "FK order_id      UUID",
        "   changed_by    VARCHAR(50)",
        "   field_name    VARCHAR(100)",
        "   old_value     TEXT",
        "   new_value     TEXT",
        "   changed_at    TIMESTAMP",
    ]),
    ("alerts", [
        "PK alert_id      SERIAL",
        "   customer_id   UUID",
        "   message       TEXT",
        "   alert_type    VARCHAR(50)",
        "   created_at    TIMESTAMP",
        "   acknowledged  BOOLEAN",
    ]),
]

MONGO_COLLECTIONS = [
    ("user_sessions\n(Bucket Pattern)", [
        "_id              ObjectId",
        "customer_id      String",
        "session_id       String  (unique)",
        "start_time       ISODate",
        "end_time         ISODate  (TTL: 30d)",
        "event_count      Integer  ($inc)",
        "flagged          Boolean",
        "events[]                       ($push)",
        "  · action_type    String",
        "  · product_id     String",
        "  · timestamp      ISODate",
    ]),
    ("session_stats\n(Computed Pattern)", [
        "session_id       String  (unique)",
        "customer_id      String",
        "total_events     Integer",
        "page_views       Integer",
        "add_to_carts     Integer",
        "checkouts        Integer",
        "purchases        Integer",
        "duration_seconds Integer",
    ]),
    ("customer_order_summary\n(CDC Target)", [
        "customer_id      String  (unique)",
        "total_orders     Integer  ($inc)",
        "total_spent      Float    ($inc)",
        "last_order_date  ISODate",
        "last_updated     ISODate",
    ]),
    ("funnel_metrics\n(Cached Pattern)", [
        "stage            String",
        "count            Integer",
        "conversion_rate  Float",
        "computed_at      ISODate",
    ]),
]

# ── Layout Configuration ──────────────────────────────────
BOX_W = 3.6     # Table box width
ROW_H = 0.28    # Row height
HEADER_H = 0.45 # Header height
PG_X_START = 1.0
MONGO_X_START = 20.0

# PostgreSQL table positions (x, y) - arranged in ER layout
pg_positions = {
    "users":             (1.5, 14.5),
    "customers":         (1.5, 11.5),
    "products":          (7.5, 14.5),
    "orders":            (1.5, 8.0),
    "order_items":       (7.5, 8.0),
    "outbox":            (13.5, 11.5),
    "order_audit_log":   (13.5, 8.0),
    "alerts":            (13.5, 14.5),
}

mongo_positions = {
    "user_sessions\n(Bucket Pattern)":           (20.5, 13.5),
    "session_stats\n(Computed Pattern)":          (26.0, 13.5),
    "customer_order_summary\n(CDC Target)":       (20.5, 7.5),
    "funnel_metrics\n(Cached Pattern)":           (26.0, 7.5),
}

# ── Helper Functions ──────────────────────────────────────

def draw_table_box(ax, name, columns, x, y, header_color, body_color):
    """Draw a table as a box with header and rows."""
    n_rows = len(columns)
    total_h = HEADER_H + n_rows * ROW_H

    # Body background
    body = FancyBboxPatch(
        (x, y), BOX_W, total_h,
        boxstyle="round,pad=0.05", edgecolor=body_color, facecolor='white',
        linewidth=1.2, zorder=2
    )
    ax.add_patch(body)

    # Header
    header = FancyBboxPatch(
        (x, y + total_h - HEADER_H), BOX_W, HEADER_H,
        boxstyle="round,pad=0.05", edgecolor=header_color, facecolor=header_color,
        linewidth=1.2, zorder=3
    )
    ax.add_patch(header)

    # Header text
    ax.text(x + BOX_W/2, y + total_h - HEADER_H/2, name,
            ha='center', va='center', fontsize=7.5, fontweight='bold',
            color='white', zorder=4, fontfamily='monospace')

    # Separator line under header
    ax.plot([x + 0.1, x + BOX_W - 0.1],
            [y + total_h - HEADER_H, y + total_h - HEADER_H],
            color=header_color, linewidth=0.8, zorder=4)

    # Column rows
    for i, col in enumerate(columns):
        cy = y + total_h - HEADER_H - (i + 0.5) * ROW_H - 0.02
        is_pk = col.strip().startswith("PK")
        is_fk = col.strip().startswith("FK")
        is_check = col.strip().startswith("CHECK")
        color = TEXT_COLOR
        weight = 'normal'
        size = 6.5
        if is_pk:
            weight = 'bold'
            size = 6.5
        elif is_fk:
            color = '#E65100'
            size = 6.5
        elif is_check:
            color = '#616161'
            size = 6.0

        ax.text(x + BOX_W/2, cy, col, ha='center', va='center',
                fontsize=size, fontweight=weight, color=color,
                zorder=4, fontfamily='monospace')

    return x + BOX_W/2, y + total_h  # Return center-top for arrow connections


def draw_arrow(ax, x1, y1, x2, y2, color='#757575', style='solid', label=''):
    """Draw a relationship arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5,
                               connectionstyle='arc3,rad=0', linestyle=style),
                zorder=1)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.2, my - 0.15, label, fontsize=7, color=color,
                fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                         edgecolor='none', alpha=0.8))


def draw_label_box(ax, x, y, text, color, fontsize=8):
    """Draw a small labeled box."""
    ax.text(x, y, text, fontsize=fontsize, fontweight='bold', color='white',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=color, edgecolor=color))


# ── Main Drawing ──────────────────────────────────────────

def generate_er_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(32, 18))
    ax.set_xlim(0, 32)
    ax.set_ylim(0, 18)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # ── Title ───────────────────────────────────────────
    ax.text(16, 17.5, 'E-Commerce Analytics Platform — Entity-Relationship Diagram',
            ha='center', va='center', fontsize=16, fontweight='bold',
            color=PG_COLOR, fontfamily='sans-serif')
    ax.text(16, 17.1, 'INF2003 Group 11 — Dual-Database Architecture (PostgreSQL + MongoDB)',
            ha='center', va='center', fontsize=10, color='#616161')

    # ── Section Labels ──────────────────────────────────
    draw_label_box(ax, 7.3, 16.8, 'PostgreSQL — Relational (ACID)', PG_COLOR, 10)
    draw_label_box(ax, 26, 16.8, 'MongoDB — NoSQL (BASE)', MONGO_COLOR, 10)

    # Vertical divider
    ax.axvline(x=18.8, ymin=0.02, ymax=0.93, color='#BDBDBD', linewidth=1, linestyle='--', zorder=0)

    # ── Draw PostgreSQL Tables ──────────────────────────
    table_centers = {}
    for name, cols in PG_TABLES:
        x, y = pg_positions[name]
        cx, top = draw_table_box(ax, name, cols, x, y, PG_HEADER, PG_COLOR)
        table_centers[name] = (cx, y, top, x + BOX_W/2, top)  # cx, bottom, top, center-x, center-top

    # ── Draw MongoDB Collections ────────────────────────
    for name, cols in MONGO_COLLECTIONS:
        x, y = mongo_positions[name]
        cx, top = draw_table_box(ax, name, cols, x, y, MONGO_HEADER, MONGO_COLOR)
        table_centers[name] = (cx, y, top, x + BOX_W/2, top)

    # ── Relationships: PostgreSQL ───────────────────────
    # customers -> orders (1:M)
    cu = table_centers["customers"]
    od = table_centers["orders"]
    draw_arrow(ax, cu[3], cu[1], od[3], od[2], PG_COLOR, 'solid', '1:M')

    # orders -> order_items (1:M)
    oi = table_centers["order_items"]
    draw_arrow(ax, od[3], od[1], oi[3], oi[2], PG_COLOR, 'solid', '1:M')

    # products -> order_items (M:1)
    pr = table_centers["products"]
    draw_arrow(ax, pr[3], pr[1], oi[3], oi[2], PG_COLOR, 'solid', 'M:1')

    # orders -> outbox (trigger)
    ob = table_centers["outbox"]
    draw_arrow(ax, od[3] + 0.3, od[2] - 0.3, ob[3] - 0.2, ob[1] + 0.5, TRIGGER_COLOR, 'dashed', 'trigger')

    # orders -> order_audit_log (trigger)
    al = table_centers["order_audit_log"]
    draw_arrow(ax, od[3] + 0.3, od[2], al[3] - 0.2, al[1] + 0.3, TRIGGER_COLOR, 'dashed', 'trigger')

    # customers -> alerts (fraud)
    alt = table_centers["alerts"]
    draw_arrow(ax, cu[3] + 0.2, cu[2] - 1.2, alt[3] - 0.2, alt[1] + 0.3, '#757575', 'dotted', 'fraud')

    # ── CDC Arrow (PostgreSQL -> MongoDB) ───────────────
    cdc_label = table_centers["customer_order_summary\n(CDC Target)"]
    ax.annotate('CDC Sync\n(Outbox Pattern)',
                xy=(cdc_label[3] - 3.5, cdc_label[4] + 1.5),
                xytext=(ob[3] + 2.5, ob[4] + 0.5),
                arrowprops=dict(arrowstyle='->', color=CDC_COLOR, lw=2.5,
                               connectionstyle='arc3,rad=0.3', linestyle='solid'),
                fontsize=8, fontweight='bold', color=CDC_COLOR, ha='center', zorder=5,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=CDC_COLOR, alpha=0.9))

    # ── Legend ──────────────────────────────────────────
    legend_y = 1.2
    ax.plot([1.5, 3.0], [legend_y, legend_y], color=PG_COLOR, linewidth=2, solid_capstyle='round')
    ax.text(3.2, legend_y, 'FK Relationship', fontsize=7, color=TEXT_COLOR, va='center')
    ax.plot([5.5, 7.0], [legend_y, legend_y], color=TRIGGER_COLOR, linewidth=2, linestyle='dashed')
    ax.text(7.2, legend_y, 'Database Trigger', fontsize=7, color=TEXT_COLOR, va='center')
    ax.plot([10.5, 12.0], [legend_y, legend_y], color=CDC_COLOR, linewidth=3, solid_capstyle='round')
    ax.text(12.2, legend_y, 'CDC Sync', fontsize=7, color=TEXT_COLOR, va='center')
    ax.plot([15.0, 16.5], [legend_y, legend_y], color='#757575', linewidth=1.5, linestyle='dotted')
    ax.text(16.7, legend_y, 'Fraud Detection', fontsize=7, color=TEXT_COLOR, va='center')

    # ── Trigger Box ─────────────────────────────────────
    draw_label_box(ax, 10.3, 6.2, '4 PostgreSQL Triggers', TRIGGER_COLOR, 7.5)
    trigger_text = (
        "1. trg_check_stock — BEFORE INSERT on order_items\n"
        "2. trg_deduct_inventory — AFTER INSERT on order_items\n"
        "3. trg_outbox_order — AFTER INSERT on orders\n"
        "4. trg_audit_order — AFTER UPDATE on orders"
    )
    ax.text(10.3, 5.6, trigger_text, fontsize=6.5, color=TEXT_COLOR,
            ha='center', va='top', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF3E0',
                     edgecolor=TRIGGER_COLOR, alpha=0.9))

    # ── Pattern Box (MongoDB) ───────────────────────────
    draw_label_box(ax, 26, 5.5, 'NoSQL Design Patterns', MONGO_COLOR, 7.5)
    pattern_text = (
        "Bucket Pattern — Events per session in one document\n"
        "Computed Pattern — Pre-aggregated session stats\n"
        "CDC Target — Denormalized order summary from PostgreSQL\n"
        "Cached Pattern — Funnel results computed on-demand"
    )
    ax.text(26, 4.9, pattern_text, fontsize=6.5, color=TEXT_COLOR,
            ha='center', va='top', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#E8F5E9',
                     edgecolor=MONGO_COLOR, alpha=0.9))

    # ── Footer ──────────────────────────────────────────
    ax.text(16, 0.3, 'INF2003 Group 11 — Team Hanzalians — June 2026',
            ha='center', fontsize=8, color='#9E9E9E')

    # ── Save ────────────────────────────────────────────
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight', facecolor=BG_COLOR, edgecolor='none')
    plt.close(fig)
    print(f"ER Diagram saved to: {OUTPUT_PATH}")
    print(f"Resolution: 300 DPI, Size: ~9600x5400 pixels")


if __name__ == "__main__":
    generate_er_diagram()
