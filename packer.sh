#!/bin/bash

#!/bin/bash
if [ "$#" -ne 1 ]; then
    echo "You must specify a valid amazon account from your credentials file"
    return
else
    account=$1
    account_data=`cat ~/.aws/credentials|grep -A4 $account`
    access_key=`echo "$account_data"|grep aws_access_key_id|cut -d= -f2|xargs`
    secret_key=`echo "$account_data"|grep aws_secret_access_key|cut -d= -f2|xargs`
    ROLE="CreateAmi"
    ACCOUNT_ID="909056075994"
    #SOURCE_AMI="ami-fd77469b" #2008
    SOURCE_AMI="ami-d3dee9b5" #2012

    CMD_ARGS="-var aws_account_id=$ACCOUNT_ID  -var role=$ROLE -var access_key=$access_key -var secret_key=$secret_key"
    CMD_ARGS="$CMD_ARGS -var ec2_source_ami=$SOURCE_AMI"

    COMMAND="packer build $CMD_ARGS ./gaming-rig.json"

    $COMMAND
fi