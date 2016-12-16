# get names of runnning containers
RUNNING="$(docker ps --format '{{.Names}}')"
if [ -z "$RUNNING" ]; then
	#start the containers
	echo 'starting aerospike and rabbitmq containers.'
	docker run -tid --name aerospike -p 3000:3000 -p 3001:3001 -p 3002:3002 -p 3003:3003 aerospike/aerospike-server
	docker run -tid --name rmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
	echo 'waiting for aerospike start-up.'
    sleep 10
else
	echo 'rmq and aerospike containers already running.'
fi

CLRY="$(ps auxww | grep 'celery' | awk '{print $2}')"
if [ -z "$CLRY" ]; then
	#start the engine
    echo 'starting event engine.'
    celery worker --beat --detach --app=tentacle.endpointworker.app --scheduler=tentacle.schedulers.EventScheduler -l debug -f eventengine.log
    echo 'event engine started.'
else
	echo 'event engine running. restarting.'
	ps auxww | grep 'celery' | awk '{print $2}' | xargs kill -9
	rm eventengine.log
	celery worker --beat --detach --app=tentacle.endpointworker.app --scheduler=tentacle.schedulers.EventScheduler -l debug -f eventengine.log
fi
