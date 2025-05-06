#Importing most necessary libraries

from astropy.table import Table
from matplotlib import pyplot as plt
import os
import numpy as np
from astropy.io.ascii import masked
from astropy.coordinates import Angle
from astropy.io import ascii
import glob
from astropy.io import fits
import wget
import matplotlib.image as mpimg
from astropy.wcs import WCS
from scipy.stats import scoreatpercentile
from astropy.visualization import simple_norm
from reproject import reproject_interp
import sys
from IPython.display import clear_output
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
from photutils.aperture import CircularAperture
from astropy.visualization import SqrtStretch
from astropy.visualization import ImageNormalize
from astropy.visualization import LogStretch
from astropy.wcs import WCS
import astropy.units as u
from astropy.stats import sigma_clipped_stats
from astropy.coordinates import Angle
from scipy import stats
from astropy.visualization import MinMaxInterval
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib import pyplot as plt
from matplotlib import colors
from astropy.stats import gaussian_sigma_to_fwhm
from astropy.nddata import CCDData
import warnings
warnings.filterwarnings('ignore')

mycolors = plt.rcParams['axes.prop_cycle'].by_key()['color']

from photutils.isophote import EllipseGeometry
from photutils.aperture import EllipticalAperture
#define an empty dictionary that will contain the EllipseGeometry instance
geometry = {}
initparams = {}
#initialize dictionary for half-light radii
rhalfpix = {}
rhalfasec = {}
from photutils.isophote import Ellipse
from photutils import aperture_photometry
#initialize dictionary for ellipse fitting
ellipse = {}
isolist = {}
def find_files(destination_folder, partial_name):
    matching_files = []

    for root, dirs, files in os.walk(destination_folder):
        for file in files:
            if partial_name.lower() in file.lower():
                matching_files.append(os.path.join(root, file))

    return matching_files 
def aperture(data):
        '''
        # rmax is max radius to measure ellipse
        # could cut this off based on SNR
        # or could cut this off based on enclosed flux?
        # or could cut off based on image dimension, and do the cutting afterward
        
        #rmax = 2.5*self.sma
        '''
        # rmax is set according to the image dimensions
        # look for where the semi-major axis hits the edge of the image
        # could by on side (limited by x range) or on top/bottom (limited by y range)
        # 
        yimage_max, ximage_max = data.shape
        
        rmax = np.min([(ximage_max - x0)/abs(np.cos(PAN)),\
                        (yimage_max - y0)/abs(np.sin(PAN))])
        index = np.arange(80)
        apertures = (index+1)*.5*.7*(1+(index+1)*.1)
        # cut off apertures at edge of image
        apertures_a = apertures[apertures < rmax]
        return apertures_a
def imdisplay(image,x,y,sma,ellip,pa, v1perc=10, v2perc=95, logscale=True): #normal non-aperture display
    '''
    display an image 
    OPTIONAL KEYWORD PARAMETERS
    v1perc: one end of the colormap assigned to the v1perc percent lowest flux 
    v2perc: the other end of the colormap assigned to the v2perc percent highest flux    
    '''
    # make sure image is an np array
    nimage = np.array(image)
    # determine the pixel values at the 10th and 95th percentile
    v1 = scoreatpercentile(nimage,v1perc)
    v2 = scoreatpercentile(nimage,v2perc)
    # display using imshow
    #
    # you can play with alternate cmaps in the function below, such as "viridis" or "gray"
    # The 'gray_r' color map reverses the color-scale so that dark display pixels are the brightest in the image
    #
    # vmin and vmax set the min and max pixel values that
    # will be mapped to the extremes of the colormap
    print(v1,v2)
    norm = None
    if (logscale):
        norm = ImageNormalize(vmin=v1, vmax=v2, stretch=LogStretch())
    else:
        norm = ImageNormalize(vmin=v1, vmax=v2)
    im = ax.imshow(image, origin='lower', norm=norm)
    aper = EllipticalAperture((x, y), sma,
                              (ellip)*sma, pa)
    plt.axis('off')    
    aper.plot(color='red')
    return fig,ax
    #fig.colorbar(fraction=.08)
def imdisplay2(image, ellipses, v1perc=10, v2perc=95, logscale=True, ax=None): #display images with ellipses imposed on it
    '''
    Display an image with multiple elliptical apertures overlaid.
    
    Parameters:
    - image: 2D numpy array (the image to display)
    - ellipses: list of tuples [(x, y, sma, ellip, pa), ...] for each ellipse
    - v1perc: percentile for lower intensity scale (default: 10)
    - v2perc: percentile for upper intensity scale (default: 95)
    - logscale: whether to apply a logarithmic stretch to the image (default: True)
    - ax: optional matplotlib axis to overlay on an existing figure

    Returns:
    - fig, ax: matplotlib figure and axis objects
    '''
    # Ensure image is a numpy array
    nimage = np.array(image)

    # Compute display intensity limits
    v1 = scoreatpercentile(nimage, v1perc)
    v2 = scoreatpercentile(nimage, v2perc)
    print(f"Image intensity limits: v1={v1}, v2={v2}")

    # Normalize for display
    norm = ImageNormalize(vmin=v1, vmax=v2, stretch=LogStretch() if logscale else None)

    # Create a new figure and axis if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    else:
        fig = ax.figure  # Get the figure from the provided axis

    # Display the image
    ax.imshow(image, origin='lower', norm=norm)

    # Overlay all ellipses
    for x, y, sma, ellip, pa in ellipses:
        aper = EllipticalAperture((x, y), sma, ellip * sma, pa)
        aper.plot(color='red', lw=1, alpha=0.7, ax=ax)  # Overlay each ellipse
    ax.axis('off')  # Hide axes
    return fig, ax
def measure_phot(data, apertures_a):
        apertures_b = (EPLI)*apertures_a
        area = np.pi*apertures_a*apertures_b # area of each ellipse

        flux1 = np.zeros(len(apertures_a),'f')
        allellipses = []
        for i in range(len(apertures_a)):
            # EllipticalAperture takes rotation angle in radians, CCW from +x axis
            ap = EllipticalAperture((x0, y0),apertures_a[i],apertures_b[i],PAN)#,ai,bi,theta) for ai,bi in zip(a,b)]
            allellipses.append(ap)
                    # subpixel is the method used by Source Extractor
            phot_table1 = aperture_photometry(data, ap, method = 'subpixel', 
                                                    subpixels=5)
            
            flux1[i] = phot_table1['aperture_sum'][0]
            if np.isnan(flux1[i]):
                break
        # first aperture is calculated differently
        sb1 = np.zeros(len(apertures_a),'f')
        flux1 = flux1 / pixscale #convert the units of the flux from Jy/pix to Jy/arcsec)
        sb1[0] = flux1[0]/area[0]
        # outer apertures need flux from inner aperture subtracted
        for i in range(1,len(area)):
            sb1[i] = (flux1[i] - flux1[i-1])/(area[i]-area[i-1])    
        valid_indices = ~np.isnan(sb1) & ~np.isnan(flux1) & (sb1 != 0) & (flux1 != 0)
        sb1 = sb1[valid_indices]
        flux1 = flux1[valid_indices]
        apertures_a = apertures_a[valid_indices]
        flux1_err = np.zeros(len(apertures_a),'f')
        sb1_err = np.zeros(len(apertures_a),'f')
        print('Number of apertures for',wave ,'microns band = ',len(apertures_a))
        # Find the maximum values
        sb1max = np.max(sb1)
        flux1max = np.max(flux1)
        arcsec_apt = apertures_a * pixscale
        apertures_ahalf1 = np.max(arcsec_apt) / 2
        total_apt = len(apertures_a)
        return sb1, flux1, sb1max, flux1max, apertures_ahalf1, flux1_err, sb1_err, apertures_a, arcsec_apt, total_apt