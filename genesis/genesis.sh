if [[ $1 =  "dev" ]];
then
	sudo -u sawtooth sawadm genesis config-genesis.batch devmode-config.batch
elif [[ $1 = "bft" ]];
then
	sudo -u sawtooth sawadm genesis config-genesis.batch pbft-config.batch
else
	sudo -u sawtooth sawadm genesis config-genesis.batch poet.batch poet-config.batch
fi
