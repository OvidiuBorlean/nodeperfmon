#!/bin/bash

CPU_VAL=16
MEM_VAL=12
DISK_VAL=4
FILE="aksreport"
TIME_VAL=5

printf "Memory|Disk|CPU\n"

end=$((SECONDS+$TIME_VAL))
while [ $SECONDS -lt $end ]; do
  MEMORY=$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }')
  DISK=$(df -h | awk '$NF=="/"{printf "%f", $5}' | sed 's/.$//' )
  CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%\n", $(NF-2)}' | sed 's/.$//')
  #echo "Disk"
  #echo $DISK
  #echo $DISK_VAL
  echo "$MEMORY|$DISK|$CPU"

  if [[ $DISK > $DISK_VAL ]]
  then
     echo "Disk Alert Pressure"
     top -n 1 -b > /tmp/aksreport.out
     ps aux >> /tmp/aksreport
  fi

  if [[ $MEMORY > $MEM_VAL ]]
  then
     echo "MemoryAlert"
     top -n 1 -b > /tmp/aksreport.out
     ps aux >> /tmp/aksreport
  fi

  if [[ $CPU > $CPU_VAL ]]
  then
    echo "CPU Alert"
    top -n 1 -b > /tmp/aksreport.out
    ps aux >> /tmp/aksreport
  fi
  
  sleep 5
done
