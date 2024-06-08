Truly a first-world problem, but, a problem. My smart-house died, and so did some wifi, and audio streaming. I found the root cause, and now want to be alerted ahead of failure.

The need to write this was from broadcast storms using MDNS and SSDP that came from a popular home automation platform (control4) the week of May 27

Beginning, around Thursday that week, the core control4 "director" device would flood my LAN with UDP broadcast storms, at port 5353. Others were in there too like SSDP
These appear to be periodic "discovery" probes to either aid in setup of devices, or figure out what else I have on the LAN ?!
I dont mind those so much and it usually does this about 1 or 2 times every 10 seconds

I eventually got wireshark out on my desktop and saw it
The problem was the device was emitting MDNS broadcast packets at a rate of 1 every << 1ms. Thats over a 1,000 a second

I used a LAN tap at the device emitting them to get everything else

No root cause from vendor yet, but, it magically started this on a Thursday and Sunday AM at 8:35 it stopped. That time is way too close to a normal weekend change window to be random

Symptoms and actions
1. Eversolo  audio streamer began to pop and distort (never does this) when using Tidal or Apple Music 
2. Two of my Ubiquiti Access points failed on Thursday at 4:15PM ET due to thermal and high CPU issues (two of the 7 I have). Those two are both new U7-Pro models. They would appear offline, and attempts to reset and re-adopt fail. They were incredibly hot when touched (a clue - high processing load)
3. Control4 itself a day after the audio and AP issues began to fail hard - house down! - Lights, TV, Audio, Locks, Alarm - nothing was working
4. Rebooting control4 only gave me a few hours before it began again. This was the case Saturday into Sunday
5. "IT Magic" occured Sunday at 8:35 AM ET - and its been fine ever since. So, what happens on a time that is 0,15,30,45 minutes after an hour, and on a weekend... change controls.... (could be ?)

Motivation for this repo
1. I was looking for a way to build a wireshark capture in command line and automate it to output and alert - way too complex (for me)
2. Broadcast events are sent to all devices on the subnet, so, I dont need a LAN TAP at the offending device, I just use my desktop
3. I explored if there were python modules that could scan interfaces, there were

How it works
1. I found "scapy" was the best way to pick out packet types - scapy is only supported up to Python 3.11, I havent tried higher yet
2. I used win10toast for local notification
3. I wanted a capture log in csv format
4. I found pushover notifications (iOS and Android) and a python module for it, so I setup an account and keys. Supply yours in the python code where it says Your Key or Token
5. Refine your loop time and threshold to suit - I use 10 second loop, 75 packets of this type or higher 
6. It sets up and loops polling the interface (you have to get the exact interface name from ipconfig/all and replace what I have here)
7. It logs every poll of the interface.
8. If it hits the threshold - it logs an alert message and then toasts it (local Windows)  and sends it to pushover - works very well

More to come likely as there are other broadcast style network issues I want to capture. I may even run this on a Pi connected to a dedicated LAN tap on suspect devices

This was MUCH easier than poking around my Ubiquiti router for logs, or enabling tcpdump on that device (which would degrade performance)

Enjoy!
