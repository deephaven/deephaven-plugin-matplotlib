from io import BytesIO
from matplotlib.figure import Figure
from deephaven.plugin.object import Exporter, ObjectType
import os
import matplotlib.pyplot as plt

NAME = "matplotlib.figure.Figure"

plt.style.use([
    'dark_background',
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'styles/deephaven.mplstyle') ]
)

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
