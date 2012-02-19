#!/usr/bin/env python
# This script captures screen output at regular intervals to then convert into a timelapse video. 

# TODO:
#  - Disable output maybe?
#
# DONE:
#  - Allow continuing timelapse frame captures
#  - Timestamp output
#  - Usage help
#  - Realtime user input on capture, so you don't have to ^C out

import os
import sys
import shutil

import time
import datetime

import re
import optparse

####################################### 
# Helpers
####################################### 

# Returns false if we don't have the correct programs installed.
def checkDependencies():
    return os.path.exists("/usr/bin/scrot") and \
           os.path.exists("/usr/bin/mencoder")

# Checks if the directory has frames recorded already, and returns an index value for the
# next frame.
def existingFrames(directory):
    # Create regular expression to match frame number, if it exists
    frameNumberRE = re.compile("Frame(\d*)-thumb.jpg")

    for filename in sorted(os.listdir(directory), reverse=True):
        matched = frameNumberRE.match(filename)
        if matched != None:
            return int(matched.group(1))
    return 0

####################################### 
# Actions
####################################### 
def capture(directory, size, interval, quality, silent):

    # If there are already frames in the output directory, continue that frame list
    count = existingFrames(directory)

    print ("Capturing every %i seconds..." % interval)
    while True:
        try:
            # 10000 frames should be enough for just about anyone
            if silent == None:
                print ("Time: %s :: Frame %04i" % (time.ctime(), count))
            file = "%s/Frame%04i.jpg" % (directory, count)

            #os.system("scrot %s -e 'convert $f -resize '%s' $f'" % (file, size))
            # This stops the user from being able to Ctrl-C out...
            #os.system("scrot -d %d %s -q %s -t %s -e 'rm %s'" % (interval, file, quality, size, file))

            # So I'm using this again...
            os.system("scrot %s -q %s -t %s -e 'rm %s'" % (file, quality, size, file))
            time.sleep(interval)

            count += 1
        except KeyboardInterrupt:
            print ("\nDone Capturing: %04i frames" % count)
            break


def compile(directory, outputFile, audioFile, framesPerSecond):
    print ("Compiling video file...")

    outputFile = "%s/%s" % (directory, outputFile)
    audioCommand = ""
    if audioFile != None:
        audioCommand = "-audiofile %s -oac pcm" % audioFile

    os.system("mencoder 'mf://%s/*.jpg' -mf fps=%i -o '%s' -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=800 %s" % (directory, framesPerSecond, outputFile, audioCommand))


def addAudio(directory, outputFile, audioFile):
    if audioFile == None:
        print ("No audio file specified.")
    else:
        print ("Adding audio to video file...")

    outputFile = "%s/%s" % (directory, outputFile)
    os.system("mencoder %s -audiofile %s -oac copy -ovc copy -o %s.tmp" % (outputFile, audioFile, outputFile))
    shutil.move(outputFile + ".tmp", outputFile)


####################################### 
# Main
####################################### 
if __name__ == "__main__":
    if not checkDependencies():
        print ("This script needs scrot/mencoder to run")
        sys.exit(1)

    usage="\n%prog -d ~/tmp/frames/ -i <inteval> -s <size percentage> -q <quality> --capture\n%prog -o <outputname> -a someAudioFile -f fps --compile"

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-d", action="store", type="string", dest="directory", help="Image output directory. Default: '.'", default=".")
    parser.add_option("-i", action="store", type="int", dest="interval", help="Time interval between screenshots (in seconds). Default: 60", default=60)
    parser.add_option("-s", action="store", type="string", dest="size", help="Resize Ratio (preferably as a percentage). Default: 50%", default="50%")
    parser.add_option("-q", action="store", type="string", dest="quality", help="Image quality as an integer between 1 and 100. Default: 75", default="75")
    parser.add_option("-n", action="store_true", dest="silent", help="Supresses output during capture.")

    parser.add_option("-o", action="store", type="string", dest="output", help="Video output file. Default: 'timelapse.mp4'", default="timelapse.mp4")
    parser.add_option("-a", action="store", type="string", dest="audio", help="Audio overlay file.")
    parser.add_option("-f", action="store", type="int", dest="fps", help="Frames per second for the video file. Default: 10", default=10)

    parser.add_option("--capture", action="store_true", dest="capture", help="Capture screen images -- Related options: Directory, Size, Interval")
    parser.add_option("--compile", action="store_true", dest="compile", help="Compile images to video -- Related options: Directory, Output, Audio, Frames Per Second")

    parser.add_option("--addAudio", action="store_true", dest="addAudio", help="Add audio to video -- Related options: Directory, Output, Audio")

    (options, args) = parser.parse_args()

    if not options.capture == None:
        capture(options.directory, options.size, options.interval, options.quality, options.silent)
    elif not options.compile == None:
        compile(options.directory, options.output, options.audio, options.fps)
    elif not options.addAudio == None:
        addAudio(options.directory, options.output, options.audio)
    else:
        parser.print_help()

