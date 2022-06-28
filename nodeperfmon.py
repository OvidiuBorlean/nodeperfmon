#apt install python3-pip -y
#pip3 install azure.storage.blob

from xml.etree.ElementTree import TreeBuilder
import requests
import os
import subprocess as sp
import socket
import time

from datetime import datetime
#now = datetime.now()
 
GLOBAL_DELAY = 10
CPU_MAX = 0.1
MEM_MAX = 0.1

#dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
#print(type(dt_string))	

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

def upload():
  now = datetime.now()
  dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
  connect_str = "DefaultEndpointsProtocol=https;AccountName=ovidiuborlean;AccountKey=AC1I4s5AIZ5yazBxMblFOr0nFapLRgBjKcoSjXzvvTcvnxIXBNpFOti1DWZ/aXDAIDEAej563AMC+AStbfEIpw==;EndpointSuffix=core.windows.net"
  blob_service_client = BlobServiceClient.from_connection_string(connect_str)
  blob_client = blob_service_client.get_blob_client(container="logs", blob=dt_string)
  with open("/tmp/aksreport", "rb") as data:
    blob_client.upload_blob(data)


#print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

def cpu_check():
   CPU_check = float(sp.getoutput("./cpucheck.sh"))
   print(CPU_check)
   if CPU_check > CPU_MAX:
     cpu_report = sp.getoutput("top -b -n 1")
     hostname = sp.getoutput("hostname")
     with open("/tmp/aksreport", "a") as f:
       f.write(hostname)
       f.write(cpu_report)
       f.write("------------------------------------------")
       f.close()
     time.sleep(5)
     upload()

def mem_check():
  mem_check =  float(sp.getoutput("./memcheck.sh"))
  print(mem_check)
  if mem_check > MEM_MAX:
    mem_report = sp.getoutput("free -h")
    hostname = sp.getoutput("hostname")
    with open("/tmp/aksreport", "a") as f:
      f.write(hostname)
      f.write(mem_report)
      f.write("---------------------------------------")
      f.close()
    time.sleep(5)
    upload()

#def kubelet_check():
#  kubelet_check = sp.getoutput("service kubelet status | grep running")
#  if "running" in kubelet_check:
#    print ("Kubelet is running")
#  else:
#    print ("Kublet Failure")

def network_check(host, port):
  settings = {}
  ports = [port]
  settings["timeout"] = 5
  #settings["port"] = 1192
  connected = False
  for n in ports:
     try:
       tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       tsock.settimeout(settings['timeout'])
       print("Checking connectivity to: ", n)
       tsock.connect((host, n))
       connected = True
       print("Success")
       tsock.shutdown(socket.SHUT_RDWR)
       tsock.close()
       time.sleep(1)
     except ConnectionRefusedError:
       print('Error Refused')
       time.sleep(1)
     except:
       print("Network Failure")
  if not connected:
    print("Generate Report")
    journal = sp.getoutput('journalctl --since "15 min ago"')
    hostname = sp.getoutput("hostname")
    with open("/tmp/aksreport", "a") as f:
      f.write(hostname)
      f.write(journal)
      f.write("---------------------------")
      f.close()
    time.sleep(5)
    upload()

if __name__ == '__main__':
  while (True):
    network_check("127.0.0.1", 10250)
    cpu_check()
    mem_check()
    time.sleep(GLOBAL_DELAY)