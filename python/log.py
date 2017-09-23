from pymongo import MongoClient
import RPi.GPIO as GPIO
from bson.objectid import ObjectId
import time
import save
import send_email
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)

mongo_db = MongoClient('localhost',27017)
db_log = mongo_db.smartbell.logs

def led():
	'''
	This function is to blink led when checking a permission to access
	'''
	GPIO.output(27,True)
	time.sleep(1)
	GPIO.output(27,False)
	time.sleep(1)


def save_log(firstname, lastname, frame, __id, log_time, access):
	'''
	This function is to check permission of the visitor and save entrance log, if he or she has permission to access.
	First, we check access permission using visitor's id. (access value is 'true' or 'false')
	If the visitor doesn't have permission to access, we would close the door and led blinks 5 times.
	If the visitor has the permission, we would open the door and save the log which is about firstname, lastname and time, and led blinks once.
	'''
	if __id == 0:
		path = 'log'
		save.make_directory(path)
		photo_path = save.save_photo(path, '/'+str(log_time)+'.jpg', frame)
		
	else:
		photo_path = 'pics/' + str(__id) + '/img0.jpg'
	if access == True:
		access_log = "allowed"
	else:
		access_log = "denied"
	# Save the log
	db_log.insert_one({"firstname":firstname, "lastname":lastname, "time":log_time, "photopath": photo_path, "access":access_log})
	return log_time

def permission_check(__id, frame,log_time):
	# Check permission to access 
	db_visitors = mongo_db.smartbell.visitors
	try:
		valid = db_visitors.find_one({"_id": ObjectId(__id[0])})
	except EOFError:
		return 0
	
	save_log(valid['firstname'], valid['lastname'], frame, valid['_id'], log_time, valid['access'])
	
	# If permission to access is true,
	if valid['access']:
		print("Available face")
		send_email.email(valid['email'],valid['firstname'],valid['lastname'],log_time)
		led()
		
	else:
		print("No permission, closed")
		for n in range(5):
			led()
