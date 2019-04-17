from optparse import OptionParser
from itertools import zip_longest
import numpy as np
from glob import glob

scale_saved = ''
image_name = ''

def readtps(input):
    """
    Function to read a .TPS file
    Args:
        input (str): path to the .TPS file
    Returns:
        lm (str list): info extracted from 'LM=' field
        im (str list): info extracted from 'IMAGE=' field
        id (str list): info extracted from 'ID=' filed
        coords: returns a 3D numpy array if all the individuals have same
                number of landmarks, otherwise returns a list containing 2d
                matrices of landmarks
    """

    # open the file
    tps_file = open(input, 'rb')  # 'r' = read
    tps = tps_file.read().decode('iso-8859-15').splitlines()  # read as lines and split by new lines
    tps_file.close()

    # initiate lists to take fields of "LM=","IMAGE=", "ID=" and the coords
    lm, im, ID, coords_array = [], [], [], []

    # looping thru the lines
    for i, ln in enumerate(tps):

        # Each individual starts with "LM="
        if ln.startswith("LM"):
            # number of landmarks of this ind
            lm_num = int(ln.split('=')[1])
            # fill the info to the list for all inds
            lm.append(lm_num)
            # initiate a list to take 2d coordinates
            coords_mat = []

            # fill the coords list by reading next lm_num of lines
            for j in range(i + 1, i + 1 + lm_num):
                coords_mat.append(tps[j].split(' '))  # split lines into values

            # change the list into a numpy matrix storing float vals
            coords_mat = np.array(coords_mat, dtype=float)
            # fill the ind 2d matrix into the 3D coords array of all inds
            coords_array.append(coords_mat)
            # coords_array.append(coords_mat)

        # Get info of IMAGE= and ID= fields
        if ln.startswith("IMAGE"):
            im.append(ln.split('=')[1])
            global image_name
            image_name = ln

        if ln.startswith("ID"):
            ID.append('='.join(ln.split('=')[1:]))

        if ln.startswith("SCALE"):
            global scale_saved
            scale_saved = ln

    # check if all inds contains same number of landmarks
    all_lm_same = all(x == lm[0] for x in lm)
    # if all same change the list into a 3d numpy array
    if all_lm_same:
        coords_array = np.dstack(coords_array)

    # return results in dictionary form
    return {'lm': lm, 'im': im, 'id': ID, 'coords': coords_array}



#from pylab import *


def main(input_pat, points_num):
    for f in glob(input_pat):
        print("Found file: ", f)
        data = readtps(f)
        with open('output_%s' % f, 'w') as f:
            for k, id, lm in zip_longest(range(data['coords'].shape[-1]), data['id'],  data['lm']):
                print("index: {}, id={}, lm={}".format(k, id, lm))
                xdata = data['coords'][:, 0, k]
                ydata = data['coords'][:, 1, k]

                #argind = np.argsort(xdata)

                ind1 = 0
                ind2 = -1
                n = len(xdata)
                ind3 = int(n / 2) + 1
                ind4 = int(n / 2) - 1

                meanx1 = 0.5 * (xdata[ind1] + xdata[ind2])
                meany1 = 0.5 * (ydata[ind1] + ydata[ind2])
    #          meanx2 = 0.5 * (xdata[ind3] + xdata[ind4])
    #          meany2 = 0.5 * (ydata[ind3] + ydata[ind4])
                meanx2 = np.mean(xdata)
                meany2 = np.mean(ydata)
                xdata -= meanx1
                ydata -= meany1
                meanx2 -= meanx1
                meany2 -= meany1
                meanx1 = meany1 = 0.0

                v = (meanx1 - meanx2, meany1 - meany2)
                angle = np.pi / 2-np.arctan(v[1] / v[0])
                rotmat = np.matrix([[np.sin(angle), np.cos(angle)],
                                    [-np.cos(angle), np.sin(angle)]])
                newdata = (rotmat @ np.vstack([xdata, ydata])).T

                newdata[:,0] -= np.min(newdata[:,0]) - 10
                newdata[:,1] -= np.min(newdata[:,1]) - 10

                if newdata[0,0] <= newdata[int(n/2.0), 0]:
                    newdata[:,0] = 2 * np.mean(newdata[:,0]) - newdata[:,0]
                    newdata[:,0] = newdata[::-1, 0]
                    newdata[:,1] = newdata[::-1, 1]
                if np.mean((newdata[1:10,1] - newdata[:9,1])) > 0.0:
                    print("illegal order: ")
                    newdata[:,0] = newdata[::-1, 0]
                    newdata[:,1] = newdata[::-1, 1]

#                plot(xdata, ydata, 'ro')
#                gca().axis('equal')
 #               plot(newdata[:,0], newdata[:,1], 'bo')
 #               ind = 1
  #              for x, y in zip(newdata[:, 0], newdata[:,1]):
  #                  gca().annotate('%s'%ind, (x, y), xytext=(x + 1, y + 1))
  #                  ind += 1
  #              ind = 1
  #              for x, y in zip(xdata, ydata):
  #                  gca().annotate('%s'%ind, (x, y), xytext=(x + 1, y + 1))
 #                   ind += 1
#                show()

                f.write('LM=%s\n' % points_num)
                for item in newdata:
                    f.write('%s %s\n'%(item[0,0], item[0,1]))

                if id is None:
                    pass
                else:
                    f.write('%s\n' % id)

                global scale_saved, image_name
                if image_name:
                    f.write(image_name)
                    f.write('\n')

                if scale_saved:
                    f.write(scale_saved)

                f.write('\n\n')


def execute(option, opt_str, value, parser):
    main(parser.largs[0], value)


parser = OptionParser(add_help_option=False)
parser.add_option("-h", "--help", action="help")
parser.add_option("-n",  action="callback", dest="number", type="int",
                  help="The number of points", callback=execute)
parser.parse_args()


