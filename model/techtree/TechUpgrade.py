from model import *
from model.techtree import Tech


class TechUpgrade(Tech):
    def __init__(self, parent, element):
        super(TechUpgrade, self).__init__(parent, element)
        self.parent = parent
        self.is_available = False
