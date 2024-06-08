The need to write this was from broadcast storms using MDNS and SSDP that came from a popular home automation platform (control4)
The main controller would periodically flood my LAN with UDP broadcast storms to all nodes, at port 5353. Others where in there too like SSDP
These appear to be periodic "discovery" probes to either aid in setup of devices, or figure out what else I have on the LAN
I dont mind those so much and it usually does this about 1 or 2 times every 10 seconds

The problem was the device was emitting MDNS broadcast packets at a rate of 1 every << 1ms. Thats over a 1,000 a second

I eventually got wireshark out on my desktop and saw it

I used a LAN tap at the device emitting them to get everything else

No root cause from vendor yet, but, it magically started this on a Thursday and Sunday AM at 8:35 it stopped. That time is way too close to a normal weekend change window to be random

Symptoms and actions
1. Network audio streamer began to pop and distort
2. Two of my Ubiquit Access points failed due to thermal issues (two of the 7 I have). Those two are both new U7-Pro models
3. Control4 itself a day after the audio and AP issues began to fail hard - house down!
4. Rebooting it only gave me a few hours before it began again

Motivation for this repo
1. I was looking for a way to build a wireshark capture in command line and automate it to output and alert - way too complex (for me)
2. Broadcast events are sent to my desktop as well, so I dont need a LAN TAP
3. I researched and found "scapy" was the best way to pick out packet types - scapy is only supported up to Python 3.11, I havent tried higher yet
4. I used win10toast for local notification
5. I wanted a capture log in csv format
6. I found pushover notifications and a python module for it, so I setup my account and keys
7. 
