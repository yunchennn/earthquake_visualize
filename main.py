# Import Deps
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Data source: https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{???}.csv

def extract_subarea(place):
    return place[0]

def extract_area(place):
    return place[-1]

def extract_date(time):
    return str(time).split(' ')[0]

def extract_weekday(time):
    date = extract_date(time)
    return date+'-'+str(time.weekday())

def extract_hour(time):
    t = str(time).split(' ')
    return t[0]+'-'+t[1].split(':')[0]

# Fetch data and clean it
def fetch_eq_data(period='daily', region='Worldwide', min_mag=1):
    # Where we are getting data from
    url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{}.csv'

    if period == 'weekly':
        new_url = url.format('all_week')
    elif period == 'monthly':
        new_url = url.format('all_month')
    else:
        new_url = url.format('all_day')

    # Fetch data and extract relevant cols
    df_earthquake = pd.read_csv(new_url)
    df_earthquake = df_earthquake[['time', 'latitude', 'longitude', 'mag', 'place']]

    # Extract sub-area in place cols
    place_list = df_earthquake['place'].str.split(', ')    
    df_earthquake['sub_area'] = place_list.apply(extract_subarea)
    df_earthquake['area'] = place_list.apply(extract_area)
    df_earthquake = df_earthquake.drop(columns=['place'], axis=1)

    # Filter data based on min. threshold
    if isinstance(min_mag, int) and min_mag > 0:
        df_earthquake = df_earthquake[df_earthquake['mag'] >= min_mag]
    else:
        df_earthquake = df_earthquake[df_earthquake['mag'] > 0]

    # Convert 'time' to pd datetime
    df_earthquake['time'] = pd.to_datetime(df_earthquake['time'])
    
    # Set lat and long to some default if not found
    if region in df_earthquake['area'].to_list():
        df_earthquake = df_earthquake[df_earthquake['area'] == region]
        max_mag = df_earthquake['mag'].max()
        center_lat = df_earthquake[df_earthquake['mag'] == max_mag]['latitude'].values[0]
        center_long = df_earthquake[df_earthquake['mag'] == max_mag]['longitude'].values[0]
    else:
        center_lat, center_long = [54,15]

    if period == 'weekly':
        animation_frame_col = 'weekday'
        df_earthquake[animation_frame_col] = df_earthquake['time'].apply(extract_weekday)
    elif period == 'monthly':
        animation_frame_col = 'date'
        df_earthquake[animation_frame_col] = df_earthquake['time'].apply(extract_date)
    else:
        animation_frame_col = 'hours'
        df_earthquake[animation_frame_col] = df_earthquake['time'].apply(extract_hour)

    df_earthquake = df_earthquake.sort_values(by='time')

    return df_earthquake, center_lat, center_long

#create visualizer

def visualize_eq_data(period='daily', region='Worldwide', min_mag=1):
    df_earthquake, center_lat, center_long = fetch_eq_data(period=period, region=region,min_mag=min_mag)

    if period == 'monthly':
        animation_frame_col = 'date'
    elif period == 'weekly':
        animation_frame_col = 'weekday'
    else:
        animation_frame_col = 'hours'

    fig = px.scatter_mapbox(
        data_frame=df_earthquake,
        lat='latitude',
        lon='longitude',
        center=dict(lat=center_lat, lon=center_long),
        size='mag',
        color='mag',
        hover_name='sub_area',
        zoom=1,
        mapbox_style='carto-positron',
        animation_frame=animation_frame_col,
        title='Earthquakes'
    )

    fig.show()

    return None
# visualize_eq_data(period= 'monthly', region='Worldwide',min_mag=1)
visualize_eq_data()


