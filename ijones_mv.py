#!/usr/bin/python
import os
import sys
import shutil
import subprocess
import logging
import smtplib
import re

import rtorrent_config as config

if config.logfile != None:
    logging.basicConfig(filename=config.logfile,format='%(asctime)s %(message)s',level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')


##### EXTENSIONS #####
logging.debug("defining extensions")
video_extensions = config.video_extensions
compressed_extensions = config.compressed_extensions

##### FINAL DIR #####
logging.debug("Defining dirs")
final_stop = config.final_stop
tvshow_stop = config.tvshow_stop
videos_stop = config.videos_stop

##### MAIL #####
logging.debug("Defining mail information")
username    = config.username
password    = config.password
mailserver  = config.mailserver
mailport    = config.mailport
frm         = config.frm
to          = config.to
usetls      = config.usetls

def move(src,dst,opts=None,step2=False):
    logging.debug("Entering move(src=%s,dst=%s,opts=%s,step2=%s)" % (src,dst,opts,step2))
    logging.debug("src: %s" % src)
    logging.debug("dst: %s" % dst)
    if opts == None: opts = ""
    opts = opts.split()
    logging.debug("opts: %s" % opts)
    logging.debug("pwd: %s" % os.getcwd())
    logging.debug("listdir: %s" % os.listdir("."))
    step2_dst = dst
    if not step2:
        dst = get_real_dst(src,dst)
    logging.debug('moving from ' + src + ' to ' + dst)
    rc = subprocess.Popen(["mv"] + opts + [src,dst] ).wait()
    logging.debug("moving rc: %s " % rc)
    if step2:
        logging.debug("spawing next process")
        dst = step2_dst
        if rc == 0:
            if src[-1] == '/':
                src = src[:-1]
            subprocess.Popen(["nohup",sys.argv[0],"step2",os.path.join(dst,os.path.basename(src))])
#            subprocess.Popen(["nohup",sys.argv[0],"step2",os.path.join(dst,os.path.basename(src))],stdout=open("/dev/null","w"),stderr=open("/dev/null","w"))
        sys.exit(rc)

def movie(src,dst):
    true_dst =  os.path.join(videos_stop,src)
    logging.debug("true_dst: %s" % true_dst)
    os.makedirs(true_dst)
    return true_dst

def get_tv_show_name(src):
    aux = re.search(".*/(\S+)\.(s\d+)e\d+",src,re.I)
    if aux:
        aux,season = aux.groups()
        aux = aux.replace("./","")
        aux = aux.replace("."," ")
        logging.debug("tvshow name = %s" % aux)
        return aux, season

def tvshow(src,dst):
    logging.debug("tv show - %s" % src)
    tv_show_name, tv_season = get_tv_show_name(src)
    logging.debug("tv_show_name = %s" % tv_show_name)
    logging.debug("tv_season = %s" % tv_season)
    tv_show_dir = tvshow_stop
    logging.debug("tv_show_dir = %s" % tv_show_dir)
    tv_shows = os.listdir(tv_show_dir)
    logging.debug("tv_shows = %s" % tv_shows)
    true_dst = os.path.join(tv_show_dir, tv_show_name, tv_season.upper())
    ref_size = tv_show_name.split()
    splits = 0
    if ref_size > 2:
        splits = len(ref_size) / 2
    while splits >= 0:
        tv_list = []
        tv_show_aux = tv_show_name.rsplit(None,splits)[0]
        for tv_show in tv_shows:
            logging.debug("tv_show = %s" % tv_show)
            if re.search(tv_show_aux, tv_show.replace(".", " "), re.I):
                logging.debug("tv_show found: %s " % tv_show)
                tv_list.append(tv_show)
                logging.debug("tv_show added to list")
        if len(tv_list) == 1:
            true_dst = os.path.join(tv_show_dir, tv_list[0], tv_season.upper())
            break
        splits -= 1
    if not os.path.isdir(true_dst):
	os.makedirs(true_dst)
    logging.debug("true_dst: %s" % true_dst)
    return true_dst


def get_real_dst(src,dst):
    if re.search("s\d+e\d+",src,re.I):
        logging.debug("tv show - %s" % src)
        return tvshow(src,dst)
    logging.debug("movie")
    return movie(src,dst)

def copy(src,dst,remove=False):
    logging.debug("copying %s %s" % (src,dst))
    ok = False
    try:
        dst = get_real_dst(src,dst)
        logging.debug("final dst = %s" % dst)
        shutil.copy(src,dst)
        ok = True
    except:
        logging.debug("not copied %s" % (sys.exc_info(),))
    if not ok:
        try:
            logging.debug("trying with %s %s" % (src,dst + "/" + src))
            shutil.copyfile(src,dst + "/" + src)
            ok = True
        except:
            logging.debug("not copied again. %s" % (sys.exc_info(),))
            for i in os.environ:
                logging.debug("Env: %s: %s" % (i,os.environ[i]))
    if not ok:
        try:
            logging.debug("trying with %s %s" % (src,dst + "/" + src))
            s,e = subprocess.Popen('whoami',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
            logging.debug("stdout = %s" % s)
            logging.debug("stderr = %s" % e)
        except:
            logging.debug("not copied again. %s" % (sys.exc_info(),))
            for i in os.environ:
                logging.debug("Env: %s: %s" % (i,os.environ[i]))
    subprocess.Popen(['ls', '-s', dst, src])
    return

def match_ext(filelist,extlist):
    logging.debug("matching extension")
    logging.debug("running through filelist")
    logging.debug("filelist: %s" % filelist)
    for filename in filelist:
        ext = os.path.splitext(filename)[1]
        logging.debug("file: %s" % filename)
        logging.debug("ext: %s" % ext)
        logging.debug("extlist: %s" % extlist)
        if filename.lower().find('sample') >= 0:
            logging.debug("Sample found.n skipping")
            continue
        if ext in extlist:
            logging.debug("extension found")
            yield filename

def has_video(filelist):
    logging.debug("searching video")
    return match_ext(filelist,video_extensions)

def has_compressed(filelist):
    logging.debug("searching compressed")
    return match_ext(filelist,compressed_extensions)

def uncompress(path,filepath):
    logging.debug("uncompressing")
    ext = os.path.splitext(filepath)[1]
    fwd,filename = os.path.split(filepath)
    logging.debug("Decompressing %s on %s" % (filename,fwd))
    logging.debug("pwd: %s" % os.getcwd())
    cmd = ""
    if ext == ".rar":
        logging.debug("rar found")
        cmd = ["/usr/bin/unrar","x","-y",filename]
    if ext == ".zip":
        logging.debug("zip found")
        cmd = ["/usr/bin/unzip","-o",filename]
    if len(cmd) > 0:
        logging.debug("subprocessing cmd: %s " % cmd)
        proc = subprocess.Popen(cmd,cwd=fwd)
        proc.wait()
#        proc = subprocess.Popen(cmd,shell=True,cwd=path)

def mail(frm,to,subj,emsg):
    msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % ( frm, to, subj, emsg )
    logging.debug("email msg: %s " % msg)
    server = smtplib.SMTP(mailserver,mailport)
    if usetls: server.starttls()
    server.login(username,password)
    server.sendmail(frm, to,msg)
    server.close()

def step2():
    logging.debug("step2")
    msg = ""
    fullpath = sys.argv[2]
    path,base = os.path.split(fullpath)
    os.chdir(path)
    logging.debug("changing path to %s " % path)
    if os.path.isdir(fullpath):
        logging.debug("is dir")
        os.chdir(fullpath)
    if os.path.isfile(fullpath):
        logging.debug("is file")
        filename,ext = os.path.splitext(fullpath)
        if ext in video_extensions:
            logging.debug("spaw copy")
            copy(fullpath,final_stop)
            sys.exit("done")
    curdir = os.getcwd()
    for path,dirs,files in os.walk("."):
#        os.chdir(os.path.join(curdir,path))
        logging.debug("walking %s" % path)
#        compressed_files = has_compressed(files)
#        video_files = has_video(files)
        compressed_files = has_compressed([os.path.join(path,filepath) for filepath in files])
        video_files = has_video([os.path.join(path,filepath) for filepath in files])
        compressed_file = None
        video_file      = None
        video_done = []
        for video_file in video_files:
            logging.debug("video file: %s " % video_file)
            msg += "File %s found.\nCopying\n" % (video_file,)
            copy(video_file,final_stop)
            video_done.append(video_file)
        for compressed_file in compressed_files:
            logging.debug("compressed file: %s " % compressed_file)
            logging.debug("uncompress")
            uncompress(path,compressed_file)
            logging.debug("relisting video")
            video_files = has_video([os.path.join(path,filepath) for filepath in os.listdir(path)])
            msg += "File %s uncompressed.\n" % (compressed_file,)
            for video_file in video_files:
                if video_file in video_done:
                    continue
                msg += "File %s found.\nMoving\n" % (video_file,)
                logging.debug("new video: %s" % video_file)
                move(video_file,final_stop)
        if not compressed_file and not video_file and not msg:
            msg += "Did not found compressed file, neither video file!"
    mail(frm,to,"Finished cycle: %s" % curdir,msg)

if __name__ == "__main__":
    logging.debug("main")
    logging.debug("sys.argv: %s" % sys.argv)
    if sys.argv[1] == "step2":
        logging.debug("steping 2")
        step2()
    if len(sys.argv) < 3:
        sys.exit("Too few arguments")
    logging.debug("still main")
    if len(sys.argv) == 4:
        logging.debug("moving")
        move(sys.argv[2],sys.argv[3],sys.argv[1],step2=True)
    logging.debug("out")

sys.exit()

