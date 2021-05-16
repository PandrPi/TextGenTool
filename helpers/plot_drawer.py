import matplotlib.pyplot as plt
import numpy as np
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
    if use_nonlinear_regression:
        regression, pcov1 = curve_fit(nonlin_curve_func, x, y, p0=(0.5, 1.0), method='lm', maxfev=20000)
        a, b = regression
        fit_quality = abs(round(get_nonlinear_fit_quality(x, y, regression) * 100, 4))
        ax.plot(x, nonlin_curve_func(x, a, b), c='#ff9113',
                label="y=$\mathregular{{{0}*x^{{{1}}}}}$, R={2}%".format(round(a, 2), round(b, 2), fit_quality))

    x_log = np.log10(x)
    regression = stats.linregress(x_log, np.log10(y))
    a, b = regression.slope, regression.intercept
    fit_quality = abs(round(regression.rvalue * 100, 4))
    ax.plot(x, np.power(10, a * x_log + b), c='#57b812',
            label="y={0}*x+{1}, R={2}%".format(round(a, 2), round(b, 2), fit_quality))


def basic_plot_draw(plot_data: dict, x_label: str, y_label: str, scatter_label: str, plot_title: str,
                    use_nonlinear_regression=True):
    """
    Draws the data inside the plot

    :param plot_data: A dictionary that contains X and Y data
    :param x_label: Label for x axis
    :param y_label: Label for y axis
    :param scatter_label: label of scatter plot inside the Legends
    :param plot_title: Plot title
    :param use_nonlinear_regression: Will nonlinear fitting curve be presented on plot
    """

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()

    x = plot_data['x']
    y = plot_data['y']

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

    fig.canvas.mpl_connect('resize_event', lambda event: (fig.tight_layout(), fig.canvas.draw()))
    fig.canvas.manager.set_window_title('Plot window')

    ax.legend(prop={'size': 11})
    fig.tight_layout()
    plt.title(plot_title)
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

    label = get_plot_label_from_parameters(model, external_filename)  # the label of resulting plot in Legends

    basic_plot_draw(data, 'Rank', 'Frequency', label, "Zipf's law", use_nonlinear_regression=False)


def draw_heaps_law(data: dict, model: GenModel, external_filename: str):
    """
    Calculates and draws the correlation of total words number to a number of unique words (Heaps' law)

    :param data: A dictionary that contains data about the growth of the number of unique words in the text
    :param model: The model which was used to generate the text
    :param external_filename: A name of text file which was used to calculate plot data
    """

    label = get_plot_label_from_parameters(model, external_filename)  # the label of resulting plot in Legends

    basic_plot_draw(data, 'Total number of words', 'Number of unique words', label, "Heaps' law")


def draw_taylor_law(data: dict, model: GenModel, external_filename: str):
    """
    Calculates and draws the correlation of average unique words number to a mean square deviation of this number
    (Taylor's law)

    :param data: A dictionary that contains data about the correlation of average unique words number to a mean square
     deviation of this number
    :param model: The model which was used to generate the text
    :param external_filename: A name of text file which was used to calculate plot data
    """

    label = get_plot_label_from_parameters(model, external_filename)  # the label of resulting plot in Legends

    basic_plot_draw(data, 'Vocabulary size', 'σ(Vocabulary size)', label, "Taylor's law")
