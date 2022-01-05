# Websocket Documentation

The backend server uses [Socket-IO](https://python-socketio.readthedocs.io/en/latest/). Use socket-io on your client. (javascript uses https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js)

The endpoint for web socket connections is ``https://altoponix-database.herokuapp.com``. For local testing, ``http://127.0.0.1:5000`` is used.

## Outline
There are two types of clients: the user and the monitor. Only the user is able to send commands to the monitor. Both connect to the backend server to send/receive commands.

## Basics
Each event has a keyword attached to it. A sender can send a keyword along with some data, and a receiver may wait for that keyword and receive that data.

Example (javascript):
```
// Connect to the server
socket = io.connect(url);
socket.on('connect', function() {
	console.log("hello world!")
});

// Send a message to the server
socket.emit('send', { message: "hello server!"});
```
This program waits for the keyword "connect" and sends the keyword "send".

## Program Flow

### User Side:
The user should emit ``query`` when it connects to the server. After receiving ``query ok``, the user is now ready to send commands. If the user receives ``query failed``, the connection closes.

When sending a command using ``command send``, the user should get the ``command ok`` keyword as a confirmation that the command reached the server (but not necessarily the monitor). When the user receives ``command finish``, the command has been received by the monitor, and the task is complete. If ``command failed`` is received, the monitor didn't accept the command, and a reason is given.

### Monitor Side:
The monitor should emit ``con`` when it connects to the server. After receiving ``con ok``, the monitor is now ready to receive commands. If the monitor receives ``con failed``, the connection closes.

The monitor should wait for the ``command do`` keyword, which includes a string on which command to execute. The monitor can decide to emit ``command done`` or ``command error`` to report back to the user.

## User Keywords
### ``query:`` event sent by user to start sending commands.
**JSON data:**
```
{
	"monitor_id": string, the monitor_id to start sending commands to (REQUIRED)
}
```
Server emits ``query ok`` if connection succeeded, ``query failed`` if connection didn't (and closes the connection)

### ``command send``: event sent by user to send a command to the monitor.
**JSON data:**
```
{
	"command": string, the command to send (REQUIRED)
}
```
Server emits ``command failed`` to the user if the command was invalid.
Server emits ``command ok`` to the user as a response and emits ``command do`` to the monitor with the same command given.

## Monitor Keywords

### ``con``: event sent by monitor to start listening commands
**JSON data:**
```
{
	"monitor_id": string, the monitor_id of the device (REQUIRED)
}
```
The monitor_id given must be a unique one that is currently not connected to a websocket.
Server emits ``con ok`` if connection succeeded, ``con failed`` if connection didn't (and closes the connection)

### ``command done``: event sent by device to signal when a command finishes
**JSON data:** None
Server emits ``command finish`` to the client

### ``command error``: event sent by device to signal when a command finishes
**JSON data:**
```
{
	"reason": string, the reason of failure (REQUIRED)
}
```
Server emits ``command failed`` to the client with the reason given.


