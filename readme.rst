ONEm Event Engine - codename Tentacle


Introduction:

	Tentacle is a single node event engine implementation,
based on the scheduling and delivery functionalities provided
by Celery and Celery Beat.

	The main flow of the system is as follows:
1. a message (a dict) containing all the task infos
hits the registration endpoint (put)
2. the message is validated and registered in the main 
event repository, returning an 'ok' signal
3. at fixed intervals the running event loop will sync
with the main event repository, loading any new events
4. at the time or interval specified in the task info,
the task is sent as a message to the respective worker

	Tasks come in two flavours: Kraken or Nautilus.
	For Kraken, they are adapted to the specific format used
by the Kraken rpc engine, so they will need to be submitted
in that format as well.
	For Nautilus, they follow the standard Celery task description
with the attributes that would be expected in this situation.
Below you will find a short description of this

Installation:

	Tentacle has one hard dependency (Aerospike DB).
	It uses the database as the main datastore for all
the events that get processed in the event loop.
	It needs access to a RabbittMQ queue to receive the
incoming messages to the event processing endpoints, and
it needs to connect to the Kraken and Nautilus vhosts and
exchanges in order to submit the work messages.

	Installation of the engine can be done with the
install script found in tentacle/scripts/install_tentacle.sh.

	To run the app in development mode, use the testing
script: tentacle/scripts/test_engine.sh
	In development mode the app uses two local docker
containers to hold Aerospike and RabbitMQ. You need to
make sure docker is installed on the system before running.

	To run the app in production, use the normal mode:
tentacle/scripts/start_engine.sh.



Monitoring:



Usage: