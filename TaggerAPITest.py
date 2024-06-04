import requests
import sys
import time

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " url")
    exit(0)

url = sys.argv[1]
health_url = url + "/health"
input_url = url + "/input"
status_url = url + "/status"
output_url = url + "/output"

rootpage = requests.get(url + "/")
print("Root page returns:", rootpage.text)

health = requests.get(health_url)
print("Health page returns:", health.text)

identifier = None

with open('test.txt', 'rb') as f:
  r = requests.post(input_url, files={'file': f})
  if r.status_code != 200:
      raise Exception("Failed to upload file, server response was: " + r.text)
  identifier= r.text

if identifier is None:
  raise Exception("Did not receive an identifier")

print("Got identifier: " + identifier)

file_status_url = status_url + "/" + identifier

print(file_status_url)

for i in range(0,20):
  r = requests.get(file_status_url)
  if r.status_code != 200:
    raise Exception("Failed to get status")
  # {"message": "File arrived", "pending": true, "busy": false, "error": false, "finished": false}
  status_json = r.json()
  print("Current status is: " + str(status_json))
  if status_json['finished'] or status_json['error']:
    break
  time.sleep(1)

if status_json['pending']:
  raise Exception("Processing did not start")
if status_json['busy']:
  raise Exception("Processing took too long")
if status_json['error']:
  raise Exception("An error occured during processing")
if not status_json['finished']:
  raise Exception("An invalid status had been returned")

file_output_url = output_url + "/" + identifier

r = requests.get(file_output_url)
if r.status_code != 200:
  raise Exception("Failed to download file")

print("I got the result:\n\n" + str(r.text))

r = requests.delete(file_output_url)
if r.status_code != 200:
  raise Exception("Failed to delete file")