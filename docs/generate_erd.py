"""
INF2003 Group 11 — Simple Clean ER Diagrams
Uses colored rectangles + text — no table overlapping issues.
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os
from pathlib import Path

OUT = str(Path(__file__).resolve().parent)
PG_HDR = '#0D47A1'; MG_HDR = '#1B5E20'; TC = '#E65100'; BG = '#FAFAFA'

def box(ax, x, y, w, h, color, text, fontsize=10, bold=False, tc='white'):
    """Draw a rounded rectangle with centered text."""
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                           facecolor=color, edgecolor=color, linewidth=1.2, zorder=2)
    ax.add_patch(patch)
    lines = text.split('\n')
    cy = y + h/2
    for i, line in enumerate(lines):
        off = (len(lines)-1)*fontsize*0.35 - i*fontsize*0.7
        ax.text(x + w/2, cy + off, line, ha='center', va='center',
                fontsize=fontsize, fontweight='bold' if bold else 'normal',
                color=tc, fontfamily='monospace', zorder=3)

def row_text(ax, x, y, w, text, fontsize=9, color='#212121', bold=False, indent=0.15):
    """Draw a single row of text inside a table body with better indentation."""
    ax.text(x + indent, y, text, ha='left', va='center', fontsize=fontsize,
            fontweight='bold' if bold else 'normal', color=color,
            fontfamily='monospace', zorder=3)

def table_block(ax, name, cols, x, y, w, header_color, fs=9):
    """Draw a complete table: header + body rows + border."""
    row_h = 0.35
    header_h = 0.45
    n = len(cols)
    total_h = header_h + n * row_h

    body = FancyBboxPatch((x, y), w, total_h, boxstyle="round,pad=0.08",
                          facecolor='white', edgecolor='#CCC', linewidth=1, zorder=1)
    ax.add_patch(body)
    box(ax, x, y + total_h - header_h, w, header_h, header_color, name, fontsize=10, bold=True)

    for i, col in enumerate(cols):
        ry = y + total_h - header_h - (i + 1) * row_h
        is_pk = col.strip().startswith("PK")
        is_fk = col.strip().startswith("FK")
        is_check = col.strip().startswith("CHECK") or col.strip().startswith("Index:")
        is_sub = col.strip().startswith("·")
        if is_pk: c, sz, b = '#1565C0', fs, True
        elif is_fk: c, sz, b = '#E65100', fs, False
        elif is_check: c, sz, b = '#757575', 8.5, False
        elif is_sub: c, sz, b = '#888', 8.5, False
        else: c, sz, b = '#212121', fs, False
        row_text(ax, x, ry, w, col, fontsize=sz, color=c, bold=b)
    return y + total_h, y

def gen_pg():
    fig, ax = plt.subplots(figsize=(18, 14))
    ax.set_xlim(0, 18); ax.set_ylim(0, 14); ax.axis('off')
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.text(9, 13.6, 'PostgreSQL — Relational Database (8 Tables, 4 Triggers)', ha='center', fontsize=16, fontweight='bold', color=PG_HDR)
    ax.text(9, 13.15, 'INF2003 Group 11 — Team Hanzalians', ha='center', fontsize=10, color='#999')
    W = 4.2; FS = 9

    users_cols = ["PK user_id         INT","   username        VARCHAR(50) UNIQUE","   email           VARCHAR(100) UNIQUE","   password_hash   VARCHAR(255)","   role            VARCHAR(20)","   created_at      TIMESTAMP"]
    cust_cols = ["PK customer_id     UUID","   country_code    VARCHAR(3)","   opt_in_status   BOOLEAN"]
    orders_cols = ["PK order_id        UUID","FK customer_id     UUID","   order_date      TIMESTAMP","   total_amount    DOUBLE PREC.","   status          VARCHAR(20)"]
    table_block(ax, "users", users_cols, 1.0, 9.95, W, PG_HDR)
    table_block(ax, "customers", cust_cols, 1.0, 8.0, W, PG_HDR)
    table_block(ax, "orders", orders_cols, 1.0, 5.3, W, PG_HDR)

    prod_cols = ["PK product_id      VARCHAR(50)","   category        VARCHAR(100)","   unit_price      DOUBLE PREC.","   stock_quantity  INTEGER","CHECK (stock_quantity >= 0)"]
    oi_cols = ["PK item_id         SERIAL","FK order_id        UUID","FK product_id      VARCHAR(50)","   quantity        INTEGER","CHECK (quantity > 0)"]
    table_block(ax, "products", prod_cols, 7.0, 10.3, W, PG_HDR)
    table_block(ax, "order_items", oi_cols, 7.0, 7.3, W, PG_HDR)

    outbox_cols = ["PK event_id        SERIAL","   aggregate_id    VARCHAR(255)","   event_type      VARCHAR(100)","   payload         JSONB","   created_at      TIMESTAMP","   processed       BOOLEAN"]
    audit_cols = ["PK audit_id        SERIAL","FK order_id        UUID","   changed_by      VARCHAR(50)","   field_name      VARCHAR(100)","   old_value       TEXT","   new_value       TEXT","   changed_at      TIMESTAMP"]
    alerts_cols = ["PK alert_id        SERIAL","   customer_id     UUID","   message         TEXT","   alert_type      VARCHAR(50)","   created_at      TIMESTAMP","   acknowledged    BOOLEAN"]
    table_block(ax, "outbox (CDC)", outbox_cols, 13.0, 9.95, W, PG_HDR)
    table_block(ax, "order_audit_log", audit_cols, 13.0, 6.6, W, PG_HDR)
    table_block(ax, "alerts (Fraud)", alerts_cols, 13.0, 3.55, W, PG_HDR)

    def arr(x1, y1, x2, y2, label, color='#1565C0', style='-'):
        ax.annotate(label, xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', color=color, lw=2, ls=style),
                    fontsize=9, color=color, fontweight='bold', ha='center', bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none'))
    arr(3.1, 8.0, 3.1, 7.5, '1:M')
    arr(9.1, 10.3, 9.1, 9.5, 'M:1')
    arr(5.2, 6.4, 7.0, 8.4, '1:M')
    arr(5.2, 7.0, 13.0, 11.2, 'trigger', TC, '--')
    arr(5.2, 6.0, 13.0, 8.0, 'trigger', TC, '--')
    arr(5.2, 8.7, 13.0, 4.8, 'fraud', '#999', ':')

    ax.text(9, 2.5, '4 TRIGGERS:\n(1) trg_check_stock — BEFORE INSERT on order_items — rejects if stock insufficient\n(2) trg_deduct_inventory — AFTER INSERT on order_items — decrements stock_quantity\n(3) trg_outbox_order — AFTER INSERT on orders — writes JSON event to outbox for CDC\n(4) trg_audit_order — AFTER UPDATE on orders — logs old/new values to audit_log',
            ha='center', fontsize=9, fontfamily='monospace', color='#212121', bbox=dict(boxstyle='round,pad=0.4', fc='#FFF3E0', ec=TC, lw=1.2))
    ax.text(9, 0.8, '--- FK (1:M / M:1)     --- Trigger     ··· Fraud Detection', ha='center', fontsize=8, color='#999')
    ax.text(9, 0.3, 'INF2003 Group 11 — Team Hanzalians — June 2026', ha='center', fontsize=7, color='#CCC')
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, "ER_Diagram_PostgreSQL.png"), dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print("PostgreSQL saved.")

def gen_mongo():
    fig, ax = plt.subplots(figsize=(18, 12))
    ax.set_xlim(0, 18); ax.set_ylim(0, 12); ax.axis('off')
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.text(9, 11.6, 'MongoDB — NoSQL Document Store (4 Collections)', ha='center', fontsize=16, fontweight='bold', color=MG_HDR)
    ax.text(9, 11.15, 'Design Patterns: Bucket | Computed | CDC Target | Cached', ha='center', fontsize=10, color='#999')
    W = 5.5

    us_cols = ["PK _id              ObjectId","   customer_id      String","   session_id       String","   start_time       ISODate","   end_time         ISODate  (TTL: 30d)","   event_count      Integer  ($inc)","   flagged          Boolean","   events[]         Array  ($push)","· action_type       String","· product_id        String","· timestamp         ISODate","Index: (customer_id, session_id) UNIQUE","Index: end_time TTL (30-day expiry)","Index: flagged, events.timestamp"]
    cdc_cols = ["PK _id              ObjectId","   customer_id      String UNIQUE","   total_orders     Integer  ($inc)","   total_spent      Float  ($inc)","   last_order_date  ISODate","   last_updated     ISODate","Index: customer_id UNIQUE"]
    ss_cols = ["PK _id              ObjectId","   session_id       String UNIQUE","   customer_id      String","   total_events     Integer","   page_views       Integer","   add_to_carts     Integer","   checkouts        Integer","   purchases        Integer","   duration_seconds Integer","Index: session_id UNIQUE"]
    fm_cols = ["PK _id              ObjectId","   stage            String","   count            Integer","   conversion_rate  Float (%)","   computed_at      ISODate","Index: (stage, computed_at DESC)"]

    table_block(ax, "user_sessions (Bucket Pattern)", us_cols, 1.0, 5.15, W, MG_HDR)
    table_block(ax, "customer_order_summary (CDC Target)", cdc_cols, 1.0, 1.6, W, MG_HDR)
    table_block(ax, "session_stats (Computed Pattern)", ss_cols, 8.5, 6.55, W, MG_HDR)
    table_block(ax, "funnel_metrics (Cached Pattern)", fm_cols, 8.5, 3.45, W, MG_HDR)

    ax.text(14.5, 2.5, 'CDC SYNC (Outbox Pattern):\n(1) Order placed in PostgreSQL\n    -> trg_outbox_order fires -> JSON in outbox\n(2) Background poller every 5 sec\n    reads outbox WHERE processed=false\n(3) MongoDB: $inc total_orders +1,\n    $inc total_spent +amount\n(4) Event marked processed=true',
            ha='center', fontsize=8.5, fontfamily='monospace', color='#212121', va='top', bbox=dict(boxstyle='round,pad=0.4', fc='#F3E5F5', ec='#7B1FA2', lw=1.2))
    ax.text(9, 0.5, 'MongoDB Patterns: Bucket ($push+$inc) · Computed (pre-aggregated) · CDC Target (denormalized) · Cached ($facet results)', ha='center', fontsize=8, color='#999')
    ax.text(9, 0.15, 'INF2003 Group 11 — Team Hanzalians — June 2026', ha='center', fontsize=7, color='#CCC')
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, "ER_Diagram_MongoDB.png"), dpi=300, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print("MongoDB saved.")

if __name__ == "__main__":
    gen_pg(); gen_mongo(); print("Done!")
