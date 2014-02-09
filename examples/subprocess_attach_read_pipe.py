#!/usr/bin/env python3
"""Example showing how to attach a read pipe to a subprocess."""
import asyncio
import os, sys
from asyncio import subprocess

code = """
import os, sys
fd = int(sys.argv[1])
data = os.write(fd, b'data')
os.close(fd)
"""

loop = asyncio.get_event_loop()

@asyncio.coroutine
def task():
    rfd, wfd = os.pipe()
    args = [sys.executable, '-c', code, str(wfd)]

    pipe = os.fdopen(rfd, 'rb', 0)
    reader = asyncio.StreamReader(loop=loop)
    protocol = asyncio.StreamReaderProtocol(reader, loop=loop)
    transport, _ = yield loop.connect_read_pipe(lambda: protocol, pipe)

    kwds = {}
    if sys.version_info >= (3, 2):
        kwds['pass_fds'] = (wfd,)
    proc = yield asyncio.create_subprocess_exec(*args, **kwds)
    yield proc.wait()

    os.close(wfd)
    data = yield reader.read()
    print("read = %r" % data.decode())

loop.run_until_complete(task())