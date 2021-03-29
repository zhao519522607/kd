#! /bin/bash

DIR=$(cd "$(dirname "$0")"; pwd)
name=(customer seller statistics job)
file_dir="/data/zyb/kd"

upload_job(){
    ansible -i $DIR/hosts job -m copy -a "src=$file_dir/job.war dest=/data/upload/job.war owner=sdk group=sdk"
}

action_job(){
    ansible -i $DIR/hosts job -b --become-user=sdk -m shell -a "echo $action > /data/upload/tmp"
}

if [ $# -eq 0 ];then
    echo "You can need two args"
    exit 1
elif [ $# -eq 1 ];then
   echo "You can need two args"
   exit 1
else
   if [[ ! "${name[*]}" =~ "$1" ]];then
       echo "$1 not in ${name[@]}"
       exit 1
   else
       case $2 in
           upload)
               if [ "$1" == "customer" ];then
                   upload_customer
               elif [ "$1" == "seller" ];then
                   upload_seller
               elif [ "$1" == "statistics" ];then
                   upload_statistics
               elif [ "$1" == "job" ];then
                   upload_job
               fi
               ;;
           update)
               action=$2
               if [ "$1" == "customer" ];then
                   action_customer
               elif [ "$1" == "seller" ];then
                   action_seller
               elif [ "$1" == "statistics" ];then
                   action_statistics
               elif [ "$1" == "job" ];then
                   action_job
               fi
               ;;
           rollback)
               action=$2
               if [ "$1" == "customer" ];then
                   action_customer
               elif [ "$1" == "seller" ];then
                   action_seller
               elif [ "$1" == "statistics" ];then
                   action_statistics
               elif [ "$1" == "job" ];then
                   action_job
               fi
               ;;
           *)
               echo "Only upload/update/rollback choice!"
       esac
   fi
fi
