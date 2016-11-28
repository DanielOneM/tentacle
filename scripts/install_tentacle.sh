if [ ! -d "venv"]; then
	virtualenv venv
fi
venv/bin/pip install aerospike --install-option="--lua-system-path=venv/lua"
venv/bin/pip install -r requirements.txt
