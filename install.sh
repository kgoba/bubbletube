#/bin/bash

cp bubbletube.service /etc/systemd/system/
cp pigpiod.service /etc/systemd/system

systemctl enable bubbletube.service
systemctl enable pigpiod.service

