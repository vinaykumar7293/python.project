"""
Customer Feedback Summary - Main Application Entry Point
DataSpark Challenge | Project #84: Small Business & Retail Analytics

Usage:
  python main.py              # Launch interactive terminal UI (Default)
  python main.py --gui        # Launch Tkinter Desktop Graphical UI
  python main.py --summary    # Display quick executive summary & exit
  python main.py --export     # Export reports (Markdown, CSV, TXT, PNG Charts)
  python main.py --import <f> # Ingest legacy CSV dataset with audit report
  python main.py --demo       # Run automated end-to-end hackathon demo
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.models import FeedbackRecord
from src.storage import StorageManager
from src.analytics import FeedbackAnalytics
from src.exporter import ReportExporter
from src.importer import BulkDatasetImporter
from src.cli import FeedbackCLI


def run_automated_demo():
    """
    Executes an automated end-to-end walkthrough demonstrating:
    1. Defensive validation catches and corrects bad input
    2. Local file persistence survives restarts
    3. Analytics computes CSAT, NPS, and NLP themes
    4. Multi-format export compiles Markdown and Matplotlib charts
    5. Bulk ingestion with row-by-row error logging
    """
    print("\n" + "=" * 75)
    print(" 🚀 COMMENCING AUTOMATED HACKATHON DEMO WALKTHROUGH")
    print(" Project #84: Customer Feedback Summary | Retail Domain")
    print("=" * 75)

    storage = StorageManager("data/demo_feedback.json", "data/demo_feedback.csv")
    
    # 1. Load initial records
    records = storage.load_records()
    if not records:
        print("\n[*] Initializing demo storage from sample data...")
        from data.generate_sample_data import main as gen_data
        gen_data()
        sample_mgr = StorageManager("data/sample_feedback.json")
        records = sample_mgr.load_records()
        storage.save_records(records)

    print(f"\n[Step 1] Verified Storage: {len(records)} active feedback records loaded.")

    # 2. Demonstrate Defensive Validation
    print("\n[Step 2] Testing Defensive Input Validation Engine:")
    from src.validator import validate_customer_name, validate_rating, validate_date, validate_customer_email

    test_cases = [
        ("Customer Name", validate_customer_name, "J", "Too short"),
        ("Rating Boundary", validate_rating, 6, "Exceeds 5 stars"),
        ("Future Date", validate_date, "2030-01-01", "Future date rejection"),
        ("Email Syntax", validate_customer_email, "notanemail", "Missing @ and domain"),
    ]

    for label, validator, test_input, desc in test_cases:
        ok, val, err = validator(test_input)
        status = "PASSED (Rejected erroneous input)" if not ok else "FAILED"
        print(f"  • {label} Check: Input='{test_input}' -> {status}")
        print(f"    Expected Rule: {desc} | Error Caught: '{err}'")

    # 3. Add Valid Record and verify NLP enrichment
    print("\n[Step 3] Adding Valid Customer Feedback with NLP Enrichment:")
    new_fb = FeedbackRecord(
        feedback_id="DEMO-999",
        customer_name="Alex Mercer",
        customer_email="alex.mercer@prototype.org",
        date="2026-03-18",
        channel="In-Store",
        category="Checkout & Billing",
        rating=1,
        feedback_text="Awful slow checkout line! Cashier was rude and unhelpful.",
        store_location="Downtown Mall",
        status="Action Required",
        action_priority="Critical"
    )
    sent_label, sent_score = FeedbackAnalytics.analyze_sentiment(new_fb.feedback_text, rating=new_fb.rating)
    new_fb.sentiment = sent_label
    new_fb.sentiment_score = sent_score
    new_fb.keywords = FeedbackAnalytics.extract_keywords(new_fb.feedback_text)
    storage.add_record(new_fb)
    print(f"  ✓ Added Record: {new_fb.feedback_id} | Rating: {new_fb.rating}★")
    print(f"  ✓ NLP Sentiment: {new_fb.sentiment} ({new_fb.sentiment_score:+.2f})")
    print(f"  ✓ Extracted Keywords: {new_fb.keywords}")

    # 4. Persistence verification
    print("\n[Step 4] Verifying Local File Persistence Across Simulated Restart:")
    fresh_storage = StorageManager("data/demo_feedback.json", "data/demo_feedback.csv")
    reloaded_record = fresh_storage.get_record("DEMO-999")
    if reloaded_record:
        print(f"  ✓ State Preservation Verified! Found record '{reloaded_record.feedback_id}' in persistent JSON/CSV.")
    else:
        print("  ✗ Error: Record not found after reload.")

    # 5. Core Business Logic & Executive Summary
    print("\n[Step 5] Computing Real-Time Executive Analytics:")
    current_records = fresh_storage.load_records()
    metrics = FeedbackAnalytics.compute_rating_metrics(current_records)
    print(f"  • Total Entries      : {metrics['total_records']}")
    print(f"  • Average Rating     : ★ {metrics['average_rating']} / 5.0")
    print(f"  • CSAT (>= 4 Stars)  : {metrics['csat_score']}%")
    print(f"  • NPS Benchmark      : {metrics['nps_score']:+.1f}")
    print(f"  • Critical Incidents : {metrics['critical_issues_count']} pending")

    insights = FeedbackAnalytics.generate_frequent_feedback_summary(current_records)
    print(f"  • Top Praise Themes  : {[p[0] for p in insights['top_praise_phrases'][:3]]}")
    print(f"  • Top Complaint Themes: {[c[0] for c in insights['top_complaint_phrases'][:3]]}")

    # 6. Bulk Ingestion with row-by-row error logging
    print("\n[Step 6] Testing Bulk CSV Ingestion with Dirty Row Logging:")
    import_summary = BulkDatasetImporter.import_csv("data/test_corrupted_import.csv", storage=fresh_storage, commit=False)
    print(f"  • Processed Rows : {import_summary.total_rows_read}")
    print(f"  • Valid Rows     : {import_summary.successful_rows} accepted")
    print(f"  • Corrupted Rows : {import_summary.failed_rows} rejected and logged")
    print(f"  • First Error Log: Row #{import_summary.errors[0]['row_index']} - {import_summary.errors[0]['reasons']}")

    # 7. Multi-Format Export
    print("\n[Step 7] Generating Multi-Format Summary Exports:")
    md = ReportExporter.export_markdown_summary(current_records, "reports/demo_summary.md")
    csv_f = ReportExporter.export_standardized_csv(current_records, "reports/demo_export.csv")
    charts = ReportExporter.generate_charts(current_records, "reports/charts")
    print(f"  ✓ Markdown Report : {md}")
    print(f"  ✓ Standardized CSV: {csv_f}")
    print(f"  ✓ Visual Charts   : {len(charts)} chart images generated in reports/charts/")

    # Clean up demo record
    fresh_storage.delete_record("DEMO-999")

    print("\n" + "=" * 75)
    print(" ✅ END-TO-END DEMO WALKTHROUGH COMPLETED SUCCESSFULLY!")
    print(" All Must-Have & Stretch features demonstrated fault-tolerantly.")
    print("=" * 75 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="DataSpark Challenge #84: Customer Feedback Summary & Retail Analytics"
    )
    parser.add_argument("--gui", action="store_true", help="Launch interactive Tkinter desktop GUI")
    parser.add_argument("--web", action="store_true", help="Launch interactive Web Dashboard (Flask)")
    parser.add_argument("--port", type=int, default=5000, help="Web server port (default: 5000)")
    parser.add_argument("--demo", action="store_true", help="Run automated end-to-end hackathon demo")
    parser.add_argument("--summary", action="store_true", help="Print executive summary metrics and exit")
    parser.add_argument("--export", action="store_true", help="Export Markdown, CSV, TXT reports and charts")
    parser.add_argument("--import-csv", dest="import_file", type=str, help="Ingest legacy CSV file")

    args = parser.parse_args()
    storage = StorageManager()

    if args.demo:
        run_automated_demo()
        return

    if args.summary:
        records = storage.load_records()
        metrics = FeedbackAnalytics.compute_rating_metrics(records)
        print("\nEXECUTIVE CUSTOMER SATISFACTION SUMMARY:")
        print(f" Total Feedback Entries : {metrics['total_records']}")
        print(f" Overall Average Rating : ★ {metrics['average_rating']} / 5.0")
        print(f" CSAT Satisfaction Rate : {metrics['csat_score']}%")
        print(f" Net Promoter Score     : {metrics['nps_score']:+.1f}")
        print(f" Critical Issues        : {metrics['critical_issues_count']}")
        return

    if args.export:
        records = storage.load_records()
        print("Exporting summary reports and visualizations...")
        ReportExporter.export_markdown_summary(records)
        ReportExporter.export_plain_text_audit(records)
        ReportExporter.export_standardized_csv(records)
        charts = ReportExporter.generate_charts(records)
        print(f"Done! Exported to 'reports/' with {len(charts)} charts.")
        return

    if args.import_file:
        print(f"Ingesting CSV dataset: {args.import_file}")
        summary = BulkDatasetImporter.import_csv(args.import_file, storage=storage, commit=True)
        print(summary.generate_report())
        return

    if args.gui:
        try:
            from src.gui import FeedbackGUIApp
            FeedbackGUIApp.launch(storage)
        except Exception as e:
            print(f"[!] Error launching GUI: {e}")
            print("Falling back to interactive terminal UI...")
            cli = FeedbackCLI(storage)
            cli.run()
        return

    if args.web:
        from src.web_app import run_web_server
        run_web_server(port=args.port)
        return

    # Default: Interactive Terminal CLI
    cli = FeedbackCLI(storage)
    cli.run()


if __name__ == "__main__":
    main()
