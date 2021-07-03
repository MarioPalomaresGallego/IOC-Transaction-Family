# IOC-Transaction-Family

## Introduction

This is an implementation of a [Sawtooth](https://sawtooth.hyperledger.org/docs/core/releases/latest/contents.html) Transaction family. The idea behind this TF is to establish an IOC sharing platform that addresses the main weaknesses that current IOC sharing platforms face. These weaknesses are:

- Centralized infrastructure which is always prone to a variety of DoS attacks as well as easing data poisoning
- Lack of data validation. It turns out to be that IOC distribution is relies on trustful bonds, this not only questions the data validity but also limits its distribution.

The idea of a blockchain network plus a proper validdation logic leads to a novel IOC shraing platform which by solving the mentioned weaknesses poses itself as an incredibly realiable source of information. However, developing a validation logic for each type of IOC requires time if one wants that logic to be as autonomous as possible, that is, not relying on current IOC-related websites (which are the ones that have the reported weaknesses). For this reson this TP only covers malicious software IOC, mainly because this are one of the most demanded. Note that, extending this tool for additional IOC would be as simple as developing another completely independent TP.

## Model

The blockchain network would not only store the hash of the samples that turn out to be malicous but the whole behavioural report, which is a much richer information since it contains additional IOC that are much more resilient than the file hash. In order to validate the incoming behavioural reports an automatic sandboxing environment will be established on each node of the blockchain network. To this extent [CAPE sandboxing](https://github.com/kevoreilly/CAPEv2) tool was used. This is an oupensource tool based on [Cuckoo](https://github.com/cuckoosandbox/cuckoo) which enables to setup a physical sandbox environment, fact that significantly decreases the false negative rate detection of sandboxes.


## Installation

Installation process to try the TP isn't quick an requires a multiple step process. Following some usefull links to install the different components are provided:

- [Hyperledger Sawtooth Network Setup](https://sawtooth.hyperledger.org/docs/core/releases/latest/app_developers_guide/ubuntu_test_network.html): When reaching the steps about the consensus algorithm choose any of them since the implementation is independent from this
- [CAPE + Physical Environment (FOG)](https://mariohenkel.medium.com/using-cape-sandbox-and-fog-to-analyze-malware-on-physical-machines-4dda328d4e2c) 

## Run

In order to ease the deployment of CAPE and Sawtooth the setup.sh script is provided. This script executes all the processes required both for CAPE and Sawtooth. Since those are quite a lot an special tool that properly arranges all the windows is needed. The chosen tool is called [Tmux](https://man7.org/linux/man-pages/man1/tmux.1.html), this is a terminal multiplexer that enables the creation of multiple terminals managed under the same terminal instance. It enables to group several terminals in such way that a user copes extremely well even with a high number of them, something otherwise would be impossible. Since the tool is not mouse compatible following we explain the minimal configurations required to ease its usage, however reading its [man page](https://man7.org/linux/man-pages/man1/tmux.1.html) is advisable to get to know better the tool:

- Install: sudo apt-get install tmux
- Enable intra-window mouse support: nano $HOME/.tmux.conf  -> Add "set-option -g mouse on"
- Inter-windows move: Crtl+b + Page number. The page number can be seen at the bottom of the tmux interface
- Download de setup.sh file and fill in the required values

!WARNING¡ Some of the values to fill correspond to the user password those are required since some processes must be run with "sudo". Hence the file must be properly protected and not uploaded to any online service


In order to run the client TODO
