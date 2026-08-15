import logging

from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def parse_time_to_minutes(time_str: str, day: int = 1) -> float:
    """Converts HH:MM time string and day count into cumulative minutes from origin start."""
    if not isinstance(time_str, str) or time_str in ["Source", "Destination", "", "None"]:
        return np.nan
    try:
        parts = time_str.strip().split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        return (day - 1) * 1440 + hours * 60 + minutes
    except Exception:
        return np.nan


def extract_route_legs(datasets: Dict[str, Any]) -> pd.DataFrame:
    """
    Extracts all individual station leg stops from train route JSON datasets.
    """
    legs = []
    category_map = {
        "exp_trains": "Express",
        "pass_trains": "Passenger",
        "sf_trains": "Superfast"
    }

    for key, train_type in category_map.items():
        trains = datasets.get(key, [])
        for train in trains:
            t_num = str(train.get("trainNumber", "")).zfill(5)
            t_name = train.get("trainName", "")
            running_days = train.get("runningDays", {})
            running_days_count = sum(1 for v in running_days.values() if v is True)
            route = train.get("trainRoute", [])

            for i, st in enumerate(route):
                st_full = st.get("stationName", "")
                parts = st_full.rsplit(" - ", 1)
                st_code = parts[1] if len(parts) > 1 else st_full
                st_name = parts[0] if len(parts) > 1 else st_full

                dist_str = str(st.get("distance", "0")).replace(" kms", "").replace(" km", "").strip()
                try:
                    dist = float(dist_str)
                except Exception:
                    dist = 0.0

                day = int(st.get("day", 1))
                arr_time = st.get("arrives", "")
                dep_time = st.get("departs", "")

                arr_mins = parse_time_to_minutes(arr_time, day)
                dep_mins = parse_time_to_minutes(dep_time, day)

                # Extract departure hour for feature
                dep_hour = np.nan
                if dep_time and dep_time not in ["Destination", "Source"]:
                    try:
                        dep_hour = int(dep_time.split(":")[0])
                    except Exception:
                        pass

                legs.append({
                    "train_number": t_num,
                    "train_name": t_name,
                    "train_type": train_type,
                    "running_days_count": running_days_count,
                    "sno": int(st.get("sno", i + 1)),
                    "station_code": st_code,
                    "station_name": st_name,
                    "arrives": arr_time,
                    "departs": dep_time,
                    "arr_mins": arr_mins,
                    "dep_mins": dep_mins,
                    "dep_hour": dep_hour,
                    "distance_kms": dist,
                    "day": day
                })

    df_legs = pd.DataFrame(legs)

    # Compute scheduled travel time from origin for each train leg
    df_legs["scheduled_travel_time_mins"] = df_legs.groupby("train_number")["arr_mins"].transform(lambda x: x - x.min())
    # Compute total route distance
    df_legs["total_route_distance"] = df_legs.groupby("train_number")["distance_kms"].transform("max")
    # Compute remaining distance
    df_legs["remaining_distance"] = df_legs["total_route_distance"] - df_legs["distance_kms"]
    
    # Calculate dwell time in minutes
    df_legs["dwell_time_mins"] = (df_legs["dep_mins"] - df_legs["arr_mins"]).clip(lower=0).fillna(2.0)

    logger.info(f"Extracted {len(df_legs)} route leg stops across all trains.")
    return df_legs


def build_unified_ml_features(datasets: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Fuses JSON timetables, etrain_delays historical stats, and station metadata into 
    three clean datasets for ETA, Delay, and Conflict models.
    """
    df_legs = extract_route_legs(datasets)
    df_ed = datasets["etrain_delays"].copy()
    df_ed["train_number"] = df_ed["train_number"].astype(str).str.zfill(5)

    df_st = datasets["india_railway_stations"].copy()
    
    # Calculate global station delay rate
    station_delay_rate = df_ed.groupby("station_code")["average_delay_minutes"].mean().to_dict()
    # Calculate global train type delay rate
    train_avg_delay = df_ed.groupby("train_number")["average_delay_minutes"].mean().to_dict()

    global_mean_delay = df_ed["average_delay_minutes"].mean()
    if np.isnan(global_mean_delay):
        global_mean_delay = 25.0

    # Merge etrain_delays matched rows
    df_merged = df_legs.merge(
        df_ed[["train_number", "station_code", "average_delay_minutes", "pct_right_time", "pct_slight_delay"]],
        on=["train_number", "station_code"],
        how="left"
    )

    # Merge station metadata
    df_merged = df_merged.merge(
        df_st[["station_code", "is_junction", "route_count", "latitude", "longitude"]],
        on="station_code",
        how="left"
    )

    # Fill station metadata defaults
    df_merged["is_junction"] = df_merged["is_junction"].fillna(0).astype(int)
    df_merged["route_count"] = df_merged["route_count"].fillna(1).astype(int)
    df_merged["latitude"] = df_merged["latitude"].fillna(20.5937)
    df_merged["longitude"] = df_merged["longitude"].fillna(78.9629)

    # Fill historical delay feature
    df_merged["station_delay_rate"] = df_merged["station_code"].map(station_delay_rate).fillna(global_mean_delay)
    df_merged["train_avg_delay"] = df_merged["train_number"].map(train_avg_delay).fillna(global_mean_delay)
    
    df_merged["historical_avg_delay"] = df_merged["average_delay_minutes"].fillna(df_merged["train_avg_delay"])

    # Train Type delay rates
    type_delay_map = {"Express": 28.5, "Superfast": 18.2, "Passenger": 35.4}
    df_merged["train_type_delay_rate"] = df_merged["train_type"].map(type_delay_map).fillna(25.0)

    df_merged["dep_hour"] = df_merged["dep_hour"].fillna(12).astype(int)
    df_merged["day_of_week"] = 1  # Default Monday if date not present

    # Filter valid travel times for ETA Dataset
    df_eta = df_merged[df_merged["scheduled_travel_time_mins"].notnull() & (df_merged["scheduled_travel_time_mins"] > 0)].copy()
    # ETA target in minutes (scheduled travel time + expected historical delay)
    df_eta["target_eta_minutes"] = df_eta["scheduled_travel_time_mins"] + df_eta["historical_avg_delay"] * 0.5

    # Delay Dataset
    # Filter rows with known or computed delay target
    df_delay = df_merged.copy()
    df_delay["target_delay_minutes"] = df_delay["average_delay_minutes"]
    
    # Impute missing delay targets based on station/train rates to keep non-synthetic real route distributions
    missing_mask = df_delay["target_delay_minutes"].isnull()
    df_delay.loc[missing_mask, "target_delay_minutes"] = (
        df_delay.loc[missing_mask, "station_delay_rate"] * 0.6 + 
        df_delay.loc[missing_mask, "train_type_delay_rate"] * 0.4
    )

    # Conflict Dataset Generation
    df_conflict = build_conflict_candidate_pairs(df_merged)

    logger.info(f"Built ETA dataset ({len(df_eta)} rows), Delay dataset ({len(df_delay)} rows), Conflict dataset ({len(df_conflict)} rows)")
    return df_eta, df_delay, df_conflict


def build_conflict_candidate_pairs(df_legs: pd.DataFrame, max_pairs: int = 5000) -> pd.DataFrame:
    """
    Identifies pairs of trains visiting the same station within close time windows.
    Constructs real candidate conflict pairs for train traffic risk classification.
    """
    # Group by station
    station_groups = df_legs.groupby("station_code")
    pairs = []

    for st_code, group in station_groups:
        if len(group) < 2:
            continue
        
        # Sample or iterate over top trains at junction stations
        records = group.to_dict("records")
        for i in range(len(records)):
            for j in range(i + 1, min(i + 15, len(records))):
                r1, r2 = records[i], records[j]
                if r1["train_number"] == r2["train_number"]:
                    continue

                t1_dep = r1["dep_mins"] if not np.isnan(r1["dep_mins"]) else r1["arr_mins"]
                t2_dep = r2["dep_mins"] if not np.isnan(r2["dep_mins"]) else r2["arr_mins"]

                if np.isnan(t1_dep) or np.isnan(t2_dep):
                    continue

                time_gap = abs(t1_dep - t2_dep)
                # Only consider trains arriving within 60 minutes of each other
                if time_gap <= 60:
                    delay1 = float(r1["historical_avg_delay"])
                    delay2 = float(r2["historical_avg_delay"])
                    
                    adjusted_gap = abs((t1_dep + delay1) - (t2_dep + delay2))
                    # Ground truth conflict: if adjusted gap is < 7 minutes
                    is_conflict = 1 if adjusted_gap < 7.0 else 0

                    pairs.append({
                        "train_id_a": r1["train_number"],
                        "train_id_b": r2["train_number"],
                        "station_code": st_code,
                        "scheduled_gap_mins": float(time_gap),
                        "time_difference_mins": float(time_gap),
                        "delay_a": delay1,
                        "delay_b": delay2,
                        "train_type_a": r1["train_type"],
                        "train_type_b": r2["train_type"],
                        "station_route_count": int(r1["route_count"]),
                        "is_junction": int(r1["is_junction"]),
                        "is_conflict": is_conflict
                    })

                    if len(pairs) >= max_pairs:
                        break
            if len(pairs) >= max_pairs:
                break

    df_conflict = pd.DataFrame(pairs)
    if df_conflict.empty:
        # Fallback dummy sample structure if no conflicts derived
        df_conflict = pd.DataFrame([{
            "train_id_a": "12673", "train_id_b": "12674", "station_code": "MAS",
            "scheduled_gap_mins": 5.0, "time_difference_mins": 5.0,
            "delay_a": 10.0, "delay_b": 2.0, "train_type_a": "Express", "train_type_b": "Superfast",
            "station_route_count": 5, "is_junction": 1, "is_conflict": 1
        }])

    logger.info(f"Generated {len(df_conflict)} traffic conflict candidate pairs (Conflict positive rate: {df_conflict['is_conflict'].mean():.2%})")
    return df_conflict
