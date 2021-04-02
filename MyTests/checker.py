import testlib
import time
from random import randint as rand

process = testlib.Process(testlib.exutables.gpp_lang("test.cpp"))
process.enable_logging("logs.log")
process.set_time_limit(300)
process.start()

n = 10000000
print("generated test\nn=%s" % n)
res = 0
process.write(n)
for x in range(n):
    if process.get_tl():
        break
    a = rand(1, int(1e9))
    process.write(a)
    res += a
    
process.free_writer()
process.wait()

if process.get_tl():
    print("TL: time limit error. done in %ss,"
          " time limit %ss. used %s%s time" % (round(process.time, 2),
                                               round(process.time_limit, 2),
                                               round(process.time / process.time_limit * 100, 2), '%'))
else:
    ans = process.read_line_as_number()
    if ans == res:
        print("OK. got %s expected %s" % (ans, res))
    else:
        print("WRONG. got %s expected %s" % (ans, res))
    print("done in %ss,"
          " time limit %ss. used %s%s time" % (round(process.time, 2),
                                               round(process.time_limit, 2),
                                               round(process.time / process.time_limit * 100, 2), '%'))
 