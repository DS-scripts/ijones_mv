#!/usr/bin/python
import logging

##### EXTENSIONS #####
video_extensions = [".mkv",".avi",".mov",".mp4"]
compressed_extensions = [".rar",".zip"]

##### FINAL DIR #####
final_stop = "/home/torrent/torrents/to_watch"
final_stop = "/home/torrent/downloads"
tvshow_stop = "/mnt/buffalo/downloads/tvshows/"
videos_stop = "/mnt/buffalo/downloads/videos/"

##### MAIL #####
username    = "spontarolli@gmail.com"
password    = "qpcduhrsnwhdxvem"
mailserver  = "smtp.gmail.com"
mailport    = 587
frm         = "spontarolli@gmail.com"
to          = "spontarolli@gmail.com"
usetls      = True

##### LOG #####
logfile = "/tmp/torrent_mv.log"
#logfile = None
