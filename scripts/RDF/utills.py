from typing import List, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray

import matplotlib.pyplot as plt
from mpl_toolkits import axes_grid1
# import matplotlib.colors as mcolors

import re


def read_text(file):
    """read file"""
    with open(file, "r") as f:
        conllu = f.read()
    return conllu


def extract_property_ids(conllu: str) -> List[str]:
    """Extract Wikidata properties ID from the CoNLL-U formatted file.

    Args:
    - conllu (str): A string containing CoNLL-U formatted data for one or
    more sentences.

    Returns:
        - A list of property ids extracted from the CoNLL-U formatted file.
    """

    # Extract sentence IDs and text from the CoNLL-U formatted file.
    sent_id_regx = re.compile(r"(?<=# sent_id = )\w+")
    sent_ids = sent_id_regx.findall(conllu)

    return sent_ids


def extract_property_labels(conllu: str) -> List[str]:
    text_regex = re.compile(r"(?<=# text = ).+")
    return text_regex.findall(conllu)


# Get property lists from Conllu
def get_prop_ids(conllu_path: str) -> List[str]:
    conllu_text = read_text(conllu_path)
    return extract_property_ids(conllu_text)


def get_prop_info(conllu_path: str) -> List[str]:
    conllu_text = read_text(conllu_path)
    prop_ids = get_prop_ids(conllu_path)
    prop_labels = extract_property_labels(conllu_text)

    return {id: label for id, label in zip(prop_ids, prop_labels)}


def adjust_lightness(color, amount=1.5):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:  # noqa: E722
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])


def add_axis(ax, aspect=20, pad_fraction=0.5, **kwargs):
    """Add a vertical axis to an image plot."""
    """ref. https://stackoverflow.com/a/33505522"""
    # when I add colorbar size to the attention visualization image, the hight
    # of the color bar does not match the graph. Also, the width of color bar
    # and spacing between color bar and image changes. see:
    # https://matplotlib.org/2.0.2/mpl_toolkits/axes_grid/users/overview.html
    divider = axes_grid1.make_axes_locatable(ax)
    width = axes_grid1.axes_size.AxesY(ax, aspect=1. / aspect)
    pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
    cax = divider.append_axes("right", size=width, pad=pad)
    return cax


def plot_hist(data: List[NDArray],
              fig_data: dict,
              bins: Optional[Union[List[List[float]], List[int]]] = None,
              norm_pdf: bool = False,
              count: bool = False) -> Tuple[plt.Figure, plt.Axes]:

    # print histograms with normal distribution if required
    if "figsize_factor" in fig_data:
        wf, hf = fig_data["figsize_factor"]
    else:
        wf, hf = (1.2, 1.3)

    fig_w, fig_h = plt.rcParamsDefault["figure.figsize"]
    figsize = (fig_w * wf * len(data), fig_h * hf)
    figs, axes = plt.subplots(nrows=1,
                              ncols=len(data),
                              figsize=figsize,
                              squeeze=False)
    axes_ = np.array(axes).reshape(-1)

    # get color cycles
    hist_colors = plt.get_cmap("Accent")
    line_colors = plt.get_cmap("tab10")
    text_colors = plt.get_cmap("Set1")
    # plot histogram for each data
    for i, (ax, d) in enumerate(zip(axes_, data)):
        lbl = None if "label_h" not in fig_data else fig_data["label_h"][i]
        if bins is None:
            bins = [30] * len(data)
        density, _bins, _ = ax.hist(d,
                                    bins=bins[i],
                                    density=True,
                                    alpha=0.5,
                                    color=hist_colors(i),
                                    ec=adjust_lightness(hist_colors(i)),
                                    label=lbl)

        _ = ax.set_xticks(_bins)
        _ = ax.set_xticklabels([str(round(float(b), 5)) for b in _bins],
                               rotation=90)

        # show counts on hist
        if count:
            counts, _ = np.histogram(d, _bins)
            Xs = [(e + s) / 2 for s, e in zip(_bins[:-1], _bins[1:])]
            for x, y, count in zip(Xs, density, counts):
                _ = ax.text(x,
                            y * 1.02,
                            count,
                            horizontalalignment="center",
                            rotation=45,
                            color=text_colors(i))

        # plot normal probability dist
        if norm_pdf:
            # calc normal distribution of bleu4
            d_sorted = np.sort(d)
            mu = np.mean(d)
            sig = np.std(d)
            data_norm_pdf = 1. / (np.sqrt(2. * np.pi) * sig) * np.exp(
                -np.power((d_sorted - mu) / sig, 2.) / 2)

            _ = ax.plot(d_sorted,
                        data_norm_pdf,
                        color=line_colors(i),
                        linestyle="--",
                        linewidth=2,
                        label=lbl)

        _ = ax.legend()
        _ = ax.set_xlabel(fig_data["xlabel"])
        _ = ax.set_ylabel(fig_data["ylabel"])
        y_lim = ax.get_ylim()
        _ = ax.set_ylim((y_lim[0], y_lim[1] * 1.1))

    figs.suptitle(fig_data["title"])

    return figs, axes
