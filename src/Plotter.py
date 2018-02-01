import itertools
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.mplot3d import axes3d

import src.Chronometer as chronometer
import src.Utils as Utils

import warnings
import matplotlib.cbook

warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)


# plt.style.use('ggplot')

Utils.os.putenv("MAGICK_MEMORY_LIMIT", "4294967296")

IDENTIFICATION = "Identification"
VERIFICATION = "Verification"

import matplotlib as mpl


def set_white_chart():
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.style.use('fivethirtyeight')

    mpl.rcParams["figure.facecolor"] = 'white'
    mpl.rcParams["axes.facecolor"] = 'white'
    mpl.rcParams["axes.edgecolor"] = 'white'
    mpl.rcParams["savefig.facecolor"] = 'white'

    mpl.rcParams["xtick.color"] = 'white'
    mpl.rcParams["ytick.color"] = 'white'


def set_fivethirtyeight_style():
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.style.use('fivethirtyeight')

    mpl.rcParams["figure.facecolor"] = 'white'
    mpl.rcParams["axes.facecolor"] = 'white'
    mpl.rcParams["axes.edgecolor"] = 'white'
    mpl.rcParams["savefig.facecolor"] = 'white'


def set_ggplot_style():
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.style.use('ggplot')


def get_title(info):
    return "{} {} {} - {}".format(
        Utils.prettify_name(info[Utils.NAME]),
        Utils.prettify_name(info[Utils.SURNAME]),
        info[Utils.WORD_NUMBER],
        Utils.prettify_name(info[Utils.HANDWRITING]))


def get_word_data(dataframe, wordid_userid, user_data, wordid, name, surname, handwriting, wordnumber):
    assert bool(wordid) != bool(
        name and surname and handwriting and wordnumber), "Need a wordid xor a (name, surname, handwriting, word number"
    if not wordid:
        wordid = Utils.get_wordidfrom_wordnumber_name_surname(wordid_userid, user_data, name, surname, handwriting,
                                                              wordnumber)
    return dataframe.loc[dataframe[Utils.WORD_ID] == wordid], wordid

class Plotter:
    def __init__(self, dataset_name):
        self.dataset_name=dataset_name
        self.results_folder = Utils.BUILD_RESULTS_FOLDER(dataset_name)

    def _get_path_hand(self, modality, handwriting):
        path = Utils.BUILD_RESULTS_HAND_FOLDER(self.results_folder, modality, handwriting)
        Utils.mkdir(path)
        return path

    def get_desc(self, desc, balanced):
        return  "{}_{}".format("balanced" if balanced else "notbalanced", desc)

    def simplePlot(self, path, xaxes, yaxes, colors, labels, lws, linestyles, xlabel, ylabel, title, xlow=-0.005, ylow=-0.005, xhigh=1, yhigh=1.01, legendpos="lower right", yscale=True, xscale=True, integer_x=False):
        assert len(xaxes) == len(yaxes)
        assert not colors or len(colors) == len(xaxes), "{}, {}".format(len(colors), len(xaxes))
        assert not labels or len(labels) == len(xaxes)
        assert not lws or len(lws) == len(xaxes)
        assert not linestyles or len(linestyles) == len(xaxes), "{}, {}".format(len(linestyles), len(xaxes))

        set_ggplot_style()

        fig = plt.figure()

        for i, (x, y) in enumerate(zip(xaxes, yaxes)):
            plt.plot(x, y,
                     color=colors[i] if colors else None,
                     lw=lws[i] if lws else None,
                     label=labels[i] if labels else None,
                     linestyle=linestyles[i] if linestyles else None)
        if xscale:
            plt.xlim([xlow, xhigh])
        if yscale:
            plt.ylim([ylow, yhigh])
        if integer_x:
            plt.axes().xaxis.set_major_locator(MaxNLocator(integer=True))

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend(loc=legendpos)
        plt.savefig(path, dpi=400)
        # plt.show()
        plt.close(fig)

    def plotRoc(self, svm_name, fpr, tpr, auc_score, handwriting, balanced):
        xaxes = [fpr] + [[0,1]]
        yaxes = [tpr] + [[0,1]]
        colors = ['darkorange', 'navy']
        labels = ["{} (area = {:.4f})".format(svm_name, auc_score), None]
        linestyles = [None, "--"]

        self.simplePlot(Utils.BUILD_RESULTS_PATH(self._get_path_hand(VERIFICATION, handwriting), handwriting, svm_name, self.get_desc("roc", balanced)),
            xaxes, yaxes, colors, labels, None, linestyles, "False Positive Rate", "True Positive Rate", "Receiver Operating Characteristic - {}".format(Utils.prettify_name(handwriting)))

    def plotRocs(self, svm_name, fpr, tpr, auc_score, handwriting, balanced):
        assert isinstance(svm_name, list)
        assert isinstance(auc_score, list)
        xaxes = fpr + [[0, 1]]
        yaxes = tpr + [[0, 1]]
        colors = [None for _ in svm_name] + ["navy"]
        labels = ["{} (area = {:.4f})".format(svm_name, auc_score) for svm_name, auc_score in zip(svm_name, auc_score)] + [None]
        linestyles = [None for _ in svm_name] + ["--"]
        self.simplePlot(Utils.BUILD_RESULTS_PATH(self._get_path_hand(VERIFICATION, handwriting), handwriting, "_".join(svm_name),  self.get_desc("roc", balanced)),
            xaxes, yaxes, colors, labels, None, linestyles, "False Positive Rate", "True Positive Rate", "Receiver Operating Characteristic - {}".format(Utils.prettify_name(handwriting)))


    def plotFRRvsFPR(self, svm_name, thresholds, frr, fpr, handwriting, balanced):
        xaxes = [thresholds, thresholds]
        yaxes = [frr, fpr]
        colors = ['darkorange', 'navy']
        lws = [2, 2]
        labels = ["FRR - {}".format(svm_name), "FPR - {}".format(svm_name)]
        self.simplePlot(Utils.BUILD_RESULTS_PATH(self._get_path_hand(VERIFICATION, handwriting), handwriting, svm_name,  self.get_desc("frrVSfpr", balanced)),
            xaxes, yaxes, colors, labels, lws, None, "Thresholds", "Errors Rate", "FRR vs FPR - {}".format(Utils.prettify_name(handwriting)), legendpos="upper center")



    def plotCMCs(self, svm_name, rank, cmcvalues, handwriting):
        assert isinstance(svm_name, list)
        labels = ["{} (rr = {:.4f})".format(s, r[1]) for s, r in zip(svm_name, cmcvalues)]
        self.simplePlot(Utils.BUILD_RESULTS_PATH(self._get_path_hand(IDENTIFICATION, handwriting), handwriting, "_".join(svm_name), "cmc"),
            rank, cmcvalues, None, labels, None, None, "Rank", "Cms Values", "Cumulative Match Curve - {}".format(Utils.prettify_name(handwriting)),
                        xscale=False,
                        yscale=False,
                        integer_x=True)

    def plotCMC(self, svm_name, rank, cmc_values, handwriting):
        xaxes = [rank]
        yaxes = [cmc_values]
        colors = ['darkorange']
        labels = ["{} (rr = {:.4f})".format(svm_name, cmc_values[1])]
        self.simplePlot(Utils.BUILD_RESULTS_PATH(self._get_path_hand(IDENTIFICATION, handwriting), handwriting, svm_name, "cmc"),
            xaxes, yaxes, colors, labels, None, None, "Rank", "Cms Values", "Cumulative Match Curve - {}".format(handwriting.title()),
                        xscale=False,
                        yscale=False,
                        integer_x=True)

class GifCreator:

    def __init__(self, dataset_name, dataframes, wordid_userid_dataframe, user_data_dataframe, word_id=None, name=None,
                 surname=None, handwriting=None, word_number=None,
                 label=Utils.MOVEMENT_POINTS, frames=120, after_delay=1000):
        set_white_chart()
        self.word_dataframe, word_id = get_word_data(dataframes[label], wordid_userid_dataframe, user_data_dataframe, word_id,
                                            name, surname, handwriting, word_number)
        self.info = Utils.get_infos(wordid_userid_dataframe, user_data_dataframe, word_id)

        self.frames = frames
        self.max_time = max(self.word_dataframe[Utils.TIME])

        self.repeat_delay = after_delay
        self.height = self.info[Utils.HEIGHT_PIXELS]
        self.width = self.info[Utils.WIDTH_PIXELS]

        self.colors_cycle = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        self.color_map = {}

        Utils.mkdir(Utils.BUILD_GIFS_FOLDER_PATH(dataset_name))
        self.title = get_title(self.info)

        self.gif_path = Utils.BUILD_GIFS_PATH(dataset_name, self.info[Utils.NAME], self.info[Utils.SURNAME],
                                              self.info[Utils.WORD_NUMBER], self.info[Utils.HANDWRITING], label)
        self._generate_animation()

    @staticmethod
    def _update_plot(i, a, time_millis_per_frame):
        data = a.word_dataframe[a.word_dataframe['time'] <= i * time_millis_per_frame]
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

        # plt.title(self.title)
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

    def __init__(self, dataset_name, dataframe, wordid_userid_dataframe, user_data_dataframe,
                 word_id=None, name=None, surname=None, handwriting=None, word_number=None, label=Utils.MOVEMENT_POINTS):
        self.word_dataframe, word_id = get_word_data(dataframe[label], wordid_userid_dataframe, user_data_dataframe, word_id,
                                            name, surname, handwriting, word_number)
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
        set_white_chart()
        path = Utils.BUILD_CHART2D_PATH(self.dataset_name, self.info[Utils.NAME], self.info[Utils.SURNAME],
                                        self.info[Utils.WORD_NUMBER], self.info[Utils.HANDWRITING], self.label)
        chrono = chronometer.Chrono("Plotting 2D Chart for: {}...".format(self.title))
        if os.path.isfile(path):
            chrono.end("already exixst")
            return

        ax = None
        colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        for i, component in enumerate(g for _, g in self.word_dataframe.groupby(Utils.COMPONENT)):
            ax = component[["x", "y", Utils.TIME]].plot(x=xaxes, y=yaxes, kind="scatter", c=next(colors)['color'],
                                                        ax=ax if ax else None)

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)

        ax.set_xticklabels([])
        ax.set_yticklabels([])

        ax.xaxis.label.set_visible(False)
        ax.yaxis.label.set_visible(False)

        # plt.title(self.title)
        plt.axes().set_aspect('equal')
        plt.axes().invert_yaxis()

        Utils.mkdir(Utils.BUILD_CHART2D_FOLDER_PATH(self.dataset_name))
        plt.savefig(path, dpi=400)
        chrono.end()

    def plot3dataframe(self, scaling_rates=None):
        set_white_chart()
        chrono = chronometer.Chrono("Plotting 3D Charts for: {}...".format(self.title))
        maxv = max(self.word_dataframe[Utils.TIME])
        if not scaling_rates:
            scaling_rates = range(0, maxv + 1, 50)
        wrote_something = False
        for scaling in scaling_rates:
            path = Utils.BUILD_CHART3D_PATH(self.dataset_name, self.info[Utils.NAME], self.info[Utils.SURNAME],
                                            self.info[Utils.WORD_NUMBER], self.info[Utils.HANDWRITING], scaling,
                                            self.label)
            if os.path.isfile(path):
                continue

            wrote_something = True

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
            for i, component in enumerate(g for _, g in self.word_dataframe.groupby(Utils.COMPONENT)):
                x = component[Utils.X]
                y = component[Utils.Y]
                z = component[Utils.TIME] / maxv * scaling

                ax.scatter(y, x, z, c=next(colors)['color'])

            ax.w_xaxis.set_pane_color((1, 1, 1, 0))
            ax.w_yaxis.set_pane_color((1, 1, 1, 0))
            ax.w_zaxis.set_pane_color((1, 1, 1, 0))

            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_zticklabels([])


            # ax.xaxis.set_ticks_position('none')  # tick markers
            # ax.yaxis.set_ticks_position('none')


            # plt.title(self.title)
            ax.set_xlim(0, self.height)
            ax.set_ylim(0, self.width)
            ax.set_zlim(0, maxv)
            ax.set_zlabel('\ntime', linespacing=-4)

            # ChartCreator.set_axes_equal(ax)

            Utils.mkdir(Utils.BUILD_CHART3D_FOLDER_PATH(self.dataset_name, self.info[Utils.NAME], self.info[Utils.SURNAME],
                                            self.info[Utils.WORD_NUMBER], self.info[Utils.HANDWRITING], self.label ))
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
