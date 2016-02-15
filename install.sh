#/bin/bash

cp bubbletube-update.service /etc/systemd/system/
cp bubbletube.service /etc/systemd/system/
cp pigpiod.service /etc/systemd/system

systemctl enable bubbletube-update.service
systemctl enable bubbletube.service
systemctl enable pigpiod.service

