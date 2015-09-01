# Singleton pattern, decorate new classes with @Singleton to make them a singleton
# taken from https://razvantudorica.com/08/example-for-singleton-decorator-pattern-in-python/

class Singleton:
  def __init__(self, klass):
    self.klass = klass
    self.instance = None
  def __call__(self, *args, **kwds):
    if self.instance == None:
      self.instance = self.klass(*args, **kwds)
    return self.instance
