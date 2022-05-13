from deephaven.plugin import Registration
from importlib import resources
import matplotlib.pyplot as plt

__version__ = "0.0.1.dev7"

def table_plot(table, ax, cols):
    """Plot data from a specified table to an axis"""
    # Start with empty data
    line, = ax.plot([], [])
    def on_table_update(update):
        data = []
        for col in cols:
            data.append(table.j_table.getColumn(col).getDirect())
        line.set_data(data)
        ax.relim()
        ax.autoscale_view(True, True, True)

    from deephaven.table_listener import listen
    listen(table, on_table_update)
    # Update right away
    on_table_update({})

def init_theme():
    # Set the Deephaven style globally.
    # We use the savefig function to export the Figure, and that uses the Figure's properties for colours rather than temporary styling.
    # The Figure's properties are set on creation time of the Figure, rather than when the Figure is exported
    # We do not have hooks into when a user creates a new Figure, so we set the theme globally ahead of time
    # https://github.com/matplotlib/matplotlib/issues/6592/
    with resources.path(__package__, 'deephaven.mplstyle') as p:
        plt.style.use(['dark_background',p])

class MatplotlibRegistration(Registration):
    @classmethod
    def register_into(cls, callback: Registration.Callback) -> None:
        init_theme()
        from . import figure_type
        callback.register(figure_type.FigureType)
