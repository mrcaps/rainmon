#test whether plotting is possible

from pylab import *

if __name__ == "__main__":
	plot([1,2,3])
	show()
	savefig("test.png",format='png')
