
address_to_state_processor.py does the following tasks:

•	Reads the address, state shapefile location (downloaded from census tiger files), postgres database hostname, username, password, google maps api key from the command line.

•	Reads the google maps api with a key embedded and retrieves the latitude and longitude coordinates for the address.

•	Connects to the postgres database using the valid connections provided above.

•	Creates a table called “states” to be filled with state geometries and attribute fields from the shape file.

•	Creates a table called “points” to be filled with the latitude, longitude coordinates from the address.

•	Opens the shape file and converts the polygon features to well-known text (wkt) geometry format.

•	Inserts the shape file wkt geometries and state name for each geometry into the “states” table using postgis functions.

•	Creates a point geometry using latitude, longitude coordinates and inserts into the table “points” using postgis functions.

•	Executes a spatial join to find the state from the “states” geometry where the “point” geometry is contained in using postgis functions.

•	Writes out the “name” of the state.

Code Execution:

•	User needs to first create a postgres database called states_us with a postgis extension. If the database name is different than specified, an input parameter in line 30 of the code needs to be changed accordingly. 

•	Copy the code to a local drive. 

•	Create a python anaconda virtual environment.

•	Install the following libraries within the virtual environment – flask, requests, psycopg2, osgeo.ogr, argparse, sys

•	Install postgres database with postgis extension.

•	Run the code within the virtual environment command line interface as below:

python address_to_state_processor.py "provide_address" "provide_path_to_shapefile_location" "provide_postgres_hostname" "provide_postgres_username" "provide_postgres_password" "provide_google_maps_api_key"

•	Example code execution:

python address_to_state_processor.py "4 Pennsylvania Plaza" "C:/Docs/state_shp/tl_2019_us_state.shp" "localhost" "postgres" "P@34Ssw05rD" "4sxtTRIS..."

•	The code runs on a local host server. Go to http://127.0.0.1:5000/ to see the result.

•	Press “CTRL+C” to exit the run.
