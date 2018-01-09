import itertools
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import axes3d

import src.Chronometer as chronometer
import src.Utils as Utils

import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

plt.style.use('fivethirtyeight')
# plt.style.use('ggplot')

Utils.os.putenv("MAGICK_MEMORY_LIMIT", "4294967296")


def get_title(info):
    return "{} {} {} - {}".format(
        Utils.prettify_name(info[Utils.NAME]),
        Utils.prettify_name(info[Utils.SURNAME]),
        info[Utils.WORD_NUMBER],
        Utils.prettify_name(info[Utils.HANDWRITING]))


class GifCreator:

    def __init__(self, dataset_name, dataframes, wordid_userid_dataframe, user_data_dataframe, word_id,
                 label=Utils.MOVEMENT_POINTS, frames=120, after_delay=1000):
        self.info = Utils.get_infos(wordid_userid_dataframe, user_data_dataframe, word_id)

        self.frames = frames
        dataframe = dataframes[label]
        self.data_word = dataframe.loc[getattr(dataframe, Utils.WORD_ID) == word_id].copy()
        self.max_time = max(self.data_word[Utils.TIME])

        self.repeat_delay = after_delay
        self.height = self.info[Utils.HEIGHT_PIXELS]
        self.width = self.info[Utils.WIDTH_PIXELS]
        self.word_id = word_id

        self.colors_cycle = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        self.color_map = {}

        Utils.mkdir(Utils.BUILD_GIFS_FOLDER_PATH(dataset_name))
        self.title = get_title(self.info)

        self.gif_path = Utils.BUILD_GIFS_PATH(dataset_name, self.info[Utils.NAME], self.info[Utils.SURNAME],
                                              self.info[Utils.WORD_NUMBER], self.info[Utils.HANDWRITING], label)

        self._generate_animation()

    @staticmethod
    def _update_plot(i, a, time_millis_per_frame):
        data = a.data_word[a.data_word['time'] <= i * time_millis_per_frame]
        for i, group in data.groupby(Utils.COMPONENT):
            if i not in a.color_map:
                a.color_map[i] = next(a.colors_cycle)['color']
            color = a.color_map[i]
            plt.scatter(group[Utils.X], group[Utils.Y], c=color, s=plt.rcParams['lines.markersize'] * 2)

    def _generate_animation(self):
        chrono = chronometer.Chrono("Generating gif for: {}...".format(self.title))
        if os.path.isfile(self.gif_path):
            chrono.end("already exixst")
            return

        time_millis_per_frame = self.max_time / (self.frames - 1)

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)

        ax.set_xticklabels([])
        ax.set_yticklabels([])

        ax.xaxis.label.set_visible(False)
        ax.yaxis.label.set_visible(False)

        plt.title(self.title)
        plt.axes().set_aspect('equal')
        plt.axes().invert_yaxis()

        ani = animation.FuncAnimation(fig, self._update_plot,
                                      fargs=(self, time_millis_per_frame,),
                                      frames=self.frames,
                                      interval=time_millis_per_frame,
                                      repeat=True,
                                      repeat_delay=self.repeat_delay,
                                      blit=False)

        ani.save(self.gif_path, writer='imagemagick')
        plt.close(fig)
        chrono.end()


class ChartCreator:

    def __init__(self, dataset_name, dataframe, wordid_userid_dataframe, user_data_dataframe, word_id, label=Utils.MOVEMENT_POINTS):
        self.info = Utils.get_infos(wordid_userid_dataframe, user_data_dataframe, word_id)
        Utils.mkdir(Utils.BUILD_PICS_FOLDER(dataset_name))

        self.dataset_name = dataset_name
        self.dataframe = dataframe
        self.word_id = word_id
        self.label = label
        self.height = self.info[Utils.HEIGHT_PIXELS]
        self.width = self.info[Utils.WIDTH_PIXELS]

        self.title = get_title(self.info)

    def plot2dataframe(self, xaxes=Utils.X, yaxes=Utils.Y):
        path = Utils.BUILD_CHART2D_PATH(self.dataset_name, self.info[Utils.NAME], self.info[Utils.SURNAME],
                                             self.info[Utils.WORD_NUMBER], self.info[Utils.HANDWRITING], self.label)
        chrono = chronometer.Chrono("Plotting 2D Chart for: {}...".format(self.title))
        if os.path.isfile(path):
            chrono.end("already exixst")
            return

        d = self.dataframe[self.label]

        ax = None
        colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        for i, component in enumerate(g for _, g in d.loc[d.word_id == self.word_id].groupby(Utils.COMPONENT)):
            ax = component[["x", "y", Utils.TIME]].plot(x=xaxes, y=yaxes, kind="scatter", c=next(colors)['color'],ax=ax if ax else None)

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)

        ax.set_xticklabels([])
        ax.set_yticklabels([])

        ax.xaxis.label.set_visible(False)
        ax.yaxis.label.set_visible(False)

        plt.title(self.title)
        plt.axes().set_aspect('equal')
        plt.axes().invert_yaxis()

        Utils.mkdir(Utils.BUILD_CHART2D_FOLDER_PATH(self.dataset_name))
        plt.savefig(path, dpi=400)
        chrono.end()

    def plot3dataframe(self, scaling_rates=range(0, 2000, 250)):
        chrono = chronometer.Chrono("Plotting 3D Charts for: {}...".format(self.title))
        d = self.dataframe[self.label]
        maxv = max(d[Utils.TIME])
        wrote_something = False
        for scaling in scaling_rates:
            path = Utils.BUILD_CHART3D_PATH(self.dataset_name, self.info[Utils.NAME], self.info[Utils.SURNAME],
                                                 self.info[Utils.WORD_NUMBER], self.info[Utils.HANDWRITING], scaling, self.label)
            if os.path.isfile(path):
                continue

            wrote_something = True


            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')


            colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
            for i, component in enumerate(g for _, g in d.loc[d.word_id == self.word_id].groupby(Utils.COMPONENT)):
                x = component[Utils.X]
                y = component[Utils.Y]
                z = component[Utils.TIME] / maxv * scaling

                ax.scatter(y, x, z, c=next(colors)['color'])


            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_zticklabels([])

            ax.xaxis.set_ticks_position('none')  # tick markers
            ax.yaxis.set_ticks_position('none')

            plt.title(self.title)

            ax.set_zlabel("\ntime", linespacing=-4)
            ax.set_xlabel("\nx", linespacing=-4)
            ax.set_ylabel("\ny", linespacing=-4)

            ChartCreator.set_axes_equal(ax)

            Utils.mkdir(Utils.BUILD_CHART3D_FOLDER_PATH(self.dataset_name))
            plt.savefig(path, dpi=400, bbox_inches='tight')
            plt.close(fig)

        if wrote_something:
            chrono.end()

        else:
            chrono.end("already exixst")



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
