"""
============================================================
INF2003 Group 11 — Final Report DOCX Generator
Converts G11_Final_Report.md to a professionally formatted
Word document with cover page, styled headings, tables, etc.
============================================================
"""

import re
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml


# ── Configuration ──────────────────────────────────────────
import os
DOCS_DIR = Path(os.path.dirname(os.path.abspath(__file__))) if '__file__' in dir() else Path(os.getcwd()) / "docs"
OUTPUT_PATH = DOCS_DIR / "G11_Final_Report.docx"
# Fallback if file is locked (e.g., open in Word)
try:
    OUTPUT_PATH.touch(exist_ok=True)
except PermissionError:
    import time
    OUTPUT_PATH = DOCS_DIR / f"G11_Final_Report_{int(time.time())}.docx"

# Brand colors
PRIMARY = RGBColor(0x19, 0x76, 0xD2)    # Blue (headings)
SECONDARY = RGBColor(0x0D, 0x47, 0xA1)  # Dark blue (borders)
ACCENT = RGBColor(0x2E, 0x7D, 0x32)     # Green (for special highlights)
LIGHT_BG = RGBColor(0xE3, 0xF2, 0xFD)   # Light blue (table headers)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)
MED_GRAY = RGBColor(0x75, 0x75, 0x75)

# ── DOCX Helpers ───────────────────────────────────────────

def set_cell_shading(cell, color):
    """Set background color of a table cell."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def set_cell_border(cell, **kwargs):
    """Set border of a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}></w:tcBorders>')
    for edge, val in kwargs.items():
        element = parse_xml(
            f'<w:{edge} {nsdecls("w")} w:val="{val.get("val", "single")}" '
            f'w:sz="{val.get("sz", "4")}" '
            f'w:color="{val.get("color", "1976D2")}" '
            f'w:space="0"/>'
        )
        tcBorders.append(element)
    tcPr.append(tcBorders)

def add_styled_paragraph(doc, text, style='Normal', bold=False, italic=False,
                         size=None, color=None, alignment=None, space_after=None,
                         space_before=None):
    """Add a paragraph with custom formatting."""
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    if alignment is not None:
        p.alignment = alignment
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    if space_before is not None:
        p.paragraph_format.space_before = Pt(space_before)
    return p

def add_heading_styled(doc, text, level=1):
    """Add a styled heading."""
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = PRIMARY
        if level == 1:
            run.font.size = Pt(18)
        elif level == 2:
            run.font.size = Pt(14)
        elif level == 3:
            run.font.size = Pt(12)
    h.paragraph_format.space_before = Pt(18 if level == 1 else 12)
    h.paragraph_format.space_after = Pt(6)
    return h

def add_bullet(doc, text, level=0, bold_prefix=None):
    """Add a bullet point, optionally with a bold prefix."""
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        run_b = p.add_run(bold_prefix)
        run_b.bold = True
        run_b.font.size = Pt(10)
        run_b.font.color.rgb = DARK_GRAY
        run_t = p.add_run(text)
        run_t.font.size = Pt(10)
        run_t.font.color.rgb = DARK_GRAY
    else:
        p.clear()
        run = p.add_run(text)
        run.font.size = Pt(10)
        run.font.color.rgb = DARK_GRAY
    if level > 0:
        p.paragraph_format.left_indent = Cm(1.5 * level)
    return p

def add_styled_table(doc, headers, rows, col_widths=None):
    """Add a professionally formatted table."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(header)
        run.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = WHITE
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(cell, "1976D2")

    # Data rows
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.rows[r + 1].cells[c]
            cell.text = ''
            run = cell.paragraphs[0].add_run(str(val))
            run.font.size = Pt(9)
            run.font.color.rgb = DARK_GRAY
            if r % 2 == 1:
                set_cell_shading(cell, "F5F5F5")

    # Set column widths if provided
    if col_widths:
        for i, width in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(width)

    doc.add_paragraph()  # spacer
    return table


# ── Document Builder ────────────────────────────────────────

def build_document():
    doc = Document()

    # ── Page Setup ──────────────────────────────────────
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(10)
    font.color.rgb = DARK_GRAY
    style.paragraph_format.space_after = Pt(4)
    style.paragraph_format.line_spacing = 1.15

    # ── COVER PAGE ──────────────────────────────────────
    # Add spacing to center content vertically
    for _ in range(6):
        doc.add_paragraph()

    # SIT Logo / Module line
    add_styled_paragraph(doc, "SINGAPORE INSTITUTE OF TECHNOLOGY",
                         size=11, color=MED_GRAY, alignment=WD_ALIGN_PARAGRAPH.CENTER,
                         space_after=4)
    add_styled_paragraph(doc, "INF2003 Database Design & Implementation",
                         size=11, color=MED_GRAY, alignment=WD_ALIGN_PARAGRAPH.CENTER,
                         space_after=24)

    # Project Title
    add_styled_paragraph(doc, "E-Commerce Clickstream &",
                         size=26, bold=True, color=PRIMARY,
                         alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)
    add_styled_paragraph(doc, "Transaction Analytics",
                         size=26, bold=True, color=PRIMARY,
                         alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    # Subtitle
    add_styled_paragraph(doc, "Dual-Database Analytics Platform",
                         size=14, italic=True, color=SECONDARY,
                         alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=30)

    # Horizontal rule
    p_hr = doc.add_paragraph()
    p_hr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pPr = p_hr._p.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:color="1976D2"/></w:pBdr>')
    pPr.append(pBdr)

    # Cover info table
    cover_data = [
        ("Group ID", "G11 — Team Hanzalians"),
        ("Topic", "Topic 2 — Dual-Database Analytics Platform"),
        ("Team Lead", "Hanzalah Hisam"),
        ("Team Members", "Faris Zharfan, Lucas Leow, Muhammad Hasan Bin Suwandi,\nMuhammad Raees Irfan Bin Ishak, Muhammad 'Afif Bin Muhd Lotfi Jarhom"),
        ("Submission Date", "13 July 2026"),
    ]

    table = doc.add_table(rows=len(cover_data), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (label, value) in enumerate(cover_data):
        cell_l = table.rows[i].cells[0]
        cell_l.width = Cm(4.5)
        run_l = cell_l.paragraphs[0].add_run(label)
        run_l.bold = True
        run_l.font.size = Pt(11)
        run_l.font.color.rgb = PRIMARY
        cell_l.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

        cell_r = table.rows[i].cells[1]
        cell_r.width = Cm(9.0)
        run_r = cell_r.paragraphs[0].add_run(value)
        run_r.font.size = Pt(11)
        run_r.font.color.rgb = DARK_GRAY

        # Remove borders
        for cell in [cell_l, cell_r]:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}></w:tcBorders>')
            for edge in ['top', 'left', 'bottom', 'right']:
                element = parse_xml(
                    f'<w:{edge} {nsdecls("w")} w:val="nil"/>')
                tcBorders.append(element)
            tcPr.append(tcBorders)

    doc.add_paragraph()
    doc.add_paragraph()

    # Page break after cover
    doc.add_page_break()

    # ── TABLE OF CONTENTS (placeholder) ─────────────────
    add_heading_styled(doc, "Table of Contents", 1)
    toc_items = [
        "1. Introduction",
        "2. System-Level Database Integration",
        "3. Relational Database (PostgreSQL)",
        "4. NoSQL Database (MongoDB)",
        "5. Application Implementation",
        "6. Performance Evaluation",
        "7. Testing & Quality Assurance",
        "8. Constraints & Limitations",
        "9. Discussion & Reflections",
        "Appendix — Source Code & Documentation Files",
    ]
    for item in toc_items:
        add_styled_paragraph(doc, item, size=11, color=DARK_GRAY, space_after=2)

    doc.add_page_break()

    # ── SECTION 1: Introduction ─────────────────────────
    add_heading_styled(doc, "1. Introduction", 1)

    add_styled_paragraph(doc,
        "This project demonstrates a dual-database e-commerce analytics platform: "
        "PostgreSQL handles ACID transactions (orders, inventory, customers) while "
        "MongoDB handles BASE clickstream analytics (user sessions, funnel conversion, "
        "fraud detection). The Outbox Pattern provides CDC (Change Data Capture) "
        "synchronization between the two systems.", size=10)

    add_heading_styled(doc, "Key Achievements", 2)
    achievements = [
        "8 PostgreSQL tables with 4 database triggers (stock check, inventory deduction, outbox CDC, audit logging)",
        "4 MongoDB collections implementing established NoSQL patterns (Bucket, Computed, CDC Target, Cached)",
        "18 REST API endpoints with JWT authentication and role-based access control",
        "React frontend with interactive analytics dashboard (RFM pie charts, funnel bars, market basket tables)",
        "161-test automated test suite covering all endpoints, triggers, and error cases (100% pass rate)",
        "Docker Compose one-command startup with automatic data loading and database reset capabilities",
        "Cross-database fraud detection pipeline (MongoDB velocity check → PostgreSQL alert insertion)",
        "Performance benchmark suite comparing PostgreSQL vs MongoDB on 4 different workload types",
    ]
    for a in achievements:
        add_bullet(doc, a)

    add_styled_paragraph(doc,
        "Dataset: ~275,000 rows across 6 CSV files sourced from Kaggle e-commerce datasets, "
        "loaded via an automated data ingestion pipeline.", size=10, bold=False, italic=True)

    # ── SECTION 2: System-Level Database Integration ─────
    add_heading_styled(doc, "2. System-Level Database Integration", 1)

    add_heading_styled(doc, "2.1 Architecture", 2)
    add_styled_paragraph(doc,
        "FastAPI connects to PostgreSQL via SQLAlchemy (ORM + raw SQL) and to MongoDB "
        "via Motor (async driver). The Outbox Pattern bridges the two: after each order "
        "commit, a PostgreSQL trigger writes to the outbox table, and a background async "
        "poller syncs denormalized summaries to MongoDB's customer_order_summary collection.",
        size=10)

    add_heading_styled(doc, "2.2 Consistency Strategy", 2)
    add_bullet(doc, "Write Path: PostgreSQL-first (ACID) → Outbox trigger → Async poller → MongoDB (eventual consistency)", bold_prefix="Write Path: ")
    add_bullet(doc, "Read Path: Queries target the appropriate database directly — no cross-DB JOINs are performed.", bold_prefix="Read Path: ")
    add_bullet(doc, "Failure Handling: Unprocessed outbox events remain marked processed = false and are retried on the next poll cycle.", bold_prefix="Failure Handling: ")

    # ── SECTION 3: Relational Database ──────────────────
    add_heading_styled(doc, "3. Relational Database (PostgreSQL)", 1)

    # ── ER Diagram Image ────────────────────────────────
    from pathlib import Path as P
    erd_path = P(DOCS_DIR) / "ER_Diagram.png"
    if erd_path.exists():
        add_heading_styled(doc, "3.0 Entity-Relationship Diagram", 2)
        # Add the ER diagram image - large enough to read
        img_paragraph = doc.add_paragraph()
        img_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = img_paragraph.add_run()
        run.add_picture(str(erd_path), width=Inches(6.3))
        # Caption
        add_styled_paragraph(doc,
            "Figure 1: Complete Entity-Relationship Diagram showing all 8 PostgreSQL tables (left), "
            "4 MongoDB collections (right), relationships (solid blue arrows), database triggers "
            "(dashed orange arrows), and the CDC sync flow via the Outbox Pattern (purple arrow).",
            size=8, italic=True, color=MED_GRAY, alignment=WD_ALIGN_PARAGRAPH.CENTER)

        # Diagram explanation
        add_styled_paragraph(doc,
            "Diagram Explanation: The ER diagram above illustrates the complete dual-database "
            "architecture. On the left side (blue), 8 PostgreSQL tables model the transactional "
            "core: users stores authentication credentials with bcrypt-hashed passwords, customers "
            "holds customer profiles with UUID primary keys, products maintains the catalog with "
            "CHECK constraints on stock quantities, orders records each purchase linked to a "
            "customer, and order_items captures individual line items with foreign keys to both "
            "orders and products. The outbox table serves as a CDC event store, order_audit_log "
            "tracks every field-level change, and alerts records fraud detection results.", size=10)

        add_styled_paragraph(doc,
            "On the right side (green), 4 MongoDB collections implement established NoSQL patterns: "
            "user_sessions uses the Bucket Pattern to accumulate clickstream events via atomic "
            "$push + $inc operations, session_stats provides pre-computed session aggregates "
            "(Computed Pattern), customer_order_summary holds denormalized order data synced via "
            "CDC (CDC Target Pattern), and funnel_metrics caches conversion funnel results (Cached "
            "Pattern). Relationships are shown as solid blue arrows, triggers as dashed orange "
            "arrows, and the CDC sync flow as a purple arrow.", size=10)
        doc.add_paragraph()

    add_heading_styled(doc, "3.1 Schema (8 Tables)", 2)
    add_styled_paragraph(doc,
        "The PostgreSQL schema consists of 8 tables with 3 relationship types and "
        "CHECK constraints enforcing data integrity at the database level:", size=10)

    pg_tables = [
        ["users", "Authentication accounts", "INT PK, username (UNIQUE), email (UNIQUE), bcrypt password_hash, role (customer/admin)"],
        ["customers", "Customer profiles", "UUID PK, country_code, opt_in_status. UUID prevents enumeration attacks."],
        ["products", "Product catalog", "VARCHAR PK, 7 categories, unit_price, stock_quantity (CHECK >= 0). 1,197 items."],
        ["orders", "Purchase orders", "UUID PK, FK → customers, order_date, total_amount, status. ~53,000 rows."],
        ["order_items", "Line items", "SERIAL PK, FK → orders + products, quantity (CHECK > 0). ~75,000 rows. Triggers fire here."],
        ["outbox", "CDC event store", "SERIAL PK, aggregate_id, event_type, JSONB payload, processed flag. Grows with orders."],
        ["order_audit_log", "Change history", "SERIAL PK, FK → orders, changed_by, field_name, old_value, new_value. Trigger-populated."],
        ["alerts", "Fraud detection", "SERIAL PK, customer_id, message, alert_type, acknowledged flag. Cross-DB pipeline target."],
    ]
    add_styled_table(doc, ["Table", "Purpose", "Key Features"], pg_tables, [3, 3.5, 7])

    add_styled_paragraph(doc,
        "Relationships: customers 1:M orders → orders 1:M order_items ← products M:1 order_items. "
        "UUID primary keys on customers and orders prevent enumeration attacks. CHECK constraints "
        "enforce stock_quantity >= 0 and quantity > 0 at the database level.", size=10, italic=True)

    add_heading_styled(doc, "3.2 Triggers (4)", 2)
    triggers_data = [
        ["trg_check_stock", "order_items (BEFORE INSERT)", "Raises exception if stock_quantity < requested quantity"],
        ["trg_deduct_inventory", "order_items (AFTER INSERT)", "Decrements products.stock_quantity by order_items.quantity"],
        ["trg_outbox_order", "orders (AFTER INSERT)", "Writes JSON event to outbox table for CDC sync to MongoDB"],
        ["trg_audit_order", "orders (AFTER UPDATE)", "Logs old → new values when status or total_amount changes"],
    ]
    add_styled_table(doc, ["Trigger", "Fires On", "Purpose"], triggers_data, [3.5, 4, 6])

    add_heading_styled(doc, "3.3 Advanced SQL", 2)
    add_bullet(doc, "Uses CTE with NTILE(4) to classify customers into 5 segments: Champions, Loyal Customers, Potential Loyalists, At Risk, and Lost.", bold_prefix="RFM Segmentation: ")
    add_bullet(doc, "Self-join on order_items to find co-occurring product pairs. Returns top N pairs sorted by frequency.", bold_prefix="Market Basket Analysis: ")
    add_bullet(doc, "Full change history captured by trg_audit_order trigger. Every status and total_amount change is recorded with old/new values and timestamps.", bold_prefix="Audit Trail: ")

    # ── SECTION 4: NoSQL Database ───────────────────────
    add_heading_styled(doc, "4. NoSQL Database (MongoDB)", 1)

    add_heading_styled(doc, "4.1 Collections (4)", 2)
    mongo_data = [
        ["user_sessions", "Bucket", "Accumulates clickstream events per session via $push + $inc. ~27,500 documents."],
        ["session_stats", "Computed", "Pre-aggregated session summaries for fast dashboard queries."],
        ["customer_order_summary", "CDC Target", "Denormalized view synced from PostgreSQL via Outbox. Updated with $inc."],
        ["funnel_metrics", "Cached", "Aggregated conversion funnel results computed via $facet pipeline."],
    ]
    add_styled_table(doc, ["Collection", "Pattern", "Purpose"], mongo_data, [3.5, 2.5, 7.5])

    add_heading_styled(doc, "4.2 Advanced Queries", 2)
    add_bullet(doc, "MongoDB aggregation pipeline with $facet computes conversion rates across 4 stages: page_view → add_to_cart → checkout → purchase. Typical results show ~15% add-to-cart rate and ~6% purchase conversion.", bold_prefix="$facet Funnel: ")
    add_bullet(doc, "Aggregation detecting sessions where add_to_cart events exist but checkout is missing — identifies lost sales opportunities.", bold_prefix="Cart Abandonment: ")
    add_bullet(doc, "end_time index with expireAfterSeconds: 2592000 (30 days) automatically removes stale session data, managing storage growth without manual intervention.", bold_prefix="TTL Index: ")

    # ── SECTION 5: Application Implementation ───────────
    add_heading_styled(doc, "5. Application Implementation", 1)

    add_heading_styled(doc, "5.1 Web Interface (React + Recharts)", 2)
    add_styled_paragraph(doc,
        "The frontend is a single-page application built with React 18 and Vite, "
        "featuring 4 functional views:", size=10)

    web_data = [
        ["Product Catalog", "/", "1,197 products across 7 categories, search, filter, pagination (20/page, 60 pages)"],
        ["Cart & Clickstream", "/cart", "4 event types, real-time event table, session tracking, fraud trigger demo"],
        ["Admin Dashboard", "/admin", "RFM pie chart, funnel bar chart, market basket, top products, alerts (admin only)"],
        ["Login/Register", "/login", "JWT auth with bcrypt hashing, form validation, role-based redirect"],
    ]
    add_styled_table(doc, ["Page", "Route", "Features"], web_data, [3, 2, 8.5])

    add_heading_styled(doc, "5.2 Key Features", 2)
    features = [
        "JWT authentication with bcrypt password hashing and role-based access control (customer/admin)",
        "Product catalog with category filter (7 categories), text search, and pagination (20/100 per page)",
        "Clickstream event tracking via MongoDB Bucket Pattern — all 4 funnel event types recorded with $push + $inc",
        "Order creation with full ACID transaction — FK validation, stock check, inventory deduction, outbox CDC, and audit logging all fire automatically via database triggers",
        "Real-time fraud detection — MongoDB session velocity analysis triggers PostgreSQL alert insertion when 10+ add_to_cart events occur in 60 seconds without a purchase",
        "Admin dashboard with RFM pie chart (Champions/Loyal/At Risk/Lost), funnel bar chart (4-stage conversion), market basket table (top 10 pairs), top products, sales by category, and fraud alerts table",
        "Automated test suite — 161 tests covering every endpoint, trigger, and error case (7-second runtime, 100% pass rate)",
        "Docker Compose one-command startup with automatic data loading and database reset capabilities",
    ]
    for f in features:
        add_bullet(doc, f)

    # ── SECTION 6: Performance Evaluation ───────────────
    add_heading_styled(doc, "6. Performance Evaluation", 1)
    add_styled_paragraph(doc,
        "Benchmarks were run using backend/benchmark/benchmark_runner.py inside the Docker "
        "environment. The suite measures 4 distinct workload types to highlight the strengths "
        "of each database:", size=10)

    bench_data = [
        ["1", "Bulk Insert (10k events)", "MongoDB", "Bucket Pattern updateOne with $push + $inc + upsert"],
        ["2", "Hotspot UPDATEs (200 txns)", "PostgreSQL", "Concurrent UPDATE under contention"],
        ["3", "5-Table JOIN", "PostgreSQL", "SELECT across orders + customers + items + products"],
        ["4", "Aggregation Pipeline", "MongoDB", "$unwind + $group equivalent of GROUP BY"],
    ]
    add_styled_table(doc, ["#", "Test", "Database", "Operation"], bench_data, [1, 3.5, 2.5, 6.5])

    add_styled_paragraph(doc,
        "Key findings: MongoDB excels at bulk inserts (Bucket Pattern avoids per-event document "
        "overhead), while PostgreSQL handles concurrent transactional updates with row-level locking "
        "that prevents data corruption. The 5-table JOIN is only possible in PostgreSQL (MongoDB has "
        "no native JOIN support), demonstrating why a polyglot persistence approach is necessary for "
        "this use case. Results are plotted to benchmark_results.png using matplotlib.", size=10)

    # ── SECTION 7: Testing & QA ─────────────────────────
    add_heading_styled(doc, "7. Testing & Quality Assurance", 1)
    add_styled_paragraph(doc,
        "A comprehensive test suite (backend/tests/test_suite.py) was developed with "
        "161 automated tests. Result: 161/161 passed (100%) in 7.08 seconds.", size=10)

    test_data = [
        ["Health Checks", "7", "Root, PostgreSQL/MongoDB connectivity, Swagger UI, OpenAPI schema"],
        ["Authentication", "12", "Registration, login, /me, duplicates, invalid passwords, expired tokens"],
        ["Products API", "30", "Listing, pagination, category filter, search, get-by-ID, 404, categories"],
        ["Cart/Clickstream", "16", "All 4 event types, invalid inputs, session retrieval, auto-generated IDs"],
        ["Orders (ACID)", "18", "Order creation, retrieval, insufficient stock, inventory deduction, outbox CDC"],
        ["Analytics", "24", "RFM (5 segments), market basket, funnel ($facet), cart abandonment, top products"],
        ["Admin Analytics", "7", "Alerts (admin + non-admin 403), audit trail (admin + non-admin + unauthenticated)"],
        ["Trigger Verification", "10", "All 4 trigger functions confirmed, table attachments, CHECK constraints"],
        ["MongoDB Verification", "10", "All 4 collections, compound index, TTL index, flagged, timestamp indexes"],
        ["Error Handling", "6", "Empty body, short username, invalid email, short password, 404, bad pagination"],
    ]
    add_styled_table(doc, ["Section", "Tests", "Key Checks"], test_data, [3, 1.5, 9])

    # ── SECTION 8: Constraints ──────────────────────────
    add_heading_styled(doc, "8. Constraints & Limitations", 1)
    constraints = [
        ("Outbox polling introduces ~5 second staleness ", "for CDC data in MongoDB. Real-time CDC would require Kafka + Debezium, which was beyond the project scope."),
        ("Fraud detection uses simple threshold counting ", "(10 events in 60 seconds). Production systems would use ML models trained on historical fraud patterns."),
        ("No distributed tracing or production observability ", "(no OpenTelemetry, no centralized logging)."),
        ("Single-instance databases ", "— no replication, sharding, or failover configured."),
        ("The users and customers tables have no FK relationship, ", "meaning any authenticated user can place orders under any customer ID. A production system would link them."),
    ]
    for bold_part, normal_part in constraints:
        add_bullet(doc, normal_part, bold_prefix=bold_part)

    # ── SECTION 9: Discussion & Reflections ─────────────
    add_heading_styled(doc, "9. Discussion & Reflections", 1)

    add_heading_styled(doc, "9.1 What Worked Well", 2)
    worked_well = [
        ("Clear separation of concerns: ", "PostgreSQL handles everything requiring ACID (orders, inventory); MongoDB handles everything requiring high write throughput (clickstream, sessions, funnel). Neither database is a bottleneck for the other's workload."),
        ("Outbox Pattern provided reliable CDC ", "without external infrastructure (Kafka, Debezium). The pattern was simple to implement, easy to debug, and guaranteed at-least-once delivery."),
        ("Database triggers simplified the application layer ", "— inventory management, CDC event generation, and audit logging happen automatically at the database level, reducing application code complexity and eliminating race conditions."),
        ("MongoDB Bucket Pattern ", "perfectly matched the clickstream use case. $push + $inc operations are O(1) and avoid the document-per-event anti-pattern."),
        ("Docker Compose ", "made the project instantly reproducible. The data loader auto-runs on first start, and the reset service enables clean demos."),
    ]
    for bold_part, normal_part in worked_well:
        add_bullet(doc, normal_part, bold_prefix=bold_part)

    add_heading_styled(doc, "9.2 Challenges", 2)
    challenges = [
        ("Cross-database consistency ", "required careful design. The Outbox Pattern provides eventual consistency, but debugging sync failures required checking both PostgreSQL (outbox.processed) and MongoDB (customer_order_summary)."),
        ("Trigger debugging was difficult ", "— PostgreSQL trigger errors roll back the entire transaction, and error messages appear only in server logs, not application output."),
        ("The JWT sub claim initially used an integer ", "user_id, which python-jose rejects (requires string). This was discovered and fixed during integration testing (changed to str(user.user_id))."),
    ]
    for bold_part, normal_part in challenges:
        add_bullet(doc, normal_part, bold_prefix=bold_part)

    add_heading_styled(doc, "9.3 GenAI Usage Reflection", 2)
    add_styled_paragraph(doc,
        "GenAI tools (ChatGPT, DeepSeek) were used throughout the project to generate initial "
        "boilerplate for FastAPI routes, SQLAlchemy models, and React components; debug PostgreSQL "
        "trigger syntax and MongoDB aggregation pipelines; and draft documentation (README, walkthrough, "
        "ER diagram).", size=10)
    add_bullet(doc, "Significantly accelerated development; provided working examples for unfamiliar technologies (Motor async driver, Recharts integration); helped identify the JWT sub type bug.", bold_prefix="Pros: ")
    add_bullet(doc, "Generated code occasionally contained subtle bugs (e.g., the integer sub issue); required careful review and testing; sometimes produced over-engineered solutions.", bold_prefix="Cons: ")
    add_bullet(doc, "Use GenAI for boilerplate generation and debugging, but maintain a strong test suite as a safety net. The 161-test suite was essential for catching AI-generated bugs.", bold_prefix="Recommendation: ")

    add_heading_styled(doc, "9.4 Future Improvements", 2)
    improvements = [
        "Add Kafka + Debezium for real-time CDC (sub-second latency vs current 5-second polling)",
        "Implement Redis caching for the product catalog (reducing PostgreSQL query load)",
        "Deploy to AWS RDS (PostgreSQL) + MongoDB Atlas for cloud-native scalability",
        "Add proper user-customer linking via FK from users to customers",
        "Implement session replay — reconstruct a user's browsing journey from MongoDB events",
        "Add OAuth2 social login (Google, GitHub) alongside current username/password auth",
    ]
    for imp in improvements:
        add_bullet(doc, imp)

    # ── APPENDIX ────────────────────────────────────────
    doc.add_page_break()
    add_heading_styled(doc, "Appendix — Source Code & Documentation Files", 1)
    add_styled_paragraph(doc, "This appendix is not counted toward the 8-page limit.", size=9, italic=True, color=MED_GRAY)

    appendix_data = [
        ["backend/triggers.sql", "4 PostgreSQL trigger definitions (stock check, inventory, outbox, audit)"],
        ["backend/models/relational.py", "SQLAlchemy ORM models for all 8 PostgreSQL tables"],
        ["backend/services/nosql_service.py", "MongoDB operations: Bucket Pattern, funnel, fraud detection, indexes"],
        ["backend/services/relational_service.py", "Complex SQL: RFM CTEs, market basket self-join, audit queries"],
        ["backend/services/sync_service.py", "CDC Outbox processor — async poller + MongoDB sync"],
        ["backend/data_loader.py", "CSV ingestion pipeline for 6 datasets into both databases"],
        ["backend/reset_db.py", "Database reset script (PostgreSQL + MongoDB wipe and recreate)"],
        ["backend/tests/test_suite.py", "161-test automated test suite (100% pass rate)"],
        ["backend/benchmark/benchmark_runner.py", "Performance comparison: PostgreSQL vs MongoDB"],
        ["docker-compose.yml", "5-container orchestration with auto data loading and DB reset"],
        ["README.md", "Technical documentation with API reference and architecture diagram"],
        ["walkthrough.md", "Non-technical guide with glossary and step-by-step instructions"],
        ["DOCKER_TROUBLESHOOTING.md", "12+ common Docker issues with diagnostic commands"],
        ["docs/ER_Diagram.md", "Complete ER diagram with 8 tables + 4 MongoDB collections"],
    ]
    add_styled_table(doc, ["File", "Description"], appendix_data, [6, 7.5])

    # ── Footer ──────────────────────────────────────────
    doc.add_paragraph()
    p_footer = add_styled_paragraph(doc,
        "INF2003 Group 11 — Team Hanzalians — Singapore Institute of Technology — July 2026",
        size=9, color=MED_GRAY, alignment=WD_ALIGN_PARAGRAPH.CENTER, italic=True)

    # ── Save ────────────────────────────────────────────
    try:
        doc.save(str(OUTPUT_PATH))
        print(f"DOCX saved to: {OUTPUT_PATH}")
        print(f"File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")
    except PermissionError:
        import time
        alt_path = DOCS_DIR / f"G11_Final_Report_{int(time.time())}.docx"
        doc.save(str(alt_path))
        print(f"DOCX saved to: {alt_path} (original was locked)")
        print(f"File size: {alt_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    build_document()
