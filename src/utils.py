from enum import Enum
from typing import Dict

# data = {} # key = UUID tag, value = DataSource
# plots = {} # key = UUID tag, value = PlotInstance


# put into utils
WINDOW_TITLE = "TIMESINK"
# VIEWPORT_HEIGHT = 1080
# VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 700
VIEWPORT_WIDTH = 1200
WINDOW_PADDING = 8
MENU_BAR_HEIGHT : int = 18
SIDEBAR_WIDTH = 150
OPTIONS_HEIGHT = 200
TAB_BAR_HEIGHT = 60 # TODO: tune this up a bit
MAX_PLOTS_ON_SCREEN = 4
NUM_PLOTS_ON_STARTUP = 2



class DragItemType(Enum):
    DATA = 1
    ANNOTATION = 2
    TRIM_WINDOW = 3




class Sources:
    def __init__(self) -> None:
        self._items: Dict[int,'DataInstance'] = {} # key = UUID tag, value = DataSource

    @property
    def tags(self) -> set[int]:
        return set(self._items.keys())

    def add(self, ds: 'DataInstance') -> None:
        self._items[ds.self_tag] = ds

    def get(self, instance_tag: int) -> 'DataInstance | None':
        return self._items.get(instance_tag, None)

    def delete(self, ds: 'DataInstance') -> None:
        ds.delete()
        self._items.pop(ds.self_tag, None)

class Plots:
    def __init__(self) -> None:
        self._items: Dict[int,'PlotInstance'] = {}  # key = UUID tag, value = PlotInstance

    @property
    def count(self) -> int:
        return len(self._items)

    @property
    def tags(self) -> set[int]:
        return set(self._items.keys())

    def add(self, pi: 'PlotInstance') -> None:
        self._items[pi.self_tag] = pi

    def get(self, instance_tag: int) -> 'PlotInstance | None':
        return self._items.get(instance_tag, None)

    def delete(self, pi: 'PlotInstance') -> None:
        pi.delete()
        self._items.pop(pi.self_tag, None)

# instantiate "singletons"
sources = Sources()
plots = Plots()