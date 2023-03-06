#! /usr/bin/bash
(crontab -l 2> /dev/null | grep -v mps_main) | crontab -
