import os
from pathlib import Path

DATASET_ROOT_PATH = str(Path(__file__).parent.parent / "data")
os.makedirs(DATASET_ROOT_PATH, exist_ok=True)

DATASET = str(Path(DATASET_ROOT_PATH) / "yellow_tripdata_2022-05.parquet")

DATASET_ZONE_GEOM = str(
    Path(DATASET_ROOT_PATH) / "taxi_zones/taxi_zones.shp"
)

DATASET_ZONE_DESCRIPTIONS = str(
    Path(DATASET_ROOT_PATH) / "taxi_zones/taxi_zone_lookup.csv"
)