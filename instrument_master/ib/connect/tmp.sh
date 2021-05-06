FIXUSERID=
FIXPASSWORD=

#IB_CONNECT_APP=GATEWAY
IB_CONNECT_TRUSTED_IPS=""
#IB_CONNECT_VNC_PASSWORD=
IB_CONNECT_API_PORT=4003
IB_CONNECT_VNC_PORT=5901

IB_CONNECT_APP=TWS
#IB_CONNECT_USER=sagges014
#IB_CONNECT_PASSWORD=password456

IB_CONNECT_VNC_PASSWORD=12345

USER="gp"

TWSUSERID="gpsagg314" \
TWSPASSWORD="test" \
IB_APP=$IB_CONNECT_APP \
IMAGE="665840871993.dkr.ecr.us-east-1.amazonaws.com/im_tws:local" \
TRUSTED_IPS=$IB_CONNECT_TRUSTED_IPS \
VNC_PASSWORD=$IB_CONNECT_VNC_PASSWORD \
API_PORT=$IB_CONNECT_API_PORT \
VNC_PORT=$IB_CONNECT_VNC_PORT \
docker-compose \
    -f devops/compose/docker-compose.local.yml \
    run --rm \
    -l user=$USER \
    -l app="ib_connect" \
    --service-ports \
    tws \
    /bin/bash
