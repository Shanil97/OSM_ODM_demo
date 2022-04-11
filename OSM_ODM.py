import streamlit as st
import numpy as np
import pandas as pd
import geopandas as gpd
import pydeck as pdk


# read data
df = gpd.read_file(r"C:\Users\Shanil\Desktop\BigQuery_to_S3\data\OD_OSM.csv")
df['people'] = df['people'].astype(int)
df['geometry'] = gpd.GeoSeries.from_wkt(df['line'])

# getting unique values for filters
origin = df['origin'].drop_duplicates()
destination = df['destination'].drop_duplicates()

# adding filters
origin_choice = st.sidebar.multiselect('Select Origin:', origin, default = origin)
destination_choice = st.sidebar.multiselect('Select Destination:', destination, default= destination)
people_count_choice = st.sidebar.slider('people_count_choice:', min_value=0, max_value=700, step=50, value = 0)


# assign filters to the dataframe
df = df[df['origin'].isin(origin_choice)]
df = df[df['destination'].isin(destination_choice)]
df = df[df['people'] >= people_count_choice]


# color coding
def color_selector(people):
    if people >= 500:
        col = [88, 24, 69]
    elif people >= 350:
        col = [144, 12, 63]
    elif people >= 200:
        col = [199, 0, 57]
    else:
        col = [255, 87, 51]

    return col

# applying color coding function
df['color'] = df['people'].apply(color_selector)

# Function that extracts the 2d list of coordinates from an input geometry
def my_geom_coord_extractor(input_geom):
    if (input_geom is None) or (input_geom is np.nan):
        return []
    else:
        if input_geom.type[:len('multi')].lower() == 'multi':
            full_coord_list = []
            for geom_part in input_geom.geoms:
                geom_part_2d_coords = [[coord[0],coord[1]] for coord in list(geom_part.coords)]
                full_coord_list.append(geom_part_2d_coords)
        else:
            full_coord_list = [[coord[0],coord[1]] for coord in list(input_geom.coords)]
        return full_coord_list

# Applying the coordinate list extractor to the dataframe
df['coord_list'] = df['geometry'].apply(my_geom_coord_extractor)

# deck.gl layer

layer = pdk.Layer(
    type="PathLayer",
    data=df,
    pickable=True,
    #get_color="[(people/10)*4, (people/10)*4, (people/10)*4]",
    get_color="color",
    width_scale=20,
    width_min_pixels=2,
    get_path='coord_list',
    get_width=4,
)
view_state = pdk.ViewState(latitude=6.9271, longitude=79.8612, zoom=12)
r = pdk.Deck(layers=[layer], initial_view_state=view_state, map_style='light', tooltip={"text":  "Way_id: {via_id}\n People: {people} \nOrigin: {origin} \nDestination: {destination}"})

# Creating visual layer
st.title(f"Origin Destination Matrix with Routes")
st.markdown('Geo view')
#st.write(r)
st.pydeck_chart(r)

print(df)