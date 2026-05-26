"""
============================================================
INF2003 Group 11 — Performance Benchmarking Script
Benchmarks:
  1. Bulk insert 100k clickstream events into MongoDB
  2. Concurrent hotspot inventory updates on PostgreSQL
  3. Complex JOIN query (5 tables) vs MongoDB aggregation
Generates matplotlib bar chart saved to plots/benchmark_results.png
============================================================
"""

import time
import threading
import asyncio
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from sqlalchemy import text

from config import settings
from models.relational import SessionLocal, Product
from services.nosql_service import track_clickstream_event, get_mongo_db

PLOTS_DIR = Path(__file__).parent / "plots"
PLOTS_DIR.mkdir(exist_ok=True)


# ============================================================
# BENCHMARK 1: Bulk Insert 100k Clickstream Events -> MongoDB
# ============================================================
async def benchmark_mongo_bulk_insert(n_events: int = 100_000):
    """
    Measure time to insert N clickstream events into MongoDB
    using the Bucket Pattern (updateOne with $push).
    """
    print(f"\n📊 Benchmark 1: Bulk inserting {n_events:,} clickstream events into MongoDB...")

    start = time.perf_counter()

    # Batch into sessions of 100 events each
    sessions_count = n_events // 100
    tasks = []

    from models.nosql_schemas import ActionType
    for i in range(sessions_count):
        session_id = f"bench_session_{i}"
        customer_id = f"bench_cust_{i % 1000}"

        for j in range(100):
            tasks.append(
                track_clickstream_event(
                    customer_id=customer_id,
                    session_id=session_id,
                    action_type=ActionType.PAGE_VIEW if j % 3 != 0 else ActionType.ADD_TO_CART,
                    product_id=str((i * 100 + j) % 5000),
                )
            )

        # Process in chunks to avoid overwhelming the event loop
        if len(tasks) >= 5000:
            await asyncio.gather(*tasks)
            tasks = []

    if tasks:
        await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start
    ops_per_sec = n_events / elapsed

    print(f"  ✅ Completed in {elapsed:.2f}s ({ops_per_sec:,.0f} ops/sec)")

    return {
        "name": "MongoDB Bulk Insert\n(100k events, Bucket Pattern)",
        "time_seconds": round(elapsed, 2),
        "ops_per_sec": round(ops_per_sec, 0),
    }


# ============================================================
# BENCHMARK 2: Concurrent Hotspot Inventory Updates (PostgreSQL)
# ============================================================
def hotspot_update_worker(product_id: str, iterations: int, results: list):
    """Worker thread: repeatedly UPDATE stock_quantity on a single product."""
    db = SessionLocal()
    try:
        for _ in range(iterations):
            try:
                db.execute(
                    text("UPDATE products SET stock_quantity = stock_quantity - 1 WHERE product_id = :pid AND stock_quantity > 0"),
                    {"pid": product_id},
                )
                db.commit()
            except Exception:
                db.rollback()
    finally:
        db.close()


def benchmark_postgres_hotspot(n_threads: int = 50, iterations_per_thread: int = 20):
    """
    Simulate 1,000 rapid UPDATEs on a single product in PostgreSQL
    across multiple threads. Measures transactions per second under contention.
    """
    print(f"\n📊 Benchmark 2: Concurrent hotspot updates on PostgreSQL...")
    print(f"   {n_threads} threads × {iterations_per_thread} updates = {n_threads * iterations_per_thread} total")

    # Ensure we have a product with enough stock
    db = SessionLocal()
    product = db.query(Product).first()
    if product:
        product.stock_quantity = 100_000  # Set high stock
        db.commit()
        product_id = product.product_id
    else:
        db.close()
        return {"name": "PostgreSQL Hotspot\n(no products)", "time_seconds": 0, "ops_per_sec": 0}
    db.close()

    threads = []
    results = []

    start = time.perf_counter()

    for _ in range(n_threads):
        t = threading.Thread(
            target=hotspot_update_worker,
            args=(product_id, iterations_per_thread, results),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.perf_counter() - start
    total_ops = n_threads * iterations_per_thread
    ops_per_sec = total_ops / elapsed if elapsed > 0 else 0

    print(f"  ✅ Completed in {elapsed:.2f}s ({ops_per_sec:,.0f} txns/sec)")

    return {
        "name": "PostgreSQL Hotspot\n(1,000 concurrent UPDATEs)",
        "time_seconds": round(elapsed, 2),
        "ops_per_sec": round(ops_per_sec, 0),
    }


# ============================================================
# BENCHMARK 3: Complex JOIN Query (5 tables) — PostgreSQL
# ============================================================
def benchmark_complex_join_postgres():
    """
    Execute a 5-table JOIN query on PostgreSQL and measure execution time.
    Joins: orders -> customers -> order_items -> products.
    """
    print(f"\n📊 Benchmark 3: Complex 5-table JOIN query on PostgreSQL...")

    query = text("""
        SELECT
            o.order_id,
            c.customer_id,
            c.country_code,
            oi.product_id,
            p.category,
            p.unit_price,
            oi.quantity,
            o.total_amount,
            o.order_date
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        ORDER BY o.order_date DESC
        LIMIT 1000;
    """)

    db = SessionLocal()

    # Warm-up
    db.execute(query)
    db.commit()

    # Timed run
    start = time.perf_counter()
    result = db.execute(query)
    rows = result.fetchall()
    elapsed = time.perf_counter() - start

    db.close()

    print(f"  ✅ Fetched {len(rows)} rows in {elapsed:.4f}s")

    return {
        "name": "PostgreSQL 5-Table JOIN\n(orders+customers+items+products)",
        "time_seconds": round(elapsed, 4),
        "rows_returned": len(rows),
    }


# ============================================================
# BENCHMARK 3b: MongoDB Equivalent (Aggregation Pipeline)
# ============================================================
async def benchmark_complex_aggregation_mongo():
    """
    MongoDB aggregation pipeline as NoSQL equivalent.
    Demonstrates structural difference: no JOINs, uses $lookup.
    """
    print(f"\n📊 Benchmark 3b: MongoDB aggregation pipeline...")

    db = await get_mongo_db()

    pipeline = [
        {"$unwind": "$events"},
        {"$match": {"events.action_type": "add_to_cart"}},
        {
            "$group": {
                "_id": "$session_id",
                "customer_id": {"$first": "$customer_id"},
                "event_count": {"$first": "$event_count"},
                "unique_products": {"$addToSet": "$events.product_id"},
            }
        },
        {"$sort": {"event_count": -1}},
        {"$limit": 1000},
    ]

    start = time.perf_counter()
    result = await db.user_sessions.aggregate(pipeline).to_list(length=1000)
    elapsed = time.perf_counter() - start

    print(f"  ✅ Fetched {len(result)} documents in {elapsed:.4f}s")

    return {
        "name": "MongoDB Aggregation\n($unwind+$group, no JOINs)",
        "time_seconds": round(elapsed, 4),
        "rows_returned": len(result),
    }


# ============================================================
# Generate Plot
# ============================================================
def generate_benchmark_plot(results: list[dict]):
    """Generate a bar chart comparing benchmark results."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Execution Time (seconds)
    ax1 = axes[0]
    names = [r["name"].replace("\n", " ") for r in results]
    times = [r["time_seconds"] for r in results]
    colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336"][:len(results)]

    bars = ax1.bar(range(len(names)), times, color=colors, edgecolor="white", linewidth=1.2)
    ax1.set_xticks(range(len(names)))
    ax1.set_xticklabels(names, fontsize=8, rotation=15, ha="right")
    ax1.set_ylabel("Time (seconds)")
    ax1.set_title("Execution Time Comparison")
    ax1.grid(axis="y", alpha=0.3)

    # Add value labels
    for bar, t in zip(bars, times):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                 f"{t:.3f}s", ha="center", va="bottom", fontsize=8)

    # Plot 2: Throughput / Row Count
    ax2 = axes[1]
    if any("ops_per_sec" in r for r in results):
        throughputs = [r.get("ops_per_sec", 0) for r in results]
        bar_colors = colors
        bars2 = ax2.bar(range(len(names)), throughputs, color=bar_colors, edgecolor="white", linewidth=1.2)
        ax2.set_xticks(range(len(names)))
        ax2.set_xticklabels(names, fontsize=8, rotation=15, ha="right")
        ax2.set_ylabel("Operations / Second")
        ax2.set_title("Throughput Comparison")
        ax2.grid(axis="y", alpha=0.3)

        for bar, t in zip(bars2, throughputs):
            if t > 0:
                ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                         f"{t:,.0f}", ha="center", va="bottom", fontsize=8)

    plt.suptitle("INF2003 Group 11 — Database Performance Benchmarks", fontsize=14, fontweight="bold")
    plt.tight_layout()

    output_path = PLOTS_DIR / "benchmark_results.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n📈 Benchmark plot saved to: {output_path}")

    return str(output_path)


# ============================================================
# Main Runner
# ============================================================
async def run_all_benchmarks():
    """Run all benchmarks and generate the plot."""
    print("=" * 60)
    print("🔬 INF2003 Group 11 — Database Benchmark Suite")
    print("=" * 60)

    results = []

    # Benchmark 1: MongoDB bulk insert (reduced for practicality)
    mongo_result = await benchmark_mongo_bulk_insert(n_events=10_000)
    results.append(mongo_result)

    # Benchmark 2: PostgreSQL hotspot updates
    pg_result = benchmark_postgres_hotspot(n_threads=20, iterations_per_thread=10)
    results.append(pg_result)

    # Benchmark 3: Complex JOIN PostgreSQL
    join_result = benchmark_complex_join_postgres()
    results.append(join_result)

    # Benchmark 3b: MongoDB aggregation
    mongo_agg_result = await benchmark_complex_aggregation_mongo()
    results.append(mongo_agg_result)

    # Generate plot
    plot_path = generate_benchmark_plot(results)

    print("\n" + "=" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 60)
    for r in results:
        name = r["name"].replace("\n", " | ")
        print(f"  {name}: {r['time_seconds']}s")
    print(f"\n  Plot saved to: {plot_path}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
