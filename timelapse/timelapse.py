# timelapse.py
#
# author:           Michael Bernhard
# available from:   https://github.com/mchlbrnhrd
#
# description:      Create timelapse movie from images.
#                   Also create blended images in between of two images. Number of blend steps
#                   can be choosen.
#
# run script:       python3 timelapse.py
#                   python3 timelapse.py -h

# GNU General Public License v3.0
#
# Copyright (C) 2022  Michael Bernhard
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PIL import Image
from PIL import ImageOps
import numpy as np
import PIL, sys

import time
import os
import sys
import cv2
import getopt

########################################################
# usage
#
# show help
########################################################
def usage():
  print("python3 timelapse.py [OPTION]")
  print("")
  print("options:")
  print("-f : fps            set frames per seconds for video output")
  print("-i : image path     set path of images")
  print("-o:  output path    set path for output video file")
  print("-b:  blend steps    set number of blend steps. 0: no additional blending")
  print("-n:  video name     name of video. filename ending mp4 is recommended")
  print("-m:  max images     set number of maximal used images from image path. 0: all images.")
  print("")
  print("-v:  verbose        activate verbose mode")
  print("-h:  help           show this help")

########################################################
# main
#
# set default parameter and get user defined options
########################################################
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvf:i:o:b:n:m:", ["help", "verbose", "fps=", "image_path=", "output_path=", "blend_steps=", "video_name="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    # default values
    verbose = False
    fps=24
    img_path=("./img")
    out_path=("./out")
    blend_steps=1
    video_name="timelapse.mp4"
    max_images=0
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--fps"):
            fps = int(a)
        elif o in ("-i", "--image_path"):
            img_path=a
        elif o in ("-o", "--output_path"):
          out_path=a
        elif o in ("-b", "--blend_steps"):
          blend_steps=int(a)
        elif o in ("-n", "--video_name"):
          video_name=a
        elif o in ("-m", "--max_images"):
          max_images=int(a)
        else:
            assert False, "unhandled option"

    img_path=os.path.abspath(img_path)
    out_path=os.path.abspath(out_path)
    
    return fps, img_path, out_path, blend_steps, video_name, max_images, verbose


########################################################
# progress_bar
#
# print progress bar on terminal
########################################################
def progress_bar(ctr, ctr_max, info):
  bar_length=30
  percent = 100.0*(ctr+1)/ctr_max
  sys.stdout.write('\r')
  sys.stdout.write(info + "[{:{}}] {:>3}%"
                 .format(chr(0x2589)*int(percent/(100.0/bar_length)),
                         bar_length, int(percent)))
  sys.stdout.flush()

########################################################
# delete_content
#
# delete all files in path.
########################################################
def delete_content(path, verbose):
  if verbose:
    print("delete content of " + path)
  os.chdir(path)
  ctr=0
  lst=os.listdir('.')
  for f in lst:
    #os.remove(f) # is deactivated, make sure you really want to delete files
    progress_bar(ctr, len(lst), "deleting:      ")
                                
    ctr+=1
  sys.stdout.write("\n")
  
########################################################
# get image list
#
# find all images in path and return in sorted order
########################################################
def get_image_list(path, verbose):
  if verbose:
    print("get image list of " + path)
  lst = [img for img in os.listdir(path)
          if img.endswith(".jpg") or
            img.endswith(".jpeg") or
            img.endswith(".JPG") or
            img.endswith(".JPEG") or
            img.endswith("png")]
  lst.sort()
  
  return lst
  
########################################################
# get_mean_size
#
# get mean size of all images of image list in img_path
########################################################
def get_mean_size(image_list, img_path, verbose):
  if verbose:
    print("get mean size of images in " + img_path)
  mean_width = 0
  mean_height = 0
  pre_width = 0
  pre_height = 0
  all_equal_flag=True
  numImages=len(image_list)
  
  ctr=0
  for file in image_list:
    im = Image.open(os.path.join(img_path, file))
    width, height = im.size
    if pre_width > 0:
      if (width != pre_width) or (height != pre_height):
        all_equal_flag = False;
    mean_width += width
    mean_height+=height
    pre_width = width
    pre_height = height
    progress_bar(ctr, numImages, "get mean size: ")
    ctr+=1

  mean_width = int(mean_width / numImages)
  mean_height = int(mean_height / numImages)
  sys.stdout.write("\n")
  if verbose:
    print("width: " + str(mean_width) + ", height: " + str(mean_height) + ", all equal: " + str(all_equal_flag))
    
  return mean_width, mean_height, all_equal_flag

########################################################
########################################################
# main
########################################################
########################################################
if __name__ == "__main__":
  fps, img_path, out_path, blend_steps, video_name, max_images, verbose=main()

os.makedirs(out_path, exist_ok=True)

# delete_content(out_path, verbose)

os.chdir(img_path)

image_list = get_image_list(img_path, verbose)

video_name = os.path.join(out_path, video_name)
if os.path.isfile(video_name):
  sys.stdout.write("file \"" + video_name + "\" does exists. Overwrite? [y/n]")
  choice = input().lower()
  if choice=="y":
    os.remove(video_name)
  else:
    exit()
  

if verbose:
  print("img path: " + img_path)
  print("out path: " + out_path)
  print("video name: " + video_name)
  print("fps: " + str(fps))
  print("blend steps: " + str(blend_steps))
  print("max images: " + str(max_images))
  
# todo: check all image sizes and resize them
#img = Image.open(image_list[0]);
#width, height = img.size

mean_width, mean_height, all_equal_flag = get_mean_size(image_list, img_path, verbose)

fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
video = cv2.VideoWriter(video_name, fourcc, fps, (mean_width, mean_height))

num=len(image_list)
if verbose:
  print("Number of images: " + str(num))
  if blend_steps > 0:
    print("Create video including blending:")
  else:
    print("Create video:")

if max_images > 0:
  if num > max_images:
    num=max_images
if blend_steps > 0:
  num-=1 # -1 because k+1 is used in loop
for k in range(num):
  offset=k*(blend_steps+1)
  if blend_steps<=0:
    img1 = Image.open(image_list[k])
    if not all_equal_flag:
      img1 = img1.resize((mean_width, mean_height))
    frame = np.array(img1)
    frame = frame[:, :, ::-1].copy()
    video.write(frame)
  else:
    img1 = Image.open(image_list[k])
    img2 = Image.open(image_list[k+1])
    if not all_equal_flag:
      img1 = img1.resize((mean_width, mean_height))
      img2 = img2.resize((mean_width, mean_height))
    for i in range(blend_steps+1):
      output_img = Image.blend(img1, img2, float(i)/blend_steps)
      # save image for debug purposes:
      # output_img.save(tmp_path + "/output" + "{:04}".format(i+offset) + ".jpg")
      frame = np.array(output_img)
      frame = frame[:, :, ::-1].copy()
      video.write(frame)
  progress_bar(k, num, "create video:  ")

if blend_steps > 0:
  # add very last image when blend mode is used
  img1 = Image.open(image_list[num]) # when blending is used: num = len()-1
  if not all_equal_flag:
    img1 = img1.resize((mean_width, mean_height))
  frame = np.array(img1)
  frame = frame[:, :, ::-1].copy()
  video.write(frame)
sys.stdout.write("\n")

cv2.destroyAllWindows()
video.release()

if verbose:
  print("finished")
