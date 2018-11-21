'''Module for localizing particle trajectories with tensorflow tracking.'''

import numpy as np
import pandas as pd
import trackpy as tp
import cv2
from tracker import tracker
from mie_video.editing import inflate, crop
import pylab as pl
from matplotlib import animation
from matplotlib.patches import Rectangle
import lab_io.h5video as h5
import features.circletransform as ct
from time import time


def oat(frame, frame_no, feature_size=(201, 201), minmass=26.0):
    '''
    Use the orientational alignment transform
    on every pixel of an image and return features.'''
    t = time()
    circ = ct.circletransform(frame, theory='orientTrans')
    circ = circ / np.amax(circ)
    circ = h5.TagArray(circ, frame_no)
    feats = tp.locate(circ,
                      31, minmass=minmass,
                      engine='numba')
    feats['w'] = feature_size[0]
    feats['h'] = feature_size[1]
    features = np.array(feats[['x', 'y', 'w', 'h']])
    print("Time to find {} features at frame {}: {}".format(features.shape[0],
                                                            frame_no,
                                                            time() - t))
    print("Mass of particles: {}".format(list(feats['mass'])))
    return features, circ


class Animate(object):
    """Creates an animated video of particle tracking
    """

    def __init__(self, video, method='oat', transform=True,
                 dest='animation/test_mpl_anim_oat.avi', bg=None, **kwargs):
        self.frame_no = 0
        self.transform = transform
        self.video = video
        self.dest = dest
        self.fig, self.ax = pl.subplots(figsize=(8, 6))
        self.ax.set_xlabel('X [pixel]')
        self.ax.set_ylabel('Y [pixel]')
        self.cap = cv2.VideoCapture(self.video)
        self.im = None
        self.method = method
        self.rects = None
        if self.method == 'tf':
            self.trk = tracker.tracker()
        self.bg = bg

    def run(self):
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.bg is not None:
            frame = (frame.astype(float) - 13) / (self.bg - 13)
        if self.transform:
            features, frame = oat(frame, self.frame_no)
        if ret:
            self.im = self.ax.imshow(frame, interpolation='none',
                                     cmap=pl.get_cmap('gray'))
            self.anim = animation.FuncAnimation(self.fig,
                                                self.anim, init_func=self.init,
                                                blit=True, interval=50)
            self.anim.save(self.dest)
        else:
            print("Failed")

    def init(self):
        ret = False
        while not ret:
            ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.bg is not None:
            frame = (frame.astype(float) - 13) / (self.bg - 13)
        self.im.set_data(frame)
        return self.im,

    def anim(self, i):
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.bg is not None:
            frame = (frame.astype(float) - 13) / (self.bg - 13)
        self.frame_no += 1
        if ret:
            if self.method == 'tf':
                features = self.trk.predict(inflate(frame))
            elif self.method == 'oat':
                features, frame_ct = oat(frame, self.frame_no)
            else:
                raise(ValueError("method must be either \'oat\' or \'tf\'"))
            if self.rects is not None:
                for rect in self.rects:
                    rect.remove()
            self.rects = []
            for feature in features:
                x, y, w, h = feature
                rect = Rectangle(xy=(x - w/2, y - h/2),
                                 width=w, height=h,
                                 fill=False, linewidth=3, edgecolor='r')
                self.rects.append(rect)
                self.ax.add_patch(rect)
            if self.transform:
                self.im.set_array(frame_ct)
            else:
                self.im.set_array(frame)
        return self.im,


if __name__ == '__main__':
    import sys
    args = sys.argv
    anim = Animate(args[1], dest=args[2])
    anim.run()