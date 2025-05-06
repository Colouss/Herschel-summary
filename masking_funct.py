#importing the important libraries
def imdisplay(image,x,y, sma, ellip,pa,width=100, height=100, v1perc=10, v2perc=95, logscale=True):
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
    # Adjust the view to focus on (x, y) without cropping the image
    x_min = max(x - width // 2, 0)
    x_max = min(x + width // 2, nimage.shape[1])
    y_min = max(y - height // 2, 0)
    y_max = min(y + height // 2, nimage.shape[0])
    # Set the axis limits so that (x, y) is at the center
    ax.set_xlim(x - width // 2, x + width // 2)
    ax.set_ylim(y - height // 2, y + height // 2)
    # Hide axis ticks and labels
    plt.axis('off')    
    aper.plot(color='red')
    return fig,ax
    #fig.colorbar(fraction=.08)
def find_files(destination_folder, partial_name):
    matching_files = []

    for root, dirs, files in os.walk(destination_folder):
        for file in files:
            if partial_name.lower() in file.lower():
                matching_files.append(os.path.join(root, file))

    return matching_files 
# Function to overlay mask on original FITS image and save as a new FITS file
def overlay_mask_on_fits(fits_file, mask_file, csv_file, output_fits, n, coords_x, coords_y):
    # Load the original FITS image and its WCS
    original_fits_data, original_fits_header = fits.getdata(fits_file, header=True)
    original_wcs = WCS(original_fits_header)
    # Load the mask FITS image and its WCS
    mask_fits_data, mask_fits_header = fits.getdata(mask_file, header=True)
    mask_wcs = WCS(mask_fits_header)
    # Extract the central X and Y pixel coordinates (assuming columns are named 'x' and 'y')
    central_x = int(coords_x)
    central_y = int(coords_y) 
    # Reproject the mask to the original FITS image WCS
    reprojected_mask, footprint = reproject_interp((mask_fits_data, mask_wcs), original_wcs, shape_out=original_fits_data.shape)    
    # Ensure that the central pixel coordinates are within the bounds of the original image
    height, width = original_fits_data.shape
    central_x = np.clip(central_x, 0, width - 1)
    central_y = np.clip(central_y, 0, height - 1)
    # Create a copy of the original FITS data and overlay the reprojected mask
    combined_data = original_fits_data.copy()
    # Overlay the mask where the mask is non-zero (assumes mask values are 0 or 1)
    combined_data[reprojected_mask > 0] = np.max(original_fits_data)  # Overlay mask pixels
    # Ensure that the central pixel is not masked unless explicitly masked in the mask file
    if reprojected_mask[central_y, central_x] == 0:
        # If the mask does not cover the central pixel, restore the original value
        combined_data[central_y, central_x] = original_fits_data[central_y, central_x]
    #else:
        # Optionally, you can mark the central pixel differently if the mask explicitly masks it
        #print(f"Central pixel ({central_x}, {central_y}) is masked in the mask file.")
    # Save the result as a new FITS file
    fits.writeto(output_fits, combined_data, original_fits_header, overwrite=True)