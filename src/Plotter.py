import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation
import pandas as pd

from src.Chronometer import Chrono
from src.Constants import *
import matplotlib.pyplot as plt
import matplotlib
plt.style.use('fivethirtyeight')
# plt.style.use('ggplot')
import numpy as np
import random
import numpy.random
import itertools
import matplotlib.animation as animation
import src.Utils as Utils

import pandas




class GifCreator:

    def __init__(self, dataset_name, dataframe, wordid_userid, user_data, word_id, label=MOVEMENT_POINTS, frames=120, after_delay=1000):
        self.info = Utils.get_infos(wordid_userid, user_data, word_id)

        self.frames = frames
        dataframe = dataframe[label]
        self.data_word = dataframe.loc[getattr(dataframe, WORD_ID) == word_id].copy()
        self.max_time = max(self.data_word[TIME])

        self.repeat_delay = after_delay
        self.height = self.info[HEIGHT_PIXELS]
        self.width = self.info[WIDTH_PIXELS]
        self.word_id = word_id

        self.colors_cycle = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        self.color_map = {}

        Utils.mkdir(BUILD_PICS_FOLDER(dataset_name))
        self.gif_path = BUILD_GIFS_PATH(dataset_name, self.info[NAME], self.info[SURNAME], self.info[WORD_NUMBER], self.info[HANDWRITING])
        self._generate_animation()

    @staticmethod
    def _update_plot(i, a, time_millis_per_frame):
        data = a.data_word[a.data_word['time'] <= i * time_millis_per_frame]
        for i, group in data.groupby(COMPONENT):
            if i not in a.color_map:
                a.color_map[i] = next(a.colors_cycle)['color']
            color = a.color_map[i]
            plt.scatter(group[X], group[Y], c=color, s=plt.rcParams['lines.markersize']*2)

    def _generate_animation(self):
        title = "{} {} {} - {}".format(
            Utils.prettify_name(self.info[NAME]),
            Utils.prettify_name(self.info[SURNAME]),
            self.info[WORD_NUMBER],
            Utils.prettify_name(self.info[HANDWRITING]))
        chrono = Chrono("Generating gif for: {}...".format(title))
        time_millis_per_frame = self.max_time / (self.frames-1)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title(title)

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.invert_yaxis()

        ani = animation.FuncAnimation(fig, self._update_plot,
                                      fargs=(self, time_millis_per_frame,),
                                      frames=self.frames,
                                      interval=time_millis_per_frame,
                                      repeat=True,
                                      repeat_delay=self.repeat_delay,
                                      blit=False)

        ani.save(self.gif_path, writer='imagemagick')
        chrono.end()


class Plotter:

    @staticmethod
    def plot2dataframe(dataframe, label, wordid):
        d = dataframe[label]
        plt.interactive(False)

        ax = None
        colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        for i, component in enumerate(g for _, g in d.loc[d.word_id == wordid].groupby(COMPONENT)):
            ax = component[["x", "y", TIME]].plot(x="x", y="y", kind="scatter", c=next(colors)['color'],
                                                  ax=ax if ax else None)

        plt.axes().set_aspect('equal', 'datalim')
        plt.axes().invert_yaxis()
        plt.show()

    @staticmethod
    def set_axes_equal(ax):
        '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
        cubes as cubes, etc..  This is one possible solution to Matplotlib's
        ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

        Input
          ax: a matplotlib axis, e.g., as output from plt.gca().
        '''

        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        # The plot bounding box is a sphere in the sense of the infinity
        # norm, hence I call half the max range the plot radius.
        plot_radius = 0.5 * max([x_range, y_range, z_range])

        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

    @staticmethod
    def plot3dataframe(dataframe, label, wordid, scaling):
        d = dataframe[label].copy()

        plt.interactive(False)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        for i, component in enumerate(g for _, g in d.loc[d.word_id == wordid].groupby(COMPONENT)):
            x = component[X]
            y = component[Y] * -1
            z = component[TIME] / max(component[TIME]) * scaling

            ax.scatter(y, x, z, c=next(colors)['color'])

        # for i, component in enumerate(g for _, g in d.loc[d.word_id==wordid].groupby(COMPONENT)):
        #
        #     x = component[X]
        #     y = component[Y] * -1
        #     z = component[TIME] / max(component[TIME]) * scaling
        #
        #     ax.scatter(z, y, x,  c=next(colors)['color'])

        # plt.axes().invert_yaxis()
        ax.set_xlabel("x label")
        ax.set_ylabel("y label")
        ax.set_zlabel("z label")
        Plotter.set_axes_equal(ax)
        plt.show()