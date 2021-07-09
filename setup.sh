
#!/bin/sh

IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | grep -v '192.168.122')
# Path to the directory containing the cape and IOC-Transaction family cloned repos
ROOT_PATH=""
# Name of the folder containing the cloned CAPE project
CAPE=""
# Name of the folder contianing the cloned IOC-TP project
SAWTOOTH=""
SAWTOOTH_GUI="/client/IOC_Site/"

# WRITE YOUR USER PASSWORD !CAREFULL¡ PROTECT THE FILE PROPERLY
PASSWORD=""

tmux new-session -d -n "CAPE" -c "$ROOT_PATH$CAPE" -s "tfm"

#CAPE
if [[ $1 = "cape" || $1 = "both" ]];
then

	tmux split-window -c "$ROOT_PATH$CAPE" -t tfm:0.0 -h
	tmux split-window -c "$ROOT_PATH$CAPE" -t tfm:0.1 -v
	tmux split-window -c "$ROOT_PATH$CAPE/web" -t tfm:0.2 -v
	tmux send-keys -t tfm:0.0 "python3 cuckoo.py" Enter
	tmux send-keys -t tfm:0.1 "python3 utils/process.py -p7 auto" Enter
	tmux send-keys -t tfm:0.2 "sudo python3 utils/rooter.py -g mario" Enter
	tmux send-keys -t tfm:0.2 "$PASSWORD" Enter # WRITE USER KEY !CAREFUL¡
	tmux send-keys -t tfm:0.3 "python3 manage.py runserver" Enter
fi

#SAWTOOTH
if [[ $1 = "saw" || $1 = "both" ]];
then

	tmux new-window -c "ROOT_PATH$SAWTOOTH" -n "SAWTOOTH"
	tmux split-window -c "$ROOT_PATH$SAWTOOTH" -t tfm:1.0 -h
	tmux split-window -c "$ROOT_PATH$SAWTOOTH" -t tfm:1.0 -v
	tmux split-window -c "$ROOT_PATH$SAWTOOTH" -t tfm:1.0 -v
	tmux split-window -c "$ROOT_PATH$SAWTOOTH" -t tfm:1.3 -v
	tmux split-window -c "$ROOT_PATH$SAWTOOTH/processor" -t tfm:1.3 -v
	tmux send-keys -t tfm:1.0 "sudo -u sawtooth sawtooth-validator -vv" Enter
	tmux send-keys -t tfm:1.0 "$PASSWORD" Enter
	tmux send-keys -t tfm:1.1 "sudo -u sawtooth settings-tp -v" Enter
	tmux send-keys -t tfm:1.1 "$PASSWORD" Enter
	tmux send-keys -t tfm:1.2 "sudo -u sawtooth sawtooth-rest-api -vv" Enter
	tmux send-keys -t tfm:1.2 "$PASSWORD" Enter

	if [[ $2 = "bft" ]];
	then
		tmux send-keys -t tfm:1.3 "sudo -u sawtooth pbft-engine -vv --connect tcp://$IP:5050" Enter
		tmux send-keys -t tfm:1.3 "$PASSWORD" Enter
	elif [[ $2 = "dev" ]];
	then
		tmux send-keys -t tfm:1.3 "sudo -u sawtooth devmode-engine-rust -vv --connect tcp://$IP:5050" Enter
		tmux send-keys -t tfm:1.3 "$PASSWORD" Enter
	else
		tmux send-keys -t tfm:1.3 "sudo -u sawtooth poet-engine -vv --connect tcp://$IP:5050" Enter
		tmux sned-keys -t tfm:1.3 "$PASSWORD" Enter
		# TODO: Add logic to launch the registry validator
	fi
	tmux send-keys -t tfm:1.4 "sudo -u sawtooth xo-tp-python -vv" Enter
	tmux send-keys -t tfm:1.4 "$PASSWORD" Enter
	tmux send-keys -t tfm:1.5 "python3 server.py" Enter
fi

#WORK

tmux new-window -n "SAWTOOTH_GUI" -c "$ROOT_PATH$SAWTOOTH$SAWTOOTH_GUI"

tmux send-keys -t tfm:2.0 "python3 manage.py runserver 0.0.0.0:8081" Enter

tmux attach
