import jpeg_location

def run_tests(test_name):
	if test_name == "all":
		tests = ["test_gps", "test_image_no_gps", "test_png", "test_nonimage", "test_dirs"]
		for test in tests:
			globals()[test]()
			print(test,"passed")
		print("All tests passed.")
	else:
		if test_name in globals() and test_name != "run_tests":
			globals()[test_name]()
			print("Test",test_name,"passed")
		else:
			print("Test with the name of",test_name,"does not exist.")
			
			
def test_gps():
	assert list(jpeg_location.image_gen("test5.jpg"))[0] == "test5.jpg", "File Generator Failed"
	exif = jpeg_location.get_exif("test5.jpg")
	assert 34853 in exif, "Cannot extract EXIF data"
	geotags = jpeg_location.get_geotagging(exif)
	assert "GPSLatitude" in geotags, "Problem parsing GPS data from EXIF"
	location = jpeg_location.get_location(geotags)
	assert location['Response']['View'][0]['Result'][0]['Location']['Address']['PostalCode'] == "08831", "Problem getting Zip Code from HERE API"
	
def test_image_no_gps():
	exif = jpeg_location.get_exif("test4.jpg")
	assert exif != None, "Cannot extract EXIF data"
	geotags = jpeg_location.get_geotagging(exif)
	assert geotags == None, "Geotagging being returned when it does not exist"
	
def test_png():
	exif = jpeg_location.get_exif("test3.png")
	assert exif == None, "EXIF returned for a PNG"
	
def test_nonimage():
	exif = jpeg_location.get_exif("README.md")
	assert exif == None

def test_dirs():
	count_files = 0
	for file in jpeg_location.image_gen("test_dir"):
		count_files += 1
		print("file", count_files,":",file)
		assert file in ["test3.png","test4.jpg","test5.jpg"], "Problem with Image File Generator"
	assert count_files == 3 , "Problem with Image File Generator"