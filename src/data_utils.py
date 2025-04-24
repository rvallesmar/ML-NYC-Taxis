import pandas as pd
import geopandas as gp
from sklearn.model_selection import train_test_split
from src import config
import os
from pathlib import Path
import requests

def download_zones_data(url:str):
    zip_url = url
    save_folder = str(Path(__file__).parent.parent / "data/taxi_zones")
    zip_filename = "zones.zip"
    save_path = os.path.join(save_folder, zip_filename)

    try:
        response = requests.get(zip_url, stream=True)
        response.raise_for_status()

        
        os.makedirs(save_folder, exist_ok=True)

        
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Zip file successfully downloaded from '{zip_url}' and saved to '{save_path}'")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading zip file from '{zip_url}': {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_feature_target(
    dataset: pd.DataFrame
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Separates our cleaned pandas dataframe columns between Features and Targets

    Arguments:
        dataset : pd.DataFrame
            Cleaned pandas dataframe containing trip data

    Returns:
        X : pd.DataFrame
            Training features
        y_travel_time : pd.Series
            Total travel time in seconds to be predicted
        y_fare_amount : pd.Series
            Fare amount of the trip to be predicted
    """

    X = dataset.drop(columns=['fare_amount','travel_time'])
    y_travel_time = dataset['travel_time']
    y_fare_amount = dataset['fare_amount']

    return X, y_travel_time, y_fare_amount

def get_train_test_sets(
    X: pd.DataFrame, y_travel_time: pd.Series, y_fare_amount:pd.Series
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Split dataset in two new sets used for training and testing.
    Can be used again to split dataset into training and validation
    datasets.

    Arguments:
        X : pd.DataFrame
            Original training features
        y_travel_time : pd.Series
            Original target array containing the travel_time data
        y_fare_amount : pd.Series
            Original target array containing the fare_amount data

    Returns:
        X_train : pd.DataFrame
            Training features
        X_test : pd.DataFrame
            Validation features
        y_train_travel_time : pd.Series
            Training target for travel time
        y_test_travel_time : pd.Series
            Validation target for travel time
        y_train_fare_amount : pd.Series
            Training target for fare amount
        y_test_fare_amount : pd.Series
            Validation target for fare amount
    """

    X_train, X_test, y_train_travel_time, y_test_travel_time, y_train_fare_amount, y_test_fare_amount = train_test_split(X,y_travel_time,y_fare_amount,
                                                      test_size=0.2, 
                                                      random_state=42, 
                                                      shuffle=True)

    return X_train, X_test, y_train_travel_time, y_test_travel_time, y_train_fare_amount, y_test_fare_amount

def clean_trip_data(filename) -> pd.DataFrame:
    """
    Function that takes in a filename containing the taxi trip information, the expectation is that
    the file is located in the data folder,
    and cleans it by removing unnecesarry columns, removing null values,
    plus adding some new ones.

    Arguments:
        filepath : str
            The path to the file containing the data

    Returns:
        df : pd.DataFrame
            Cleaned pandas dataframe
    """
    root_path = str(Path(__file__).parent.parent / "data")
    os.makedirs(root_path, exist_ok=True)
    raw_dataset = str(Path(root_path) / filename)

    df = pd.read_parquet(raw_dataset)
    # 1
    # drop the null values
    df.dropna(inplace=True)

    # 2
    # drop the rows that contain negative values in their
    # fare_amount
    idx_to_drop = df[df['fare_amount'] < 0].index
    df.drop(idx_to_drop, inplace=True)

    # 3
    # create a new column that contains the travel_time information
    df['travel_time'] = df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
    df['travel_time'] = df['travel_time'].dt.total_seconds()
    # now we drop the travel times around 5 hours
    idx_travel_time = df[df['travel_time'] > 18000].index
    df.drop(idx_travel_time, inplace=True)

    # 4
    # include a new categorical column called 'time_of_day' to establish whether
    # a trip happened during the morning, afternoon or at night
    def period_of_time(dt:pd.Timestamp):
        if dt.hour <= 7 or dt.hour >= 20:
            return 'night'
        elif dt.hour > 7 and dt.hour < 12:
            return 'morning'
        else:
            return 'afternoon'
    df['time_of_day'] = df['tpep_pickup_datetime'].apply(period_of_time)

    # 5
    # adding new column to indicate the day of the month, month number, and to indicate
    # whether the trip took place on a weekend or not
    df['day'] = df['tpep_dropoff_datetime'].dt.day
    df['month'] = df['tpep_dropoff_datetime'].dt.month
    def is_weekend(dt:pd.Timestamp):
        if dt.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return 1
        else:
            return 0
    df['is_weekend'] = df['tpep_dropoff_datetime'].apply(is_weekend)

    # 6
    # since we will augment our dataset with distances
    # between zones, we need to drop the zone codes 264 and
    # 265 since those are unknown and out of NY respectively
    remove_zones = (df['DOLocationID'] == 264) | (df['DOLocationID'] == 265) | (df['PULocationID'] == 264) | (df['PULocationID'] == 265)
    df = df[~remove_zones]

    # 7
    # now we will augment out dataset including the distance between the
    # centroids of each zone based on their geometry
    # we can get that from the .shp file
    gdf = gp.read_file(config.DATASET_ZONE_GEOM)
    gdf['centroids'] = gdf.centroid
    gdf = gdf.to_crs('EPSG:32618')

    def dist_between_zones(row):
        pu = int(row['PULocationID'])
        do = int(row['DOLocationID'])
        return gdf['centroids'].iloc[pu-1].distance(gdf['centroids'].iloc[do-1])
    df['distance_between_zones'] = df.apply(dist_between_zones,axis=1)
    # we also convert the distances to miles (they are originally in meters)
    df['distance_between_zones'] = df['distance_between_zones']*0.000621371

    # 8 finally we drop the columns that we might not need
    df.drop(columns=['VendorID','tpep_pickup_datetime','tpep_dropoff_datetime','passenger_count',
                   'RatecodeID','store_and_fwd_flag','payment_type','extra',
                   'mta_tax','tip_amount','tolls_amount','total_amount','trip_distance'],inplace=True)
    
    return df
