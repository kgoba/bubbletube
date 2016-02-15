#/bin/bash

cp dhcp-update-rules /etc/dhcp/dhclient-exit-hooks.d/update-src
cp usb-update-rules /etc/udev/rules.d/11-usb-media-automount.rules

cp bubbletube-update.service /etc/systemd/system/
cp bubbletube.service /etc/systemd/system/
cp pigpiod.service /etc/systemd/system

systemctl enable bubbletube-update.service
systemctl enable bubbletube.service
systemctl enable pigpiod.service

