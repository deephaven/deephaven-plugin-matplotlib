from io import BytesIO
from matplotlib.figure import Figure
from deephaven.plugin.object import Exporter, ObjectType
from importlib import resources
import matplotlib.pyplot as plt

NAME = "matplotlib.figure.Figure"

with resources.path(__package__, 'deephaven.mplstyle') as p:
    plt.style.use(['dark_background',p])

class FigureType(ObjectType):
    @property
    def name(self) -> str:
        return NAME

    def is_type(self, object) -> bool:
        return isinstance(object, Figure)

    def to_bytes(self, exporter: Exporter, figure: Figure) -> bytes:
        buf = BytesIO()
        figure.savefig(buf, format='PNG')
        return buf.getvalue()
