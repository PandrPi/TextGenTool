import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from scipy import stats
from scipy.optimize import curve_fit

from generation_models.general_model import GenModel


# !!! IMPORTANT !!!
# atan(m) - angle of slope in radians, where m - slope


def nonlin_curve_func(values, a, b):
    return a * values ** b


def get_nonlinear_fit_quality(x, y, popt) -> float:
    residuals = y - nonlin_curve_func(x, *popt)
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return 1.0 - (ss_res / ss_tot)


def draw_regression_curves(ax, x, y, use_nonlinear_regression=True):
    print('\t', end='')
    if use_nonlinear_regression:
        regression, pcov1 = curve_fit(nonlin_curve_func, x, y, p0=(0.5, 1.0), method='lm', maxfev=20000)
        a, b = regression
        fit_quality = abs(round(get_nonlinear_fit_quality(x, y, regression) * 100, 4))
        ax.plot(x, nonlin_curve_func(x, a, b), c='#ff9113',
                label="y=$\mathregular{{{0}*x^{{{1}}}}}$, R={2}%".format(round(a, 2), round(b, 2), fit_quality))
        print("S_NLF {0}, R_NLF {1}, ".format(round(b, 3), fit_quality), end='')

    x_log = np.log10(x)
    regression = stats.linregress(x_log, np.log10(y))
    a, b = regression.slope, regression.intercept
    fit_quality = abs(round(regression.rvalue * 100, 4))
    ax.plot(x, np.power(10, a * x_log + b), c='#57b812',
            label="y={0}*x+{1}, R={2}%".format(round(a, 2), round(b, 2), fit_quality))
    print("S_LF {0}, R_LF {1}".format(round(a, 3), fit_quality))


def basic_plot_draw(fig: Figure, ax: Axes, plot_data: dict, x_label: str, y_label: str, scatter_label: str,
                    plot_title: str, use_nonlinear_regression: bool = True, show_plot: bool = True):
    """
    Draws the data inside the plot

    :param ax: Figure to use
    :param fig: Axis to use
    :param plot_data: A dictionary that contains X and Y data
    :param x_label: Label for x axis
    :param y_label: Label for y axis
    :param scatter_label: label of scatter plot inside the Legends
    :param plot_title: Plot title
    :param use_nonlinear_regression: Will nonlinear fitting curve be presented on plot
    :param show_plot: Will the plot window be shown
    """

    x = plot_data['x']
    y = plot_data['y']

    print('{0} regression data:'.format(plot_title))
    draw_regression_curves(ax, x, y, use_nonlinear_regression)

    # smooth = gaussian_filter1d(y, 70)
    # ax.plot(x, smooth, label='smooth')
    # # compute second derivative
    # smooth_d2 = np.gradient(np.gradient(smooth))
    # ax.plot(x, smooth_d2 / np.max(smooth_d2), label='smooth d2')
    # # find switching points
    # inflection_points = np.where(np.diff(np.sign(smooth_d2)))[0]
    # for i, infl in enumerate(inflection_points, 1):
    #     plt.axvline(x=x[infl], color='k', label=f'Inflection Point {i}')

    ax.scatter(x, y, marker='s', s=14, label=scatter_label)
    ax.tick_params(labelbottom=True, labeltop=True, labelleft=True, labelright=True,
                   bottom=True, top=True, left=True, right=True, which='both')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend(prop={'size': 9.5})
    ax.set_title(plot_title)

    if show_plot:
        fig.canvas.mpl_connect('resize_event', lambda event: (fig.tight_layout(), fig.canvas.draw()))
        fig.canvas.manager.set_window_title('Plot window')
        fig.tight_layout()
        print()

        plt.show()


def get_plot_label_from_parameters(model: GenModel, external_filename: str) -> str:
    if external_filename != '':
        return external_filename
    else:
        label = ''
        for k, v in model.get_params_for_plot().items():
            label += f"{k}={v} "
        return label[:-1]


def draw_zipf_law(data: dict, model: GenModel, external_filename: str):
    """
    Calculates and draws the correlation of word's rank to a word occurrence frequency (Zipf's law)

    :param data: A dictionary that contains data about word occurrence frequencies
    :param model: The model which was used to generate the text
    :param external_filename: A name of text file which was used to calculate plot data
    """

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()

    label = get_plot_label_from_parameters(model, external_filename)  # the label of resulting plot in Legends

    basic_plot_draw(fig, ax, data, 'Rank', 'Frequency', label, "Zipf's law", use_nonlinear_regression=False)


def draw_heaps_law(data: dict, model: GenModel, external_filename: str):
    """
    Calculates and draws the correlation of total words number to a number of unique words (Heaps' law)

    :param data: A dictionary that contains data about the growth of the number of unique words in the text
    :param model: The model which was used to generate the text
    :param external_filename: A name of text file which was used to calculate plot data
    """

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()

    label = get_plot_label_from_parameters(model, external_filename)  # the label of resulting plot in Legends

    basic_plot_draw(fig, ax, data, 'Total number of words', 'Number of unique words', label, "Heaps' law")


def draw_taylor_law(data: dict, model: GenModel, external_filename: str):
    """
    Calculates and draws the correlation of average unique words number to a mean square deviation of this number
    (Taylor's law)

    :param data: A dictionary that contains data about the correlation of average unique words number to a mean square
     deviation of this number
    :param model: The model which was used to generate the text
    :param external_filename: A name of text file which was used to calculate plot data
    """

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()

    label = get_plot_label_from_parameters(model, external_filename)  # the label of resulting plot in Legends

    basic_plot_draw(fig, ax, data, 'Vocabulary size', 'σ(Vocabulary size)', label, "Taylor's law")


def draw_fluctuation_scaling(data: dict, model: GenModel, external_filename: str):
    """
    Calculates and draws the correlation of window size to a mean square deviation of Vocabulary
    (Fluctuation scaling)

    :param data: A dictionary that contains data about the correlation of average unique words number to a mean square
     deviation of this number
    :param model: The model which was used to generate the text
    :param external_filename: A name of text file which was used to calculate plot data
    """

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()

    label = get_plot_label_from_parameters(model, external_filename)  # the label of resulting plot in Legends

    basic_plot_draw(fig, ax, data, 'Window size', 'σ(Vocabulary size)', label, "Fluctuation scaling")


def draw_all_laws(data: dict, model: GenModel, external_filename: str):
    """
    Draws the plots of three laws inside a single window

    :param data: A dictionary that contains data about the correlation of average unique words number to a mean square
     deviation of this number
    :param model: The model which was used to generate the text
    :param external_filename: A name of text file which was used to calculate plot data
    """

    label = get_plot_label_from_parameters(model, external_filename)  # the label of resulting plot in Legends
    law_params = [
        [data['zipf'], 'Rank', 'Frequency', label, "Zipf's law", False, False],
        [data['heaps'], 'Total number of words', 'Number of unique words', label, "Heaps' law", True, False],
        [data['taylor'], 'Vocabulary size', 'σ(Vocabulary size)', label, "Taylor's law", True, False],
        [data['fluctuation'], 'Window size', 'σ(Vocabulary size)', label, "Fluctuation scaling", True, False],
    ]

    fig: Figure = plt.figure()
    gs = gridspec.GridSpec(2, 2)
    axes = [gs[0, 0], gs[0, 1], gs[1, 0], gs[1, 1]]

    for i in range(len(law_params)):
        ax = fig.add_subplot(axes[i])
        basic_plot_draw(fig, ax, *law_params[i])

    fig.canvas.mpl_connect('resize_event', lambda event: (fig.tight_layout(), fig.canvas.draw()))
    fig.canvas.manager.set_window_title('Plot window')
    fig.tight_layout()
    print()

    plt.show()
