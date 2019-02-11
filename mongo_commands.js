use ab2019;


# add a new record
db.users.insert({
	"email": "selam@selam.com",
	"is_admin": true,
	"password": "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"
});


# finding a record
db.users.find_one({
	"is_admin": True,
	"password": "password": "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"
});
