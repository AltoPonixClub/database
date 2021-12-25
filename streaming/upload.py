import boto3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import sys
import time

streaming_id = '672ef79b4d0a4805bc529d1ae44bc26b'

# Deletes everything in the cdn's path
def clearPath(client, path):
  response = client.list_objects_v2(Bucket='altoponix-cdn', Prefix=path)
  if 'Contents' in response:
    objs = []
    for obj in response['Contents']:
      print("Removing: " + obj['Key'])
      objs.append({"Key": obj['Key']})
    client.delete_objects(Bucket='altoponix-cdn', Delete={'Objects': objs})

# Uploads the file to the cdn
def uploadfile(client, path, file, streaming_id):
  try:
    if file.endswith(".ts"):
      with open(path + "/" + file, "rb") as f:
        client.upload_fileobj(f, "altoponix-cdn", "streaming/" + streaming_id + "/" + file, 
        ExtraArgs={
          'ACL': 'public-read',
          'ContentType': 'video/mp2t',
          'ContentDisposition': 'attachment'
        })
    elif file.endswith(".m3u8"):
      with open(path + "/" + file, "rb") as f:
        client.upload_fileobj(f, "altoponix-cdn", "streaming/" + streaming_id + "/master.m3u8", 
        ExtraArgs={
          'ACL': 'public-read',
          'ContentType': 'application/x-mpegURL',
          'ContentDisposition': 'inline',
          'CacheControl': 'max-age=0'
        })
    else:
      print("Couldn't recognize file type of '" + file + "'")
  except Exception as e:
    print(e)

# Initalize the connection
session = boto3.session.Session()
client = session.client('s3',
                        region_name='sfo3',
                        endpoint_url='https://sfo3.digitaloceanspaces.com',
                        aws_access_key_id=os.getenv('SPACES_KEY'),
                        aws_secret_access_key=os.getenv('SPACES_SECRET'))

# Remove anything already present in the streaming folder
clearPath(client,'streaming/' + streaming_id + "/")

# Check for path argument
path = ""
if len(sys.argv) == 1:
  path = (".")
else:
  path = (sys.argv[1])

print("Selected path: '" + path + "'")
if not os.path.isdir(path):
  print("Given path is not a valid directory!")
  exit()

class FileHandler(FileSystemEventHandler):
  def on_modified(self, event):
    if event.is_directory:
      return None
    if event.event_type == 'modified':
      m3u8 = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and (f.endswith('.m3u8'))]
      match = [f for f in m3u8 if event.src_path[(len(path)+1):].startswith(f)]
      if event.src_path.endswith(".ts"):
        print("Uploading ts: " + event.src_path[(len(path)+1):])
        uploadfile(client, path, event.src_path[(len(path)+1):], streaming_id)
        print("Uploaded ts: " + event.src_path[(len(path)+1):])
      elif len(match) > 0:
        print("Uploading m3u8: " + match[0])
        if len(match) > 1:
          print("Warning: Found more than one similarily named m3u8 files.")
        uploadfile(client, path, match[0], streaming_id)
        print("Uploaded m3u8: " + match[0])

# Cache
oldfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and (f.endswith('.ts'))]
m3u8 = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and (f.endswith('.m3u8'))]
if len(m3u8) > 1:
  print("Found more than one m3u8 file. Aborting.")
  exit()

if __name__ == "__main__":
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()
    try:
      while True:
        # Remove old files
        ts = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and (f.endswith('.ts'))]
        removals = list(set(oldfiles) - set(ts))
        if len(removals) > 0:
          for file in removals:
            print("Removing: " + file)
            client.delete_object(Bucket='altoponix-cdn', Key='streaming/' + streaming_id + '/' + file)
            print("Removed: " + file)
        oldfiles = ts
        time.sleep(1)
    except KeyboardInterrupt:
      observer.stop()
    observer.join()