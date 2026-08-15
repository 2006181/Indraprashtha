import json
import logging
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import numpy as np

from ml.config import REPORT_DIR
from ml.data_loader import RailwayDataLoader

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Automated Data Quality Validation Suite for Railway Datasets.
    Performs comprehensive data health checks and produces JSON and Markdown reports.
    """

    def __init__(self, data_loader: RailwayDataLoader):
        self.loader = data_loader
        self.report_dir = REPORT_DIR

    def validate_all(self) -> Dict[str, Any]:
        datasets = self.loader.load_all_datasets()
        report = {
            "summary": {"total_files_validated": 0, "total_issues_found": 0},
            "datasets": {}
        }

        # 1. Validate etrain_delays.csv
        df_ed = datasets["etrain_delays"]
        ed_checks = self._validate_etrain_delays(df_ed)
        report["datasets"]["etrain_delays.csv"] = ed_checks

        # 2. Validate Train_delay_Prediction.csv
        df_tdp = datasets["train_delay_prediction"]
        tdp_checks = self._validate_train_delay_prediction(df_tdp)
        report["datasets"]["Train_delay_Prediction.csv"] = tdp_checks

        # 3. Validate india_railway_stations
        df_st = datasets["india_railway_stations"]
        st_checks = self._validate_stations(df_st)
        report["datasets"]["india_railway_stations"] = st_checks

        # 4. Validate Train Schedule JSONs
        exp = datasets["exp_trains"]
        pas = datasets["pass_trains"]
        sf = datasets["sf_trains"]
        json_checks = self._validate_train_schedules(exp, pas, sf)
        report["datasets"]["train_schedules_json"] = json_checks

        # 5. Validate Excel Scheduling Data
        excel_data = datasets["scheduling_excel"]
        excel_checks = self._validate_scheduling_excel(excel_data)
        report["datasets"]["Railway_Scheduling_Data.xlsx"] = excel_checks

        # Summarize issues
        total_issues = sum(d.get("issues_count", 0) for d in report["datasets"].values())
        report["summary"]["total_files_validated"] = len(report["datasets"])
        report["summary"]["total_issues_found"] = total_issues

        self.save_reports(report)
        return report

    def _validate_etrain_delays(self, df: pd.DataFrame) -> Dict[str, Any]:
        null_counts = df.isnull().sum().to_dict()
        duplicates = int(df.duplicated().sum())
        negative_delays = int((df["average_delay_minutes"] < 0).sum())
        invalid_pcts = int(((df["pct_right_time"] < 0) | (df["pct_right_time"] > 100)).sum())

        issues = []
        if null_counts.get("average_delay_minutes", 0) > 0:
            issues.append(f"Missing average_delay_minutes in {null_counts['average_delay_minutes']} rows.")
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate rows.")
        if negative_delays > 0:
            issues.append(f"Found {negative_delays} negative delay values.")

        return {
            "row_count": len(df),
            "col_count": len(df.columns),
            "unique_trains": int(df["train_number"].nunique()),
            "unique_stations": int(df["station_code"].nunique()),
            "null_counts": null_counts,
            "duplicate_rows": duplicates,
            "issues_count": len(issues),
            "issues": issues
        }

    def _validate_train_delay_prediction(self, df: pd.DataFrame) -> Dict[str, Any]:
        null_counts = df.isnull().sum().to_dict()
        duplicates = int(df.duplicated().sum())
        issues = []
        if null_counts.get("Started On", 0) > 0:
            issues.append(f"Missing 'Started On' timestamp in {null_counts['Started On']} rows.")

        return {
            "row_count": len(df),
            "col_count": len(df.columns),
            "null_counts": null_counts,
            "duplicate_rows": duplicates,
            "issues_count": len(issues),
            "issues": issues
        }

    def _validate_stations(self, df: pd.DataFrame) -> Dict[str, Any]:
        null_counts = df.isnull().sum().to_dict()
        duplicates = int(df.duplicated().sum())
        invalid_coords = int(((df["latitude"] < -90) | (df["latitude"] > 90) | (df["longitude"] < -180) | (df["longitude"] > 180)).sum())
        
        issues = []
        if null_counts.get("latitude", 0) > 0:
            issues.append(f"Missing coordinates for {null_counts['latitude']} stations.")
        if invalid_coords > 0:
            issues.append(f"Invalid coordinates for {invalid_coords} stations.")

        return {
            "row_count": len(df),
            "unique_stations": int(df["station_code"].nunique()),
            "junction_count": int(df["is_junction"].sum()) if "is_junction" in df.columns else 0,
            "null_counts": null_counts,
            "duplicate_rows": duplicates,
            "issues_count": len(issues),
            "issues": issues
        }

    def _validate_train_schedules(self, exp: List[Dict], pas: List[Dict], sf: List[Dict]) -> Dict[str, Any]:
        total_trains = len(exp) + len(pas) + len(sf)
        empty_routes = 0
        total_stops = 0

        for train_list in [exp, pas, sf]:
            for t in train_list:
                route = t.get("trainRoute", [])
                if not route:
                    empty_routes += 1
                total_stops += len(route)

        issues = []
        if empty_routes > 0:
            issues.append(f"Found {empty_routes} trains with empty routes.")

        return {
            "total_trains": total_trains,
            "express_trains": len(exp),
            "passenger_trains": len(pas),
            "superfast_trains": len(sf),
            "total_route_leg_stops": total_stops,
            "empty_routes": empty_routes,
            "issues_count": len(issues),
            "issues": issues
        }

    def _validate_scheduling_excel(self, excel_data: Any) -> Dict[str, Any]:
        issues = []
        if isinstance(excel_data, dict):
            df = list(excel_data.values())[0]
        else:
            df = excel_data

        null_counts = df.isnull().sum().to_dict()
        invalid_speeds = int((df["speed_kmh"] <= 0).sum()) if "speed_kmh" in df.columns else 0
        if invalid_speeds > 0:
            issues.append(f"Found {invalid_speeds} trains with speed <= 0.")

        return {
            "row_count": len(df),
            "columns": list(df.columns),
            "null_counts": null_counts,
            "issues_count": len(issues),
            "issues": issues
        }

    def save_reports(self, report: Dict[str, Any]):
        self.report_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.report_dir / "data_quality_report.json"
        md_path = self.report_dir / "data_quality_report.md"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # Markdown Report Generation
        md_lines = [
            "# Data Quality & Health Validation Report",
            "## Summary",
            f"- **Total Datasets Validated**: {report['summary']['total_files_validated']}",
            f"- **Total Issues Identified**: {report['summary']['total_issues_found']}",
            "",
            "## Dataset Details",
        ]

        for name, info in report["datasets"].items():
            md_lines.append(f"### {name}")
            for k, v in info.items():
                if k not in ["issues", "null_counts"]:
                    md_lines.append(f"- **{k.replace('_', ' ').title()}**: {v}")
            if info.get("issues"):
                md_lines.append("- **Issues Identified**:")
                for issue in info["issues"]:
                    md_lines.append(f"  - ⚠️ {issue}")
            else:
                md_lines.append("- **Status**: ✅ Clean / Valid")
            md_lines.append("")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        logger.info(f"Saved Data Quality Reports to {json_path} and {md_path}")
