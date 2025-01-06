#!/bin/bash

print_about() {
    echo """
Usage: Run './cli.sh <command>'. Following are the valid commands:
 
            run-api
                Runs API  along with Mongo
            
            run-dev-api-build
                Builds and runs API  along with Mongo

            stop-services
                Stops all containers
    """
}

CMD=$1
ARG1=$2

if [ "$0" = "bash" ];
    then
        CMD=$2
        ARG1=$3
fi



# Helper functions

start_services() {
    doppler run -- docker compose up mongodb -d
}

load_env() {
    # Loading doppler token, if exists
    if [[ ! -z "$ARG1" ]]; then
        echo "Starting with env file"
        export $(cat $ARG1 | grep -v "# " | xargs)
    else
        echo "Starting without env file"
    fi
}

load_env

case $CMD in
    "run-api")
        start_services
        doppler run -- docker compose up api
        ;;
    "stop-services") # Stops all runnning containers
        doppler run -- docker compose down
        ;;
esac