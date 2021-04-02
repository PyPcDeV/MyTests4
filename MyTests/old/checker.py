import testlib
from random import randint
from time import time
import logging

logging.basicConfig(filename="logs.log", filemode="a", level=logging.DEBUG, format="%(asctime)s - %(message)s")

FILE_NAME = "test.py"
LANG = "py"

process = testlib.Process(FILE_NAME, LANG)
process.set_time_limit(10)
process.start()

n = randint(1, int(1e5))
logging.info("Generated test n=%s" % n)
res = 0
process.write_line(str(n))
for x in range(n):
    a = randint(1, int(1e2))
    process.write_line(str(a))
    res += a
process.end_write()
process.wait()
ans = int(process.lines[0])

if ans == res:
    logging.info("OK. expected res %s got ans %s" % (res, ans))
else:
    logging.info("WRONG. expected res %s got ans %s" % (res, ans))

logging.info("Elapsed %ss, %s%s of %ss TL" % (round(process.get_elapsed(time()), 2),
                                              round(process.get_elapsed(time()) / process.time_limit * 100, 2), "%",
                                              process.time_limit))
