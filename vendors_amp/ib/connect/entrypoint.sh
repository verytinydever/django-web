#!/usr/bin/env bash

export PYTHONPATH=$PYTHONPATH:/amp

# Create configurations for controller.
CMD="python vendors_amp/ib/connect/scripts/make_ib_controller_init_file.py \
     --user ${TWSUSERID} \
     --password ${TWSPASSWORD} \
     --stage ${STAGE}"

echo $CMD
eval $CMD

CMD="python vendors_amp/ib/connect/scripts/make_jts_init_file.py \
    --trusted_ips 127.0.0.1,${VNC_TRUSTED_IPS}"
echo $CMD
eval $CMD

# Run controller.
xvfb-daemon-run /opt/IBController/Scripts/DisplayBannerAndLaunch.sh &

# Tail latest in log dir.
sleep 1
tail -f $(find $LOG_PATH -maxdepth 1 -type f -printf "%T@ %p\n" | sort -n | tail -n 1 | cut -d' ' -f 2-) &

# Give enough time for a connection before trying to expose on 0.0.0.0:4003
sleep 30
echo "Forking :::4001 onto 0.0.0.0:4003\n"
socat TCP-LISTEN:4003,fork TCP:127.0.0.1:4001