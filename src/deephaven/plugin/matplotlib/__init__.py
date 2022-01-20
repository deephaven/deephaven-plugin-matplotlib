from deephaven.plugin import Registration
from importlib import resources
import matplotlib.pyplot as plt

__version__ = "0.0.1.dev5"

class MatplotlibRegistration(Registration):
    @classmethod
    def register_into(cls, callback: Registration.Callback) -> None:
        # Need to set the Deephaven style here. When using savefig to export the figure, it reads from the global state instead of temporary style sheets
        with resources.path(__package__, 'deephaven.mplstyle') as p:
            plt.style.use(['dark_background',p])
        from . import figure_type
        callback.register(figure_type.FigureType)
