import inspect

# If you set _DEBUG to true, @coroutine will wrap the resulting
# generator objects in a CoroWrapper instance (defined below).  That
# instance will log a message when the generator is never iterated
# over, which may happen when you forget to use "yield from" with a
# coroutine call.  Note that the value of the _DEBUG flag is taken
# when the decorator is used, so to be of any use it must be set
# before you define your coroutines.  A downside of using this feature
# is that tracebacks show entries for the CoroWrapper.__next__ method
# when _DEBUG is true.
_DEBUG = False
import functools


class Return(StopIteration):
    def __init__(self, value=None):
        StopIteration.__init__(self)
        self.value = value

def create_generator(result):
    # dead code to ensure that create_generator() is a generator
    if 0:
        yield None
    raise Return(result)

def create_exception_generator(err):
    # dead code to ensure that create_generator() is a generator
    if 0:
        yield None
    raise err

class CoroWrapper(object):
    """Wrapper for coroutine in _DEBUG mode."""

    __slot__ = ['gen', 'func']

    def __init__(self, gen, func):
        assert inspect.isgenerator(gen), gen
        self.gen = gen
        self.func = func

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.gen)

    def send(self, value):
        return self.gen.send(value)

    def throw(self, exc):
        return self.gen.throw(exc)

    def close(self):
        return self.gen.close()

    def __del__(self):
        frame = self.gen.gi_frame
        if frame is not None and frame.f_lasti == -1:
            func = self.func
            code = func.__code__
            filename = code.co_filename
            lineno = code.co_firstlineno
            logger.error(
                'Coroutine %r defined at %s:%s was never yielded from',
                func.__name__, filename, lineno)


def coroutine(func):
    """Decorator to mark coroutines.

    If the coroutine is not yielded from before it is destroyed,
    an error message is logged.
    """
    if True:
        # FIXME: dead code
        if inspect.isgeneratorfunction(func):
            coro = func
        else:
            @functools.wraps(func)
            def coro(*args, **kw):
                res = func(*args, **kw)
                from asyncio import futures
                if isinstance(res, futures.Future) or inspect.isgenerator(res):
                    res = yield res
                raise Return(res)

        wrapper = coro

        wrapper._is_coroutine = True  # For iscoroutinefunction().
        return wrapper
    else:
        if not inspect.isgeneratorfunction(func):
            # FIXME: functools.wrapped
            def wrapped(*args, **kw):
                try:
                    res = func(*args, **kw)
                except Exception as err:
                    return create_exception_generator(err)
                else:
                    if inspect.isgenerator(res):
                        return res
                    else:
                        return create_generator(res)
            wrapped._is_coroutine = True  # For iscoroutinefunction().
            return wrapped
        else:
            return func
