
#!/bin/sh

IP = $(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | grep -v '192.168.122')
#PATH to the directory containing the cloned githubs of Sawtooth and CAPE
ROOT_PATH=""
#Dir name of CAPE repository
CAPE=""
#Dir name of Sawtooth repository
SAWTOOTH=""

tmux new-session -d -n "CAPE" -c "$ROOT_URL$CAPE" -s "ioc"

#CAPE
if [[ $1 = "cape" || $1 = "" ]];
then

	tmux split-window -c "$ROOT_URL$CAPE" -t ioc:0.0 -h
	tmux split-window -c "$ROOT_URL$CAPE" -t ioc:0.1 -v
	tmux split-window -c "$ROOT_URL$CAPE/web" -t ioc:0.2 -v
	tmux send-keys -t ioc:0.0 "python3 cuckoo.py" Enter
	tmux send-keys -t ioc:0.1 "python3 utils/process.py -p7 auto" Enter
	tmux send-keys -t ioc:0.2 "sudo python3 utils/rooter.py -g mario" Enter
	tmux send-keys -t ioc:0.2 "" Enter #Write user key !CAREFUL¡
	tmux send-keys -t ioc:0.3 "python3 manage.py runserver" Enter
fi

#SAWTOOTH
if [[ $1 = "saw" || $1 = "" ]];
then

	tmux new-window -c "ROOT_URL$SAWTOOTH" -n "SAWTOOTH"
	tmux split-window -c "$ROOT_URL$SAWTOOTH" -t ioc:1.0 -h
	tmux split-window -c "$ROOT_URL$SAWTOOTH" -t ioc:1.0 -v
	tmux split-window -c "$ROOT_URL$SAWTOOTH" -t ioc:1.0 -v
	tmux split-window -c "$ROOT_URL$SAWTOOTH" -t ioc:1.3 -v
	tmux send-keys -t ioc:1.0 "sudo -u sawtooth sawtooth-validator -vv" Enter
	tmux send-keys -t ioc:1.0 "" Enter #WRITE USER KEY !CAREFUL¡
	tmux send-keys -t ioc:1.1 "sudo -u sawtooth devmode-engine-rust -vv --connect tcp://localhost:5050" Enter
	tmux send-keys -t ioc:1.1 "" Enter #WRITE USER KEY !CAREFUL¡
	tmux send-keys -t ioc:1.2 "sudo -u sawtooth sawtooth-rest-api -vv" Enter
	tmux send-keys -t ioc:1.2 "" Enter #WRITE USER KEY !CAREFUL¡
	tmux send-keys -t tfm:1.3 "sudo -u sawtooth pbft-engine -vv --connect tcp://$IP:5050" Enter
	tmux send-keys -t tfm:1.3 "" Enter #wRITE USER KEY !CAREFUL¡
	tmux send-keys -t tfm:1.4 "sudo -u sawtooth xo-tp-python -vv" Enter
	tmux send-keys -t tfm:1.4 "" Enter #WRITE USER KEY !CAREFUL¡ 
fi

#WORK
tmux new-window -n "SAWTOOTH_GUI" -C "$ROOT_PATH$SAWTOOTH$SAWTOOTH_GUI"
tmux new-window -n "WORK"

tmux attach
