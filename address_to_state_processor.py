# author: Kash Sabba
"""
instructions to run the code:
create a python anaconda virtual environment with all the libraries specified below
install postgres database with postgis extension
run the code from command line as below:
python address_to_state_processor.py "provide_address" "provide_path_to_shapefile_location" "provide_postgres_hostname" "provide_postgres_username" "provide_postgres_password"
python address_to_state_processor.py "4 Pennsylvania Plaza" "C:/Docs/state_shp/tl_2019_us_state.shp" "localhost" "postgres" "P@34Ssw05rD"
Go to http://127.0.0.1:5000/ to see the result
"""
import flask
from flask import request, jsonify
import requests
import psycopg2
import osgeo.ogr
import argparse
import sys

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# input from the command line
address = sys.argv[1]
states_shapefile = sys.argv[2]
hostname = sys.argv[3]
username = sys.argv[4]
password = sys.argv[5]

# input parameters that need to be adjusted if needed (hardcoded for now)
dbname = 'states_us'

@app.route('/', methods=['GET'])
def homepage():
    # setting up google url and api with the key hardcoded
    google_url = 'https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyBKkmm-mDx-WM5X3pwuHPdnZJgFCMFhT3Y'
    params = {'sensor': 'false', 'address': address}

    # using the url to retrieve latitude and longitude for the address
    r = requests.get(google_url, params=params)
    results = r.json()['results']
    location = 0
    try:
        location = results[0]['geometry']['location']
        address_latitude = location['lat']
        address_longitude = location['lng']
    except IndexError:
        print("please provide a valid address within the US")

    # importing the state boundary shape file downloaded from census tigerline files
    state_shape = states_shapefile

    # setting up postgres database connection
    connection = psycopg2.connect(host=hostname, user=username, password=password, database=dbname)
    cursor = connection.cursor()

    # setting for the first states table to be imported with values from the shape file
    cursor.execute("DROP TABLE IF EXISTS states")
    cursor.execute("CREATE TABLE states (id SERIAL PRIMARY KEY, name TEXT NOT NULL, boundary GEOMETRY)")

    # setting up the second point coordinate table to be imported with values from the address lat/long
    cursor.execute("DROP TABLE IF EXISTS points")
    cursor.execute("CREATE TABLE points (id SERIAL PRIMARY KEY, geom GEOMETRY)")
    connection.commit()

    # open shape file and extract required attribute columns and
    # convert each state boundary to well known text and import into
    # the postgres table
    shapefile = osgeo.ogr.Open(state_shape)
    layer = shapefile.GetLayer(0)

    for row in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(row)

        # get only attribute fields of interest
        name = feature.GetField("NAME")

        # retrieve feature geometry
        geometry = feature.GetGeometryRef()

        # convert it to wkt format (well known text)
        wkt = geometry.ExportToWkt()

        # insert shape file contents into database table states, convert wkt geometry to postgis geometry
        cursor.execute("INSERT INTO states (name, boundary) " + "VALUES(%s, ST_GeometryFromText(%s, " + "4326))",
                       (name, wkt))
    connection.commit()

    # insert address coordinates into postgres database table points
    cursor.execute("INSERT INTO points (geom) " + "VALUES(ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
                   (address_longitude, address_latitude))

    # select state with the lat/long coordinate using point in poly spatial join
    sql = "SELECT states.name FROM states, points WHERE ST_Contains(states.boundary, points.geom)"
    cursor.execute(sql)

    # print out the state name
    final_result = address + " is in the State of " + cursor.fetchone()[0]
    return jsonify(final_result)

    # close the connection
    cursor.close()
    connection.close()

app.run()