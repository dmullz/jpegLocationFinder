import jpeg_location

def run_tests(test_name, file):
	if test_name == "all":
		tests = ["test_gps", "test_image_no_gps", "test_png", "test_nonimage", "test_dirs", "test_gps_vs_gps_lib"]
		for test in tests:
			if file:
				globals()[test](file)
			else:
				globals()[test]()
			print(test,"passed")
		print("All tests passed.")
	else:
		if test_name in globals() and test_name != "run_tests":
			if file:
				globals()[test_name](file)
			else:
				globals()[test_name]()
			print("Test",test_name,"passed")
		else:
			print("Test with the name of",test_name,"does not exist.")
			
			
def test_gps(file="test5.jpg"):
	print("\nTesting gps extraction from file end-to-end")
	assert list(jpeg_location.image_gen(file))[0] == file, "File Generator Failed"
	geotags = jpeg_location.get_geotags_from_jpeg(file)
	assert "GPSLatitude" in geotags, "Problem parsing GPS data from EXIF"
	location = jpeg_location.get_location(geotags)
	assert location['Response']['View'][0]['Result'][0]['Location']['Address']['PostalCode'] == "08831", "Problem getting Zip Code from HERE API"
	
def test_image_no_gps(file="test4.jpg"):
	print("\nTesting an image without gps data")
	geotags = jpeg_location.get_geotags_from_jpeg(file)
	assert geotags == None, "Geotagging being returned when it does not exist"
	
def test_png(file="test3.png"):
	print("\nTesting a PNG")
	geotags = jpeg_location.get_geotags_from_jpeg(file)
	assert geotags == None, "EXIF returned for a PNG"
	
def test_nonimage(file="README.md"):
	print("\nTesting a non-image")
	geotags = jpeg_location.get_geotags_from_jpeg(file)
	assert geotags == None

def test_dirs(file="test_dir"):
	print("\nTesting the file generator")
	count_files = 0
	for file in jpeg_location.image_gen(file):
		count_files += 1
		print("file", count_files,":",file)
		assert file in ["test3.png","test4.jpg","test5.jpg"], "Problem with Image File Generator"
	assert count_files == 3 , "Problem with Image File Generator"
	
def test_gps_vs_gps_lib(file="test5.jpg"):
	print("\nTesting manual extraction of gps data vs library extraction")
	man_geotags = jpeg_location.get_geotags_from_jpeg(file)
	exif = jpeg_location.get_exif(file)
	lib_geotags = jpeg_location.get_geotagging(exif)
	for tag in man_geotags:
		print("For Tag", tag, "-> Manual:", man_geotags[tag],"Library:", lib_geotags[tag])
		assert man_geotags[tag] == lib_geotags[tag], "Difference in geotag data"