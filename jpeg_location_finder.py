import argparse
import image_tests
import jpeg_location
import os

# @DEV - Function to parse input arguments
# @RET (tuple) - Returns the file or directory to check for image data, and optionally the excel file output
def read_inputs():
	parser = argparse.ArgumentParser(description="This program extracts zip codes from JPEG image files.")
	parser.add_argument("-f", "--file", help="image file or directory")
	parser.add_argument("-x", "--excel", help="output results in an excel file with the given filename")
	parser.add_argument("-t", "--test", help="provide the name of the test or 'all' to run all tests")
	args = parser.parse_args()
	
	if args.test:
		image_tests.run_tests(args.test)
		return None
	
	if not args.file:
		raise ValueError("No image file or directory specified")
	
	if args.excel:
		return (args.file, args.excel)
	return (args.file,"")
	
	
########################################################################################################
# Get input arguments
args = read_inputs()

if args:
	# Generate files and check them until there are none left
	for file in jpeg_location.image_gen(args[0]):
		# Check for exif data in file
		exif = jpeg_location.get_exif(file)
		if exif != None:
			# Get geotagging data from EXIF
			geotags = jpeg_location.get_geotagging(exif)
			if geotags == None:
				print("No geotagging EXIF data in image",file)
			else:
				# Use API to get location data
				location = jpeg_location.get_location(geotags)
				try:
					# Get zip code from location data
					postal_code = location['Response']['View'][0]['Result'][0]['Location']['Address']['PostalCode']
					# Output results
					if args[1] != "":
						jpeg_location.add_to_excel(args[1],file,postal_code)
					else:
						print(file,postal_code)
				except:
					print("Postal Code could not be found for file:", file)