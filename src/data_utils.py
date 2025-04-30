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
    # drop the null values, we will also be dropping any values that are not in the month that we are supposed to be looking at
    # i.e. if our month is 2022-05, the we will drop any values below that and above that
    df.dropna(inplace=True)
    # we get our boundaries, we will use the median since this will most likely contain the month that the dataset is supposed to be about
    median = df['tpep_pickup_datetime'].median()
    lower_bound = pd.to_datetime(f'{median.year}-{median.month}-01 00:00:01')
    if median.month == 2:
        upper_bound = pd.to_datetime(f'{median.year}-{median.month}-28 11:59:59')
    else:
        upper_bound = pd.to_datetime(f'{median.year}-{median.month}-30 11:59:59')
    
    # now with our boundaries, we drop any rows which date time is not within these bounds
    dates_pickup_idx = df[df['tpep_pickup_datetime'] < lower_bound].index
    dates_dropoff_idx = df[upper_bound < df['tpep_dropoff_datetime']].index

    # we drop from our table those values
    df.drop(dates_pickup_idx,inplace=True)
    df.drop(dates_dropoff_idx,inplace=True)

    # 2
    # drop the rows that contain negative values in their
    # fare_amount, or really small values
    idx_to_drop = df[df['fare_amount'] < 1].index
    df.drop(idx_to_drop, inplace=True)
    # also anything above 40, since most of our data is below this threshold
    idx_fare_low = df[df['fare_amount'] > 60.0].index
    df.drop(idx_fare_low, inplace=True)

    # 3
    # create a new column that contains the travel_time information
    df['travel_time'] = df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
    df['travel_time'] = df['travel_time'].dt.total_seconds()
    # now we drop the travel times around 5 hours
    idx_travel_time_big = df[df['travel_time'] > 4000.0].index
    df.drop(idx_travel_time_big, inplace=True)
    # we also drop travel times below 3 minutes
    idx_travel_time_small = df[df['travel_time'] < 180].index
    df.drop(idx_travel_time_small, inplace=True)

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
    # gdf = gp.read_file(config.DATASET_ZONE_GEOM)
    # gdf['centroids'] = gdf.centroid
    # gdf = gdf.to_crs('EPSG:32618')

    # def dist_between_zones(row):
    #     pu = int(row['PULocationID'])
    #     do = int(row['DOLocationID'])
    #     return gdf['centroids'].iloc[pu-1].distance(gdf['centroids'].iloc[do-1])
    # df['distance_between_zones'] = df.apply(dist_between_zones,axis=1)
    # # we also convert the distances to miles (they are originally in meters)
    # df['distance_between_zones'] = df['distance_between_zones']*0.000621371

    # 7 alternate
    # remove trip distances equal to 0
    idx_trip_distance_low = df[df['trip_distance'] == 0.0].index
    df.drop(idx_trip_distance_low, inplace=True)
    # also remove trip distances above 100 miles
    idx_trip_distance_high = df[df['trip_distance'] > 100.0].index
    df.drop(idx_trip_distance_high, inplace=True)

    # 8 finally we drop the columns that we might not need
    df.drop(columns=['VendorID','tpep_pickup_datetime','tpep_dropoff_datetime',
                   'RatecodeID','store_and_fwd_flag','payment_type','extra',
                   'mta_tax','tip_amount','tolls_amount','total_amount','PULocationID','DOLocationID',
                   'improvement_surcharge','airport_fee','congestion_surcharge'],inplace=True)
    
    return df

def sampled_yearly_data(files:list, n_samples:int):
    """
    This function return a df containing sampled data from all the specified file names in the list

    Arguments:
        files : list
            A list of path files containing all the files that want to be sampled

    Returns:
        df : pd.DataFrame
            Pandas dataframe containing the same amount of random sampling from the specified
            data frames
    """
    df_list = [clean_trip_data(file_path).sample(n=n_samples, random_state=42) for file_path in files]
    df = pd.concat(df_list, ignore_index=True)
    return df