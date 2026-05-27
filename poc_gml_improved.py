import csv
import json
import math
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def bbox_for_polygon(poly):
    lats = [p["lat"] for p in poly]
    lons = [p["lon"] for p in poly]
    return min(lats), max(lats), min(lons), max(lons)


def in_bbox(lat, lon, bbox):
    min_lat, max_lat, min_lon, max_lon = bbox
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def point_in_polygon(lat, lon, polygon):
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        yi, xi = polygon[i]["lat"], polygon[i]["lon"]
        yj, xj = polygon[j]["lat"], polygon[j]["lon"]
        crosses = (xi > lon) != (xj > lon)
        if crosses:
            intersect_lat = (yj - yi) * (lon - xi) / (xj - xi) + yi
            if lat < intersect_lat:
                inside = not inside
        j = i
    return inside


def run_zfe():
    data = load_json("data_geo.json")
    polygon = data["zfe_polygon"]
    bbox = bbox_for_polygon(polygon)
    alerts = []
    for point in data["truck_path"]:
        lat, lon = point["lat"], point["lon"]
        is_inside = in_bbox(lat, lon, bbox) and point_in_polygon(lat, lon, polygon)
        if is_inside:
            msg = f"[ALERT ZFE] camion={point['id']} timestamp={point['timestamp']} lat={lat} lon={lon}"
            print(msg)
            alerts.append(point)
    return alerts


def run_safety(threshold_g=2.5):
    events = []
    with open("accelerometer_data.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ax = float(row["acc_x"])
            ay = float(row["acc_y"])
            dynamic_g = math.sqrt(ax * ax + ay * ay)  # on ignore la gravité verticale pour le score freinage/virage
            if dynamic_g > threshold_g:
                event = {
                    "timestamp": row["timestamp"],
                    "dynamic_g": round(dynamic_g, 2),
                    "type": "hard_braking_or_evasive_manoeuvre",
                    "severity": "critical" if dynamic_g >= 3.0 else "warning",
                }
                print(f"[ALERT SAFETY] {event}")
                events.append(event)
    Path("daily_score.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    return events


if __name__ == "__main__":
    run_zfe()
    run_safety()
