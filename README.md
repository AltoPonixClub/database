# Key Value Store For Sensor Data from S2

**GET**
Endpoint: `/get` or `/get?key=<key>`
Returns the value associated with the key given.
If there is no key given, returns the whole json object
If the key doesn't exist, returns 404

**POST**
Endpoint: `/set/`
Use a json object with the fields that need to be updated.
ex (python):
```
url = "https://altoponix-database.herokuapp.com/set"
data = {"key":"672ef79b4d0a4805bc529d1ae44bc26b","atmospheric_temp":8}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
import json, requests
r = requests.post(url, data=json.dumps(data), headers=headers)
```
ex (javascript):
```
let json = {"key":672ef79b4d0a4805bc529d1ae44bc26b,"atmospheric_temp":8};
let xhr = new XMLHttpRequest();
xhr.onload = function(e) {
	console.log(xhr.responseText)
	...
}
r.open("POST", url);
r.setRequestHeader('Content-Type', 'application/json');
r.send(JSON.stringify(json));

Must require a key. Any fields that aren't specified are not updated
Returns 400 if the data is invalid
See requests.html
```
