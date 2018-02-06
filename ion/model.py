from collections import namedtuple

from .utils import Marshalled, require
from .crypto import keccak_256


_BlockStruct= namedtuple('Block', ('prev', 'root'))


class Block(_BlockStruct, Marshalled):
    def __init__(self, *args, **kwa):
        _BlockStruct.__init__(*args, **kwa)

    @property
    def hash(self):
        require( len(self.prev) == 32 )
        require( len(self.root) == 32 )
        return keccak_256(self.prev + self.root).digest()