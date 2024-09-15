FROM jasonish/suricata

# Install iptables using dnf
RUN dnf -y update && dnf -y install iptables && dnf clean all

# Set the command to configure iptables and start Suricata
CMD /usr/sbin/iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 172.19.5.2