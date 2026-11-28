import faulthandler, sys, runpy
faulthandler.dump_traceback_later(90, exit=True)
sys.argv = ["residual.py"] + sys.argv[1:]
runpy.run_path("residual.py", run_name="__main__")
