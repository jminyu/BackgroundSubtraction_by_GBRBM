import os.path
import numpy as np
import cPickle
from PIL import Image
from scipy import ndimage 
import matplotlib.pylab as plt
import matplotlib.cm as cm

def print_it(x, dir_name, files):
    print dir_name
    dataset = np.zeros(120*160)
    #dataset = np.zeros(256*320)
    for f in files:
        imf = Image.open(dir_name + '/' + f)
        #d = np.array(imf)
        d = ((np.array(imf.getdata())/255) > 0.5 ) * 1 
        print d.shape
        dataset = np.vstack((dataset,d))
    output = open(dir_name + '.pkl', 'wb')
    cPickle.dump(dataset, output)
    output.close()

def generate_orignal(x, dir_name, files):
    print dir_name
    dataset = np.zeros(120*160)
    for f in files:
        imf = Image.open(dir_name + '/' + f)
        d = (np.array(imf.getdata())/255)  
        dataset = np.vstack((dataset,d))
    output = open('imagedata_orignal.pkl', 'wb')
    cPickle.dump(dataset[1:, :], output)
    output.close()
   
def generate_grayscale(x, dir_name, files):
    print dir_name
    #dataset = np.zeros(120*160)
    for f in files:
        imf = Image.open(dir_name + '/' + f)
        imf = imf.convert('1')
        imf.save(dir_name +'/' + f)
        
def generateBlurImg(x, dir_name, files):
    print dir_name
    dataset = np.zeros(120*160)
    #dataset = np.zeros(320*256)
    for f in files:
        imf = Image.open(dir_name + '/' + f)
        blr = ndimage.gaussian_filter(np.reshape(np.array(imf.getdata()),(120,160)),sigma=0.6)
        #blr = ndimage.gaussian_filter(np.reshape(np.array(imf.getdata()),(256,320)),sigma=0.6)
        d = ((blr*1.0/255) > 0.5 ) * 1 
        #plt.imshow((numpy.reshape(p[:,i],(28,28))), cmap = cm.Greys_r, interpolation ="nearest")
        # plt.imshow(d, cmap = cm.Greys_r)
        # plt.show()
        d = d.flatten()
        #print d.shape
        dataset = np.vstack((dataset,d))
    output = open(dir_name + 'blr_varp6.pkl', 'wb')
    cPickle.dump(dataset[1:, :], output)
    output.close()

def generateBlurImgOrg(x, dir_name, files):
    print dir_name
    dataset = np.zeros(120*160)
    for f in files:
        imf = Image.open(dir_name + '/' + f)
        blr = ndimage.gaussian_filter(np.reshape(np.array(imf.getdata()),(120,160)),sigma=0.6)
        d = ((blr*1.0/255) > 0.5 ) * 1 
        #plt.imshow((numpy.reshape(p[:,i],(28,28))), cmap = cm.Greys_r, interpolation ="nearest")
        # plt.imshow(d, cmap = cm.Greys_r)
        # plt.show()
        d = d.flatten()
        #print d.shape
        dataset = np.vstack((dataset,d))
    output = open('imagedata_blr_var_Org.pkl', 'wb')
    cPickle.dump(dataset[1:, :], output)
    output.close()

#os.path.walk('Bootstrap\orignal', generate_grayscale, 0)
#os.path.walk('fountain01/orignal/gcdataset', generate_grayscale, 0)

os.path.walk('LightSwitch\gcdataset', print_it, 0)
os.path.walk('LightSwitch\gcdataset', generateBlurImg, 0)