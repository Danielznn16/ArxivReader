from services.arxiv import checkArxiv
import time
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()

@tl.job(interval=timedelta(minutes=30))
def checkBox():
    checkArxiv()

checkArxiv()
tl.start()
try:
    t = input("Input anything to stop the loop\n")
except:
    print("Error encountered")

tl.stop()
