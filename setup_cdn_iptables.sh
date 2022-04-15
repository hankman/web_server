#!/bin/bash

iptables -F

for i in `curl https://www.cloudflare.com/ips-v4`; do
    iptables -I INPUT -p tcp -s $i --dport http -j ACCEPT;
    iptables -I INPUT -p tcp -s $i --dport https -j ACCEPT;
done

#iptables -A INPUT -m state --state RELATED,ESTABLISHED -m limit --limit 150/second --limit-burst 160 -j ACCEPT

iptables -A INPUT -p tcp --dport http -j DROP
iptables -A INPUT -p tcp --dport https -j DROP
