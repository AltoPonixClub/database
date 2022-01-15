
# Database API Documentation
This document outlines the various endpoints and workings of the database API.

For testing this API, use the HTML page testing/requests.html. Select the request URL and fill in the fields. 

## Endpoints
This database service is currently being hosted at ``https://altoponix-database.herokuapp.com``. Any API requests should be sent to this URL. For testing purposes, you can run ``main.py`` locally and change this endpoint to ``http://127.0.0.1:5000``.

## Permissions
There are two ways to obtain log in: logging in as a user (from the website), or logging in as a monitor. A user will be able to access their monitors, while a monitor can only add new measurements to stored dataa.
A table of permissions is shown below.
|                             | Admin | User | Monitor |
|-----------------------------|-------|------|---------|
| Read Monitor/User Data      | x     | x    |         |
| Update Monitor Data         | x     |      | x       |
| Reset/Delete Monitors/Users | x     |      |         |
| Get All Monitor Data/Users  | x     |      |         |

Trying to call a method without the proper access will result in a ``403 Forbidden`` error.

## API Basics

API responses are in the format:
```
{
	success: True,
	data: object (the data)
}
```
or
```
{
	success: False,
	cause: string (more details on why the request failed)
}
```
Be sure to check whether a API request was successful with the success variable or the error code before accessing data.

**HTTP Codes**
HTTP codes and what they mean are documented in this document. The 500 Internal Server Error, which isn't listed, occurs when an error has occurred in the server.

**GET Requests**
Get requests are done by adding arguments in NVP format (ex. ``?value1=cat&value2=dog``)
Example (python):
```
data = requests.get('https://altoponix-database.herokuapp.com/api/v1/monitors/get?monitor_id=<monitor_id>')
```
**POST Requests**
Post requests are done by sending a JSON object to the endpoint. A string representation of the JSON object is acceptable.
**The HTTP Request must have the Content-Type header set to application/json**.
Example (python):
```
url = "https://altoponix-database.herokuapp.com/api/v1/monitors/update"
data = {"id":<monitor_id>,"atmospheric_temp":<insert>}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
import json, requests
r = requests.post(url, data=json.dumps(data), headers=headers)
```
Example (javascript):

```
let url = "https://altoponix-database.herokuapp.com/api/v1/monitors/update"
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

## Getting started

### Logging in as a user
**Endpoint:** /api/v1/login/user
**Allowed Methods:** POST
**JSON Input:**
```
{
	"username": string,
	"password": string,
	"persist": bool
}
```
**JSON Output:**
```
{
	"token": string,
	"username": string,
	"user_id": string
}
```
**Extra Notes:**
``persist``: If this is true, the authentication token will not expire and can only be expired when that user logs out or if the password is reset.
``token``: This is the authentication token used for future API requests. You may store this token in the browser's local storage if you want the user to stay logged in. Authentication tokens will expire after 4 hours, after which the user must log in again. Authentication tokens are hexadecimal strings of length 32.
``username``: The username associated with the account
``user_id``: The user_id associated with the account

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                        |
|-----------------------------|--------------------------------------------------------------------|
| 200 OK                      | The login was successful.                                           |
| 400 Bad Request             | At least one of the username or password arguments are missing.    |
| 401 Unauthorized            | Invalid credentials were provided, and the login was unsuccessful. |

### Logging in as a monitor
**Endpoint:** /api/v1/login/monitor
**Allowed Methods:** POST
**JSON Input:**
```
{
	"monitor_id": string,
	"password": string,
	"persist": bool
}
```
**JSON Output:**
```
{
	"token": string
}
```
**Extra Notes:**
``persist``: If this is true, the authentication token will not expire and can only be expired when that user logs out or if the password is reset.
``token``: This is the authentication token used for future API requests. You may store this token in the browser's local storage if you want the user to stay logged in. Authentication tokens will expire after 4 hours, after which the user must log in again. Authentication tokens are hexadecimal strings of length 32.
**Possible HTTP Codes:**
| HTTP Code                   | Description                                                        |
|-----------------------------|--------------------------------------------------------------------|
| 200 OK                      | The login was successful.                                           |
| 400 Bad Request             | At least one of the monitor_id or password arguments are missing.    |
| 401 Unauthorized            | Invalid credentials were provided, and the login was unsuccessful. |

### Logging out as a user
**Endpoint:** /api/v1/logout/user
**Allowed Methods:** POST
**JSON Input:**
```
{
	"user_id": string (required),
	"token": string (required),
}
```
**JSON Output:** None
**Extra Notes:**
This method will remove the current token from the active tokens list.

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                        |
|-----------------------------|--------------------------------------------------------------------|
| 200 OK                      | The logout was successful.                                           |
| 400 Bad Request             | At least one of the user_id or token arguments are missing.    |
| 401 Unauthorized            | Invalid credentials were provided, and the logout was unsuccessful. |


### Logging out as a monitor
**Endpoint:** /api/v1/logout/monitor
**Allowed Methods:** POST
**JSON Input:**
```
{
	"monitor_id": string (required),
	"token": string (required)
}
```
**JSON Output:** None
**Extra Notes:**
This method will remove the current token from the active tokens list.

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                        |
|-----------------------------|--------------------------------------------------------------------|
| 200 OK                      | The logout was successful.                                           |
| 400 Bad Request             | At least one of the monitor_id or token arguments are missing.    |
| 401 Unauthorized            | Invalid credentials were provided, and the logout was unsuccessful. |

# All Methods

Authentication tokens are obtained by logging in (see above methods).

### Verifying a user token
**Endpoint:** /api/v1/login/user/verify
**Allowed Methods:** POST
**JSON Input:**
```
{
	"user_id": string (required),
	"token": string (required)
}
```
**Output:** ``true`` if the token is valid, ``false`` if it isn't
**Extra Notes:**
Use this method to check if a stored token is invalid before doing any other methods.

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                        |
|-----------------------------|--------------------------------------------------------------------|
| 200 OK                      | The request was successful.                                           |
| 400 Bad Request             | At least one of the user_id or token arguments are missing.    |

### Verifying a monitor token
**Endpoint:** /api/v1/login/monitor/verify
**Allowed Methods:** POST
**JSON Input:**
```
{
	"monitor_id": string (required),
	"token": string (required)
}
```
**Output:** ``true`` if the token is valid, ``false`` if it isn't
**Extra Notes:**
Use this method to check if a stored token is invalid before doing any other methods.

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                        |
|-----------------------------|--------------------------------------------------------------------|
| 200 OK                      | The request was successful.                                           |
| 400 Bad Request             | At least one of the monitor_id or token arguments are missing.    |


### Get a monitor's data
**Endpoint:** /api/v1/monitors/get
**Allowed Methods:** GET
**Arguments:**
```
"token": string, (required)
"monitor_id": string,
"startTime": int,
"endTime": int
```
**JSON Output:**
```
{
	"atmospheric_temp": {
      "value": 1,
      "history": {
	      "1641347967585": 1
      }
    },
    "reservoir_temp": {...},
    "light_intensity": {...},
    "soil_moisture": {...},
    "electrical_conductivity": {...},
    "ph": {...},
    "dissolved_oxygen": {...},
    "air_flow": {...},
    "foliage_feed": string,
    "root_stream": string
}
```
**Extra Notes:**
Only users and admins can use this method, and accessing another account's monitors as a user is forbidden.

``monitor_id`` If this argument isn't given, this method returns all the monitors in the entire system. **This only works if the user accessing this method is an admin.**
The data returned is then in this structure: 
```
{
	monitor_id1: {
		"atmospheric_temp": {...},
		⋮
	    "root_stream": string,
	    "owner": string,
	},
	monitor_id2: {
		"atmospheric_temp": {...},
		⋮
	    "root_stream": string,
	    "owner": string,
	},
	⋮
}
```
where the ``owner`` is the ``owner_id`` of the monitor.

``startTime``: Filter all data points after this unix timestamp
``endTime``: Filter all data points before this unix timestamp
Each measurement (atmospheric_temp, reservoir_temp, etc..) has this data structure:
```
{
	"value": null / float,
	"history": {string: float}
}
```
``value`` is the current value of the measurement. If it is null, there is no data stored.
``history`` is an object containing time-value pairs. Keys of the history object are the unix timestamp and the value of the measurement at that time. (example ``"1641347967585": 1``) 

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                                                                   |
|-----------------------------|---------------------------------------------------------------------------------------------------------------|
| 200 OK                      | The request was successful.                                                                                   |
| 400 Bad Request             | The monitor_id or token given was invalid.                                                                  |
| 401 Unauthorized            | The provided token was invalid.                                                                               |
| 403 Forbidden               | Listing all monitors without an admin token was attempted, or accessing another user's monitor was attempted. |

### Update a monitor's data with a new data point
**Endpoint:** /api/v1/monitors/update
**Allowed Methods:** POST
**JSON Input:**
```
{
	"token": string, (required)
	"monitor_id": string, (required)
	"atmospheric_temp": float,
	"reservoir_temp": float,
	⋮
	"foliage_feed": string,
	"root_stream": string
}
```
**JSON Output:** None

**Extra Notes:**
Only monitors and admins can use this method, and updating another monitor as a monitor is not allowed.

Data measurements like ``atmospheric_temp`` and ``reservoir_temp`` will automatically update the ``value`` and ``history`` of that measurements. Only arguments that have been passed will be updated.


**Possible HTTP Codes:**

| HTTP Code                   | Description                                                                     |
|-----------------------------|---------------------------------------------------------------------------------|
| 200 OK                      | The request was successful.                                                     |
| 400 Bad Request             | The monitor_id or token given was invalid, or no measurements could be updated. |
| 401 Unauthorized            | The provided token was invalid.                                                 |
| 403 Forbidden               | The token doesn't match the provided monitor_id.                                |

### Add a new monitor to a given user
**Endpoint:** /api/v1/monitors/add
**Allowed Methods:** POST
**JSON Input:**
```
{
	"token": string, (required)
	"user_id": string, (required)
	"monitor_id": string (required)
	"password": string (required)
}
```
**JSON Output:** None

**Extra Notes:**
Only admins can use this method.

``user_id``: The owner_id of the new monitor
``monitor_id``: The monitor_id of the new monitor
``password``: The password that the new monitor will use to log in.

This will fail if there is already a monitor with the same monitor_id.


**Possible HTTP Codes:**
| HTTP Code                   | Description                                                                                                               |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------|
| 200 OK                      | The request was successful and the monitor was created.                                                                   |
| 400 Bad Request             | Some arguments weren't provided, the monitor_id already exists or is invalid, or the user_id doesn't exist or is invalid. |
| 401 Unauthorized            | The provided token was invalid.                                                                                           |
| 403 Forbidden               | A non-admin tried to access this method.                                                                                  |

### Reset a monitor's data points
**Endpoint:** /api/v1/monitors/reset
**Allowed Methods:** POST
**JSON Input:**
```
{
	"token": string, (required)
	"monitor_id": string (required)
}
```
**JSON Output:** None

**Extra Notes:**
Only admins can use this method.

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                    |
|-----------------------------|----------------------------------------------------------------|
| 200 OK                      | The request was successful.                                    |
| 400 Bad Request             | Some arguments weren't provided, or the monitor_id is invalid. |
| 401 Unauthorized            | The provided token was invalid.                                |
| 403 Forbidden               | A non-admin tried to access this method.                       |

### Delete a monitor
**Endpoint:** /api/v1/monitors/delete
**Allowed Methods:** POST
**JSON Input:**
```
{
	"token": string, (required)
	"monitor_id": string (required)
}
```
**JSON Output:** None

**Extra Notes:**
Only admins can use this method.

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                    |
|-----------------------------|----------------------------------------------------------------|
| 200 OK                      | The request was successful.                                    |
| 400 Bad Request             | Some arguments weren't provided, or the monitor_id is invalid. |
| 401 Unauthorized            | The provided token was invalid.                                |
| 403 Forbidden               | A non-admin tried to access this method.                       |

### Get a info about a user
**Endpoint:** /api/v1/owners/get
**Allowed Methods:** GET
**Arguments:**
```
"token": string, (required)
"user_id": string
```
**JSON Output:** 
```
{
	"monitor_ids": [string],
    "username": string,
    "type": string
}
```

**Extra Notes:**
Only users and admins can use this method, and accessing another account's monitors as a user is forbidden.

``user_id`` If this argument isn't given, this method returns all the users in the entire system. **This only works if the user accessing this method is an admin.**
The data returned is then in this structure: 
```
{
	user_id1: {
		"monitor_ids": [string],
		"username": string,
		"type": string
	},
	user_id2: {
		"monitor_ids": [string],
		"username": string,
		"type": string
	},
}
⋮
```

``monitor_ids``: a list of the monitor_ids that this user owns.
``username``: the username associated with this account.
``type``: the type of account. This may be "user" or "admin".

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                                                                   |
|-----------------------------|---------------------------------------------------------------------------------------------------------------|
| 200 OK                      | The request was successful.                                                                                   |
| 400 Bad Request             | The user_id or token given was invalid.                                                                  |
| 401 Unauthorized            | The provided token was invalid.                                                                               |
| 403 Forbidden               | Listing all users without an admin token was attempted, or accessing another user's data was attempted. |

### Reset a user's password
**Endpoint:** /api/v1/owners/resetpassword
**Allowed Methods:** POST
**JSON Input:**
```
{
	"token": string, (required)
	"user_id": string, (required)
	"old_password": string,
	"new_password": string (required)
}

```
**JSON Output:** None

**Extra Notes:**
Only users and admins can use this method, and trying to reset another account's password as a user is forbidden.

  
``old_password`` The old password. This is not required if the user is an admin
``new_password`` The new password.

After using this method, every session with this user_id will by logged out, and the user must sign in again.

**Possible HTTP Codes:**
| HTTP Code                   | Description                                                    |
|-----------------------------|----------------------------------------------------------------|
| 200 OK                      | The request was successful.                                    |
| 400 Bad Request             | Some arguments weren't provided or are invalid.                |
| 401 Unauthorized            | The provided token was invalid.                                |
| 403 Forbidden               | The user doesn't have access to reset this account's password. |