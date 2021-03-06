#apt install python3-pip -y
#pip3 install azure.storage.blob

#from xml.etree.ElementTree import TreeBuilder
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from datetime import datetime
import requests
import os
import subprocess as sp
import socket
import time
 
def init_report():
  if 'CONN_STR' in os.environ:
    CONN_STR = os.environ.get('CONN_STR')
  else:
    CONN_STR = "Customer Connextion String"
    print ("Azure Storage - Connection String Not found in Environment. Please add to upload report")
  now = datetime.now()
  # Getting current date/time from environment
  dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
  # Getting hostname of Node
  hostName = sp.getoutput("hostname")
  # Generate the Blob name by merging hostname and date/time
  blobName = hostName + "_" + dt_string
  # Executing top command on Linux host for the most active processes
  cpu_report = sp.getoutput("top -b -n 1")
  time.sleep(1)
  # Getting the free memory from Linux host
  mem_report = sp.getoutput("free -h")
  time.sleep(1)
  # Getting last 10 min logs from Journal
  journal = sp.getoutput('journalctl --since "10 min ago"')
  # Creating report file and adding the previous commands output
  with open("/tmp/aksreport", "a") as f:
    f.write(cpu_report)
    f.write("\n")
    f.write("------------------------------------------")
    f.write("\n")
    f.write(mem_report)
    f.write("------------------------------------------")
    f.write("\n")
    f.write(journal)
    f.close()
    time.sleep(2)
  try:
    print ("Initialize connection to Azure Storage Account...")
    connect_str = CONN_STR
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container="logs", blob=blobName)
    print ("Connection initalized, uploading file: ")
    with open("/tmp/aksreport", "rb") as data:
      blob_client.upload_blob(data)
    print ("Done")
  
  except:
    print ("An error occured, please check connection string or connectivity")
    
def perfmon():
   CPU_check = float(sp.getoutput("./cpucheck.sh"))
   print("CPU Load: ", CPU_check)
   mem_check =  float(sp.getoutput("./memcheck.sh"))
   print("Memory Load: ", mem_check)
   if CPU_check > float(CPU_MAX):
      init_report()
   if mem_check > float(MEM_MAX):
      init_report()  

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
    init_report()

if __name__ == '__main__':

  with open("/tmp/aksreport.logs", "w") as logs:
    logs.write("Starting Up \n")

  if 'GLOBAL_DELAY' in os.environ:
    GLOBAL_DELAY = os.environ.get('GLOBAL_DELAY')
    logs.write(GLOBAL_DELAY)
  else:
    GLOBAL_DELAY = 10

  if 'CPU_MAX' in os.environ:
    CPU_MAX = os.environ.get('CPU_MAX')
    logs.write(CPU_MAX)
  else:
    CPU_MAX = float(90)

  if 'MEM_MAX' in os.environ:
    MEM_MAX = os.environ.get('MEM_MAX')
    logs.write(MEM_MAX)
  else:
    MEM_MAX = float(3)
  print ("Starting Monitor")
  logs.write("Main Function")
  while (True):
    network_check("127.0.0.1", 10250)
    perfmon()
    time.sleep(GLOBAL_DELAY)