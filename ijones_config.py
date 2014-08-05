#!/usr/bin/python
import logging

##### EXTENSIONS #####
video_extensions = [".mkv",".avi",".mov",".mp4"]
compressed_extensions = [".rar",".zip"]

##### FINAL DIR #####
final_stop = "/home/torrent/torrents/to_watch"

##### MAIL #####
username    = "seumail@gmail.com"
password    = "pass"
mailserver  = "smtp.gmail.com"
mailport    = 587
frm         = "seumail@gmail.com"
to          = "seumail@gmail.com"
usetls      = True

##### LOG #####
#logfile = "/tmp/torrent_mv.log"
logfile = None
