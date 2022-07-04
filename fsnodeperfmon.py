#apt install python3-pip -y
#pip3 install azure.storage.blob
#https://docs.microsoft.com/en-us/python/api/overview/azure/storage-file-share-readme?view=azure-python#uploading-a-file
#from xml.etree.ElementTree import TreeBuilder
#from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from azure.storage.fileshare import ShareServiceClient
from azure.storage.fileshare import ShareFileClient
from os.path import exists
from datetime import datetime
import requests
import os
import subprocess as sp
import socket
import time
 
storage_accout = "https://ovidiuborlean.file.core.windows.net/"
account_key = "geS8Pi70WAY9BIiX/ii4ubZxh7YPw3JIslvWT7TtIuWy7I9dAeqOhCLRhy0SBmzbfbhMLnDY3xIV+ASttmtYCA=="
conn_str = "DefaultEndpointsProtocol=https;AccountName=ovidiuborlean;AccountKey=geS8Pi70WAY9BIiX/ii4ubZxh7YPw3JIslvWT7TtIuWy7I9dAeqOhCLRhy0SBmzbfbhMLnDY3xIV+ASttmtYCA==;EndpointSuffix=core.windows.net"


def upload(fileName):
  now = datetime.now()
  # Getting current date/time from environment
  dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
  # Getting hostname of Node
  hostName = sp.getoutput("hostname")
  # Generate the FileShare name by merging hostname and date/time
  shareName = hostName + "_" + dt_string
  service = ShareServiceClient(account_url=storage_accout, credential=account_key)
  file_client = ShareFileClient.from_connection_string(conn_str=conn_str, share_name=shareName, file_path=fileName)
  
  with open(fileName, "rb") as source_file:
    file_client.upload_file(source_file)
    time.sleep(1)
    #file_client



def node_backup():
  file_exists = exists("./backup.sh")
  if not file_exists:
    print("Backup script does not exist: ")
  else:
    os.system("./backup.sh")
    upload("/tmp/akslogs.tgz")


def perfmon():
   CPU_check = float(sp.getoutput("./cpucheck.sh"))
   print("CPU Load: ", CPU_check)
   mem_check =  float(sp.getoutput("./memcheck.sh"))
   print("Memory Load: ", mem_check)
   if CPU_check > float(CPU_MAX) or mem_check > float(MEM_MAX):
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
    node_backup()

if __name__ == '__main__':
  #init_report()
  #print(os.environ)
  if 'CONN_STR' in os.environ:
    CONN_STR = os.environ.get('CONN_STR')
  else:
    print ("Azure Storage - Connection String Not found in Environment. Please add to upload report")
  if 'GLOBAL_DELAY' in os.environ:
    GLOBAL_DELAY = os.environ.get('GLOBAL_DELAY')
    print(GLOBAL_DELAY)
  if 'CPU_MAX' in os.environ:
    CPU_MAX = os.environ.get('CPU_MAX')
  else:
    CPU_MAX = float(95)
  if 'MEM_MAX' in os.environ:
    MEM_MAX = os.environ.get('MEM_MAX')
  else:
    MEM_MAX = float(3)
  print ("Starting Monitor")
  if 'RUN_FOR' in os.environ:
    RUN_FOR = os.environ.get('RUN_FOR')
  else:
    RUN_FOR = float(5)
  
  #while (True):
  t_end = time.time() + 60 * RUN_FOR
  while time.time() < t_end:
    network_check("127.0.0.1", 10250)
    perfmon()
    time.sleep(GLOBAL_DELAY)


