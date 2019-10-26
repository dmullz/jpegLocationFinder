from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.styles import Font
import requests
import os

HERE_APP_ID = "vQCC4M7DiyR3w4sNySuk"
HERE_APP_CODE = "J0hDHbYEc9lf5WXlXszxCw"

# @DEV - Function to add a row to the excel file
# @param excel - string of file location of excel document
# @param filename - string of path to an image file
# @param location - string of the zip code parsed from image file
def add_to_excel(excel,filename,location):
	# Format row
	new_row = [filename,location]
        
    # Load excel or build excel if this is the first one
	try:
		workbook = load_workbook(excel)
		worksheet = workbook.worksheets[0]
	except FileNotFoundError:
		headers_row = ["Image File", "Zip Code"]
		font = Font(bold=True)
		workbook = Workbook()
		worksheet = workbook.active
		worksheet.append(headers_row)
		for cell in worksheet["1:1"]:
			cell.font = font
	
	# Add row to Excel doc
	worksheet.append(new_row)
	workbook.save(excel)

# @DEV - Generator to get the next image file
# @param dir - directory containing image files (or singular file)
# @RET (string) - Yields a file to attempt to decode
def image_gen(dir):
	if os.path.isfile(dir):
		yield dir
	else:
		files = []
		for (dirpath, dirnames, filenames) in os.walk(dir):
			files.extend(filenames)
			break
		
		for file in files:
			yield file

# @DEV - Function to find geotagging data in EXIF data
# @param exif - dictionary of EXIF data from a JPEG image
# @RET (dict) - returns a dictionary of geotagging data
def get_geotagging(exif):
	if not exif:
		raise ValueError("No EXIF metadata found")
	print(GPSTAGS.items())
	geotagging = {}
	for (idx, tag) in TAGS.items():
		if tag == 'GPSInfo':
			if idx not in exif:
				return None
			for (key, val) in GPSTAGS.items():
				if key in exif[idx]:
					geotagging[val] = exif[idx][key]

	return geotagging

# @DEV - Function to get the EXIF data in an image file.
# @param filename - string containing the path to a file
# @RET (dict) - returns a dictionary of EXIF data, or None if the file cannot be read or is not a JPEG
def get_exif(filename):
	try:
		image = Image.open(filename)
		image.verify()
		print("Image Info", image.info)
		if image.format.lower() != 'jpeg':
			print("File", filename, "is not a JPEG.")
			return None
		exif = image._getexif()
		print("exif:",exif)
		return exif
	except:
		print("There was a problem reading file", filename)
		return None

# @DEV - Function to convert degrees, minutes, and seconds to a latitude/longitude
# @param dms - matrix of degrees, minutes, and seconds data
# @param ref - string of bearing information (N,S,E,W)
# @RET (float) - returns a float representing latitude/longitude coordinates
def get_decimal_from_dms(dms, ref):

	degrees = dms[0][0] / dms[0][1]
	minutes = dms[1][0] / dms[1][1] / 60.0
	seconds = dms[2][0] / dms[2][1] / 3600.0

	if ref in ['S', 'W']:
		degrees = -degrees
		minutes = -minutes
		seconds = -seconds

	return round(degrees + minutes + seconds, 5)

# @DEV - Function to get latitude/longitude from geotagging data
# @param geotags - dictionary of geotagging data
# @RET (tuple) - returns floats of latitude and longitude coordinates
def get_coordinates(geotags):
	lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])

	lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])

	return (lat,lon)

# @DEV - Function to find location data from geotagging data in a JPEG
# @param geotags - dictionary of geotagging data
# @RET (dictionary) - returns JSON containing location data for the image
def get_location(geotags):
	coords = get_coordinates(geotags)

	uri = 'https://reverse.geocoder.api.here.com/6.2/reversegeocode.json'
	headers = {}
	params = {
		'app_id': HERE_APP_ID,
		'app_code': HERE_APP_CODE,
		'prox': "%s,%s" % coords,
		'gen': 9,
		'mode': 'retrieveAddresses',
		'maxresults': 1,
	}

	response = requests.get(uri, headers=headers, params=params)
	try:
		response.raise_for_status()
		return response.json()

	except requests.exceptions.HTTPError as e:
		print(str(e))
		return {}