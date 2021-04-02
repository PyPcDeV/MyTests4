from subprocess import Popen, PIPE
from threading import Thread
from time import time
from old.testlib import python_executable
import logging

logging.basicConfig(filename="logs.log", filemode="w", level=logging.DEBUG, format="%(asctime)s - %(message)s")


class Process:
    def __init__(self, file: str, lang: str):
        cmd = ""
        if lang == "py":
            cmd = python_executable(file).split()
        
        self.proc = Popen(cmd, stdin=PIPE, stdout=PIPE)
        self.lines = []
        self.kill_writer = False
        self.kill_reader = False
        self.kill_limiter = False
        self.can_kill_writer = False
        self.write_data = []
        
        self.time_limit = 0
        self.start_time = 0
        
        self._reader = Thread(target=self.reader, args=(self.proc, self.lines))
        self._writer = Thread(target=self.writer, args=(self.proc, self.write_data))
        self._limiter = Thread(target=self.limiter, args=(self.proc, []))
    
    def reader(self, proc: Popen, lines: list):
        try:
            while True and not self.kill_reader:
                line = proc.stdout.readline()
                if self.kill_writer and not line:
                    self.kill_reader = True
                    break
                if not line:
                    continue
                lines.append(line)
                logging.info("reader read output %s" % line)
            proc.stdout.close()
            logging.info("reader finished his work. kill_reader: %s" % self.kill_reader)
        except Exception as e:
            logging.error("got an error in reader: %s" % e)
    
    def writer(self, proc: Popen, write_data: list):
        try:
            while True:
                if not write_data and self.kill_writer:
                    break
                i = 0
                for line in write_data:
                    i += 1
                    proc.stdin.write(line)
                    proc.stdin.flush()
                    #logging.info("writer wrote input %s" % line)
                for x in range(i):
                    write_data.pop(0)
                if self.can_kill_writer:
                    self.kill_writer = True
                    break
                    
            proc.stdin.close()
            logging.info("writer finished his work. kill_writer: %s" % self.kill_writer)
        except Exception as e:
            logging.error("got an error in writer: %s" % e)
    
    def limiter(self, proc: Popen, nothing: list):
        try:
            self.start_time = time()
            while time() - self.start_time <= self.time_limit and not self.kill_limiter:
                pass
            if self.kill_limiter:
                logging.info("Limiter killed, OK.")
            else:
                logging.info("Time Limit Exceed, terminating the process...")
            self.kill_writer = True
            self.kill_reader = True
            proc.stdin.close()
            proc.stdout.close()
            proc.terminate()
            if not self.kill_limiter:
                logging.info("Time Limit Exceed, terminated.")
        except Exception as e:
            logging.error("got an error in limiter: %s" % e)
    
    def set_time_limit(self, limit: int):
        self.time_limit = limit
    
    def start(self):
        logging.info("starting...")
        self._limiter.start()
        self._reader.start()
        self._writer.start()
        logging.info("started...")
    
    def write_line(self, line: str):
        self.write_data.append(bytes(line + "\n", encoding="utf-8"))
        #logging.info("added %s to write list" % line)
    
    def end_write(self):
        logging.info("Now writer can be killed...")
        self.can_kill_writer = True
    
    def wait(self):
        while not self.kill_writer or not self.kill_reader:
            pass
        logging.info("waiting ended. elements awaiting for write: %s" % len(self.write_data))
        self.kill_limiter = True
    
    def get_elapsed(self, t: float) -> float:
        return t - self.start_time
