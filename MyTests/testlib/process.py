import subprocess
import threading
import logging
import time
from collections import deque
from typing import Union
from testlib import status


class Process:
    def __init__(self, cmd):
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        self.__writer_proc = threading.Thread(target=self.__writer)
        self.__reader_proc = threading.Thread(target=self.__reader)
        self.__catcher_proc = threading.Thread(target=self.__catcher)
        self.__limiter_proc = threading.Thread(target=self.__limiter)
        self.__killer_proc = threading.Thread(target=self.__killer)
        
        self.status = status.Status()
        self.time_limit = 0
        self.start_time = 0
        self.time = 0
        
        self.__input = deque()
        self.__awaiting_input = deque()
        self.__output = deque()
        
        self.__lock = threading.RLock()
        
        self.__enable_logs = False
    
    def __log_full_error(self):
        self.__error("READER %s, READER_KILL %s, READER_FREE %s" % (self.status.get(status.READER),
                                                                    self.status.get(status.READER_KILL),
                                                                    self.status.get(status.READER_FREE)))
        
        self.__error("WRITER %s, WRITER_KILL %s, WRITER_FREE %s" % (self.status.get(status.WRITER),
                                                                    self.status.get(status.WRITER_KILL),
                                                                    self.status.get(status.WRITER_FREE)))
        
        self.__error("LIMITER %s, LIMITER_KILL %s, LIMITER_FREE %s" % (self.status.get(status.LIMITER),
                                                                       self.status.get(status.LIMITER_KILL),
                                                                       self.status.get(status.LIMITER_FREE)))
        
        self.__error("CATCHER %s, CATCHER_KILL %s, CATCHER_FREE %s" % (self.status.get(status.CATCHER),
                                                                       self.status.get(status.CATCHER_KILL),
                                                                       self.status.get(status.CATCHER_FREE)))
        
        self.__error("KILLER %s, KILLER_KILL %s, KILLER_FREE %s" % (self.status.get(status.KILLER),
                                                                    self.status.get(status.KILLER_KILL),
                                                                    self.status.get(status.KILLER_FREE)))
    
    def __writer(self):
        try:
            while True:
                if self.status.get(status.WRITER_KILL):
                    self.__log("writer killed")
                    break
                if self.status.get(status.WRITER_FREE) and not len(self.__input):
                    self.status.on(status.WRITER_KILL)
                if self.__input:
                    with self.__lock:
                        self.proc.stdin.writelines(self.__input)
                        self.proc.stdin.flush()
                        self.__input.clear()
            self.status.off(status.WRITER)
            self.proc.stdin.close()
        except Exception as e:
            self.__error("writer error: %s" % e)
            self.__log_full_error()
    
    def __reader(self):
        try:
            while True:
                if self.status.get(status.READER_KILL):
                    self.__log("reader killed")
                    break
                line = self.proc.stdout.readline()
                if not line:
                    self.status.on(status.READER_KILL)
                else:
                    self.__output.append(line.decode(encoding="utf-8"))
            self.status.off(status.READER)
            self.proc.stdout.close()
        except Exception as e:
            self.__error("reader error: %s" % e)
            self.__log_full_error()
    
    def __catcher(self):
        try:
            while True:
                if self.status.get(status.CATCHER_KILL):
                    self.__log("catcher killed")
                    break
            self.status.off(status.CATCHER)
            self.proc.stderr.close()
        
        except Exception as e:
            self.__error("catcher error: %s" % e)
            self.__log_full_error()
    
    def __limiter(self):
        try:
            self.start_time = time.time()
            while True:
                if self.status.get(status.LIMITER_KILL):
                    self.__log("limiter killed")
                    break
                if time.time() - self.start_time >= self.time_limit:
                    self.__log("time limit exceed")
                    self.status.on(status.TIME_LIMIT)
                    self.status.on(status.WRITER_KILL)
                    self.status.on(status.READER_KILL)
                    self.status.on(status.CATCHER_KILL)
                    self.status.on(status.LIMITER_KILL)
                    self.status.on(status.KILLER_KILL)
            self.status.off(status.LIMITER)
        except Exception as e:
            self.__error("limiter error: %s" % e)
            self.__log_full_error()
    
    def __killer(self):
        try:
            while True:
                if not self.status.get(status.WRITER) and \
                    not self.status.get(status.READER):
                    self.status.on(status.CATCHER_KILL)
                    self.status.on(status.LIMITER_KILL)
                if not self.status.get(status.WRITER) and \
                    not self.status.get(status.READER) and \
                    not self.status.get(status.CATCHER) and \
                    not self.status.get(status.LIMITER):
                    self.proc.terminate()
                    self.__log("killed process")
                    break
                if self.status.get(status.KILLER_KILL):
                    self.__log("killer killed")
                    break
            self.status.off(status.KILLER)
        except Exception as e:
            self.__error("killer error: %s" % e)
            self.__log_full_error()
    
    def __log(self, message: str):
        if self.__enable_logs:
            logging.debug(message)
    
    def __error(self, message: str):
        if self.__enable_logs:
            logging.error(message)
    
    def start(self):
        self.__log("starting process")
        self.status.on(status.WRITER)
        self.status.on(status.READER)
        self.status.on(status.CATCHER)
        self.status.on(status.LIMITER)
        self.status.on(status.KILLER)
        
        self.__limiter_proc.start()
        self.__log("limiter started")
        self.__catcher_proc.start()
        self.__log("cather started")
        self.__writer_proc.start()
        self.__log("writer started")
        self.__reader_proc.start()
        self.__log("reader started")
        self.__killer_proc.start()
        self.__log("killer started")
    
    def enable_logging(self, file: str):
        self.__enable_logs = True
        logging.basicConfig(filename=file, filemode="w", level=logging.DEBUG,
                            format="%(levelname)s - %(asctime)s - %(message)s")
    
    def set_time_limit(self, limit: int):
        self.__log("changed time limit from %ss to %ss" % (self.time_limit, limit))
        self.time_limit = limit
    
    def write(self, data: Union[int, str]):
        with self.__lock:
            self.__input.append(bytes(str(data) + '\n', encoding="utf-8"))
    
    def free_writer(self):
        self.status.on(status.WRITER_FREE)
        self.__log("writer is currently free")
    
    def wait(self):
        while self.status.get(status.WRITER) or \
            self.status.get(status.READER) or \
            self.status.get(status.CATCHER) or \
            self.status.get(status.LIMITER):
            pass
        self.time = self.get_time()
        self.__log("done in %ss. time limit %ss. used %s%s of time" % (round(self.time, 2),
                                                                       round(self.time_limit, 2),
                                                                       round(self.time / self.time_limit * 100, 2), '%')
                   )
    
    def get_time(self) -> float:
        return time.time() - self.start_time
    
    def get_tl(self):
        return self.status.get(status.TIME_LIMIT)
    
    def read_line_as_number(self) -> int:
        return int(self.__output.popleft())
