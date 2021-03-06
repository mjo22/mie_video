'''Nifty module for methods involving OpenCV. Includes a method
to grab a background image from a file'''

import cv2
import numpy as np


def background(fn, shape=(480, 640)):
    '''
    Return a background image from a video file

    Args:
        fn: video filename
    Keywords:
        shape: shape of video frames
    Returns:
        bg: background image represented by np.ndarray
            of size shape
    '''
    count = count_frames(fn)
    n_frames = min(count, 200)
    frames = np.zeros((n_frames, shape[0], shape[1]),
                      dtype=np.float_)
    frame_nos = range(count)
    for idx in range(n_frames):
        frame_no = np.random.choice(frame_nos)
        cap = cv2.VideoCapture(fn)
        cap.set(1, frame_no)
        ret, rand_frame = cap.read()
        attempt = 0
        while ret is False:
            if attempt == 10:
                print("Failed to read {} at frame {}".
                      format(fn, frame_no))
                break
            ret, rand_frame = cap.read()
            attempt += 1
        if rand_frame is not None:
            frames[idx] = cv2.cvtColor(rand_frame, cv2.COLOR_BGR2GRAY)
    bg = np.median(frames, axis=0)
    return bg


def count_frames(path):
    '''Gets the number of frames in a video
    '''
    video = cv2.VideoCapture(path)
    total = 0
    version = cv2.__version__
    if version.startswith('3.') or version.startswith('4.'):
        total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    else:
        total = int(video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    return total


def inflate(image):
    '''
    Returns a RGB image from a BW image.
    '''
    shape = image.shape
    new_image = np.zeros([shape[0], shape[1], 3])
    new_image[:, :, 0] = image
    new_image[:, :, 1] = image
    new_image[:, :, 2] = image
    return new_image
