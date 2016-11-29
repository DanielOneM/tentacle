CLRY="$(ps auxww | grep 'celery' | awk '{print $2}')"
LOGFILE="eventengine.log"

if [[ -e $LOGFILE ]] ; then
    i=0
    while [[ -e $LOGFILE.$i ]] ; do
        let i++
    done
    LOGFILE=$LOGFILE.$i
fi

if [ -z "$CLRY" ]; then
	#start the engine
    echo 'starting event engine.'
    celery worker --beat --detach --app=tentacle.endpointworker.app --scheduler=tentacle.schedulers.EventScheduler -l info -f eventengine.log
    echo 'event engine started.'
else
	echo 'event engine running. restarting.'
	ps auxww | grep 'celery' | awk '{print $2}' | xargs kill -9
	mv eventengine.log $LOGFILE
	celery worker --beat --detach --app=tentacle.endpointworker.app --scheduler=tentacle.schedulers.EventScheduler -l info -f eventengine.log
fi