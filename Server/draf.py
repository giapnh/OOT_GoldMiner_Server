__author__ = 'Nguyen Huu Giap'
import inspect
import command
class Test:
    ARG_1 = 1
    ARG_2 = 2

for a in dir(Test):
    if a.startswith("ARG_"):
       if getattr(Test(),a) == 1:
           print a

# for a in dir(Test):
#     if inspect.isbuiltin(a)== False and inspect.ismethod(a) == False:
#         print a
