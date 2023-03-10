from test import customer
from multiprocessing import Process, Queue, Pool, get_context
from statistics import mean
import itertools
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

def main():
    times = []
    no_proc = 4000
    print('aaa')
    p =  Pool(processes=400, maxtasksperchild=1) 
    print('aaa')
    times = p.map(customer, range(no_proc))
    print('aaa')

    # p.terminate()
    # p.join()
    print('finished')
    times = list(itertools.chain(*times))
    #print(times)

    try:
        print("mean: ", mean(times))
        print("max: ", max(times))
        print("min: ", min(times))
    except:
        pass
    plt.hist(times, bins=100)
    plt.show()

if __name__ == "__main__":
    main()