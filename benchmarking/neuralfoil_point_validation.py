import aerosandbox as asb
import aerosandbox.numpy as np
from aerosandbox.tools.string_formatting import eng_string
from neuralfoil import get_aero_from_airfoil
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap
from tqdm import tqdm

af = asb.Airfoil(name="HALE_02", coordinates=Path(__file__).parent / "assets" / "HALE_03.dat")

alphas_xfoil = np.linspace(-5, 15, 50)
# alphas_xfoil = np.concatenate([
#     np.sinspace(-5, 2.5, reverse_spacing=True)[:-1],
#     np.sinspace(2.5, 15)
# ])
alphas_nf = np.linspace(alphas_xfoil.min(), alphas_xfoil.max(), 1000)
Re_values_to_test = [1e4, 1e5, 1e6, 1e7, 1e8]
# Re_values_to_test = [10e3, 50e3, 200e3, 500e3, 5e6, 1e8]
# Re_values_to_test = [1e4, 1e8]

import matplotlib.pyplot as plt
import aerosandbox.tools.pretty_plots as p

fig, ax = plt.subplots(figsize=(8,5))
plt.xscale('log')

# cmap = plt.get_cmap("rainbow")
cmap = LinearSegmentedColormap.from_list(
    "custom_cmap",
    colors=[
        p.adjust_lightness(c, 0.8) for c in
        ["orange", "darkseagreen", "dodgerblue"]
    ]
)

colors = cmap(np.linspace(0, 1, len(Re_values_to_test)))

transparency = 0.7

for Re, color in tqdm(zip(Re_values_to_test, colors)):

    nf_aero = get_aero_from_airfoil(
        airfoil=af,
        alpha=alphas_nf,
        Re=Re,
        model_size="xxxlarge"
    )

    plt.plot(
        nf_aero["CD"],
        nf_aero["CL"],
        "--",
        color=color, alpha=transparency
    )

    nf_aero = get_aero_from_airfoil(
        airfoil=af,
        alpha=alphas_nf,
        Re=Re,
        model_size="medium"
    )

    plt.plot(
        nf_aero["CD"],
        nf_aero["CL"],
        ":",
        color=color, alpha=transparency
    )

    xfoil_aero = asb.XFoil(
        airfoil=af,
        Re=Re,
    ).alpha(alpha=alphas_xfoil)

    plt.plot(
        xfoil_aero["CD"],
        xfoil_aero["CL"],
        color=color, alpha=transparency
    )
    # xfoil_aero = nf_aero

    plt.annotate(
        f" $Re = \\mathrm{{{eng_string(Re)}}}$",
        xy=(xfoil_aero["CD"][-1], xfoil_aero["CL"][-1]),
        color=p.adjust_lightness(color, 0.8),
        ha="left", va="center", fontsize=10
    )

plt.annotate(
    text="Note the log-scale on $C_D$, which is unconventional - it's\nthe only way to keep it readable given the wide range.",
    xy=(0.01, 0.01),
    xycoords="figure fraction",
    ha="left",
    va="bottom",
    fontsize=8,
    alpha=0.7
)

# Format log ticks
from matplotlib import ticker

ax.tick_params(which="minor", labelsize=8)

p.set_ticks(None, None, 0.5, 0.1)
ax.xaxis.set_major_locator(ticker.LogLocator())
ax.xaxis.set_minor_locator(ticker.LogLocator(subs=np.arange(1, 10)))

def fmt(x, pos):
    coefficient = x / 10 ** np.floor(np.log10(x))
    if any([np.allclose(coefficient, i) for i in [1, 2, 5]]):
        return f"{x:.2g}"
    else:
        return f""

ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt))
ax.xaxis.set_minor_formatter(ticker.FuncFormatter(fmt))

from matplotlib.patches import Patch
from matplotlib.lines import Line2D

plt.legend(
    handles=[
        Line2D([], [], color="k", label="XFoil"),
        Line2D([], [], color="k", linestyle="--", label="NeuralFoil \"xxxlarge\""),
        Line2D([], [], color="k", linestyle=":", label="NeuralFoil \"medium\""),
    ],
    title="Analysis Method", loc="lower left", ncols=3, fontsize=10,
    labelspacing=0.3, columnspacing=1.5, handletextpad=0.4,
    framealpha=0.5,
)

plt.xlim()
plt.ylim(bottom=-0.8)

afax = ax.inset_axes([0.76, 0.802, 0.23, 0.23])
afax.plot(
    af.x(),
    af.y(),
    "k", alpha=0.7,
    linewidth=1
)
afax.fill(
    af.x(),
    af.y(),
    "k", alpha=0.2
)
afax.annotate(
    text="HALE_03 Airfoil",
    xy=(0.5, 0.15),
    xycoords="data",
    ha="center",
    va="bottom",
    fontsize=10,
    alpha=0.7
)

afax.grid(False)
afax.set_xticks([])
afax.set_yticks([])
# afax.axis('off')
afax.set_facecolor((1, 1, 1, 0.5))
afax.set_xlim(-0.05, 1.05)
afax.set_ylim(-0.05, 0.28)
afax.set_aspect("equal", adjustable='box')


plt.suptitle("Comparison of $C_L$-$C_D$ Polar for NeuralFoil vs. XFoil", fontsize=16,y=0.94)
plt.title("On HALE_03 Airfoil (out-of-sample)", fontsize=12, alpha=0.7)

p.show_plot(
    None,
    "Drag Coefficient $C_D$",
    "Lift Coefficient $C_L$",
    legend=False,
    savefig="neuralfoil_point_validation.svg"
)
