# Altoponix API with SQLite3 Database

**GET Requests**
Endpoint: `/get` or `/get?key=<key>`
Returns the value associated with the key given.
If there is no key given, returns the whole json object
If the key doesn't exist, returns 404
ex (python):
```
data = requests.get('https://altoponix-database.herokuapp.com/api/v1/monitors/get?monitor_id=<monitor_id>')
```

**POST Requests**
Any other endpoint is a post request, including "/delete"
Use a json object with the fields that need to be updated.
ex (python):
```
url = "https://altoponix-database.herokuapp.com/api/v1/monitors/update"
data = {"id":<monitor_id>,"atmospheric_temp":<insert>}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
import json, requests
r = requests.post(url, data=json.dumps(data), headers=headers)
```
ex (javascript):
```
let json = {"id":<monitor_id>,"atmospheric_temp":<insert>};
let xhr = new XMLHttpRequest();
xhr.onload = function(e) {
	console.log(xhr.responseText)
	...
}
r.open("POST", url);
r.setRequestHeader('Content-Type', 'application/json');
r.send(JSON.stringify(json));
```

Must require a key. Any fields that aren't specified are not updated
Returns 400 if the data is invalid
See app/modules/database.py for documentation

**Websocket Command Sending**
Documentation for this is in the file app/modules/websocket.py

**Adding more modules**
Simply create another module in the app/modules folder, and import it in app/modules/\_\_init__.py.
