import numpy as np
from osgeo import gdal
import skimage.color as color
import cv2

dsp = gdal.Open("PAN.TIF")
dsm = gdal.Open("MULTI.TIF")

bands=dsm.ReadAsArray()
pan = dsp.GetRasterBand(1).ReadAsArray()

R = cv2.resize(bands[0,:,:], (pan.shape[1],pan.shape[0]))
G = cv2.resize(bands[1,:,:], (pan.shape[1],pan.shape[0]))
B = cv2.resize(bands[2,:,:], (pan.shape[1],pan.shape[0]))
I = cv2.resize(bands[3,:,:], (pan.shape[1],pan.shape[0]))


def simple_mean():
    image = np.empty((R.shape[0], R.shape[1], 3))
    image[:, :, 0] = 0.5*(R+pan)
    image[:, :, 1] = 0.5*(G+pan)
    image[:, :, 2] = 0.5*(B+pan)
    return image


def brovey():
    image = np.empty((R.shape[0], R.shape[1], 3))
    image[:, :, 0] = pan*np.true_divide(R, R + G + B)
    image[:, :, 1] = pan*np.true_divide(G, R + G + B)
    image[:, :, 2] = pan*np.true_divide(B, R + G + B)
    return image


def esri():
    adj=pan-(R+G+B)/3
    image = np.empty((R.shape[0], R.shape[1], 4))
    image[:, :, 0] = R+adj
    image[:, :, 1] = G+adj
    image[:, :, 2] = B+adj
    image[:, :, 3] = I+adj
    return image


def ihs():
    array=np.empty((R.shape[0], R.shape[1], 3))
    array[:, :, 0] = R
    array[:, :, 1] = G
    array[:, :, 2] = B
    hsv=color.rgb2hsv(array)
    hsv[:,:,2]=pan-I*0.1
    image=color.hsv2rgb(hsv)
    return image


def saveImage(image, outname, dsp):
    nrows, ncols = image[:,:,0].shape
    driv  = gdal.GetDriverByName('GTiff')
    if image.shape==(image[:,:,0].shape,4):
        dst = driv.Create(outname, ncols, nrows, 4, gdal.GDT_UInt16)
        dst.SetGeoTransform(dsp.GetGeoTransform())
        dst.SetProjection(dsp.GetProjection())
        dst.GetRasterBand(1).WriteArray(image[:,:,0])
        dst.GetRasterBand(2).WriteArray(image[:,:,1])
        dst.GetRasterBand(3).WriteArray(image[:,:,2])
        dst.GetRasterBand(4).WriteArray(image[:,:,3])
    else:
        dst = driv.Create(outname, ncols, nrows, 3, gdal.GDT_UInt16)
        dst.SetGeoTransform(dsp.GetGeoTransform())
        dst.SetProjection(dsp.GetProjection())
        dst.GetRasterBand(1).WriteArray(image[:,:,0])
        dst.GetRasterBand(2).WriteArray(image[:,:,1])
        dst.GetRasterBand(3).WriteArray(image[:,:,2])
    dst = None
    del dst


saveImage(simple_mean(),"simple.tif",dsp)
saveImage(brovey(),"brovey.tif",dsp)
saveImage(esri(),"esri.tif",dsp)
saveImage(ihs(),"ihs.tif",dsp)