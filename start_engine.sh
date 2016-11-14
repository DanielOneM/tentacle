#start the containers
docker rm -f aerospike rmq
docker run -tid --name aerospike -p 3000:3000 -p 3001:3001 -p 3002:3002 -p 3003:3003 aerospike/aerospike-server
docker run -tid --name rmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

#start the engine
sleep 10
celery worker --beat --detach --app=tentacle.endpointworker.app --scheduler=tentacle.schedulers.EventScheduler -l info -f eventengine.log
