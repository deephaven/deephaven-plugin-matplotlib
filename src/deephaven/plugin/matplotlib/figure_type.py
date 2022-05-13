from io import BytesIO
from weakref import WeakKeyDictionary
from matplotlib.figure import Figure
from deephaven.plugin.object import Exporter, ObjectType
from threading import Timer


# Name of the matplotlib figure object that was export
NAME = "matplotlib.figure.Figure"

# DPI for the figure
DPI = 144

# Dictionary to store the input tables created for each figure
figure_tables = WeakKeyDictionary()

def debounce(wait):
    """Postpone a functions execution until after some time has elapsed

    :type wait: int
    :param wait: The amount of Seconds to wait before the next call can execute.
    """
    def decorator(fun):
        def debounced(*args, **kwargs):
            def call_it():
                fun(*args, **kwargs)

            try:
                debounced.t.cancel()
            except AttributeError:
                pass

            debounced.t = Timer(wait, call_it)
            debounced.t.start()

        return debounced

    return decorator

# Creates an input table that will update a figures size when the input is set
# Has three different key value pairs:
# revision: Increases whenever the figure 'ticks'
# width: The width of panel displaying the figure
# height: The height of the panel displaying the figure
def make_input_table(figure):
    from deephaven import new_table
    from deephaven.column import string_col, int_col
    import jpy
    from deephaven.table_listener import _do_locked

    # We need to get the liveness scope so we can run table operations
    LivenessScope = jpy.get_type('io.deephaven.engine.liveness.LivenessScope')
    LivenessScopeStack = jpy.get_type('io.deephaven.engine.liveness.LivenessScopeStack')
    liveness_scope = LivenessScope(True)
    LivenessScopeStack.push(liveness_scope)

    input_table = None

    def init_table():
        nonlocal input_table
        revision = 0
        t = new_table([
            string_col("key", ["revision", "width", "height"]),
            int_col("value", [revision, 640, 480])
        ])
        input_table = jpy.get_type('io.deephaven.engine.table.impl.util.KeyedArrayBackedMutableTable').make(t.j_table, 'key')

        # TODO: Add listener to input table to update figure width/height

        @debounce(0.2)
        def handle_figure_update(self, value):
            if not value:
                # value is True if it's stale, false otherwise
                # Only send a revision update if it's true
                print("handle_figure_update was not stale")
                return
            nonlocal revision
            revision = revision + 1
            # print("handle_figure_update " + str(value) + " self " + str(self) + " fig.stale=" + str(self.stale) + " revision " + str(revision) + " table " + str(input_table))
            input_table.getAttribute("InputTable").add(new_table([string_col('key', ['revision']), int_col('value', [revision])]).j_table)
            # print("revision updated")
            self.stale = False
            # print("No longer stale" + str(self.stale))

        figure.stale_callback = handle_figure_update

    _do_locked(init_table)

    LivenessScopeStack.pop(liveness_scope)

    return input_table, liveness_scope

def get_input_table(figure):
    if not figure in figure_tables:
        figure_tables[figure] = make_input_table(figure)
    return figure_tables[figure]

class FigureType(ObjectType):
    @property
    def name(self) -> str:
        return NAME

    def is_type(self, object) -> bool:
        return isinstance(object, Figure)

    def to_bytes(self, exporter: Exporter, figure: Figure) -> bytes:
        input_table, liveness_scope = get_input_table(figure)
        exporter.reference(input_table)
        exporter.reference(liveness_scope)
        buf = BytesIO()
        figure.savefig(buf, format='PNG', dpi=DPI)

        # Eliminate the staleness by drawing the figure
        figure.canvas.draw_idle()
        return buf.getvalue()
