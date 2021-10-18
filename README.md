# Key Value Store For Sensor Data from S2

**GET**
Endpoint: `/get/<key>`
Returns the value associated with the key given.
If there is no key given, returns the whole json object
If the key doesn't exist, returns 404

**POST**
Endpoint: `/set/`
Use a json object with the fields that need to be updated.
ex (javascript):
```
let json = {"atmospheric_temp":8};
let xhr = new XMLHttpRequest();
xhr.onload = function(e) {
	console.log(xhr.responseText)
	...
}
r.open("POST", url);
r.setRequestHeader('Content-Type', 'application/json');
r.send(JSON.stringify(json));
```
# Deployment
``git push heroku main``