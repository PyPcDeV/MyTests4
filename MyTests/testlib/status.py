from math import log2

WRITER = 1 << 0
WRITER_FREE = 1 << 1
WRITER_KILL = 1 << 2
READER = 1 << 3
READER_FREE = 1 << 4
READER_KILL = 1 << 5
CATCHER = 1 << 6
CATCHER_FREE = 1 << 7
CATCHER_KILL = 1 << 8
LIMITER = 1 << 9
LIMITER_FREE = 1 << 10
LIMITER_KILL = 1 << 11
KILLER = 1 << 12
KILLER_FREE = 1 < 13
KILLER_KILL = 1 << 14
TIME_LIMIT = 1 << 15


class Status:
    def __init__(self):
        self.status = 0

    def get(self, mask: int) -> bool:
        return bool(self.status >> int(log2(mask)) & 1)
    
    def on(self, mask: int):
        if not self.get(mask):
            self.status ^= mask
        
    def off(self, mask: int):
        if self.get(mask):
            self.status ^= mask
