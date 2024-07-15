#Lillehei

#--------------------------------------------------------------------------------------------------------------------
# IMPORTS
#--------------------------------------------------------------------------------------------------------------------


import aplpy
import astropy
import astroquery
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt
import urllib 
import pandas as pd 


from scipy.stats import norm
from urllib.parse import urlencode
from astropy.io import fits
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from astroquery.hips2fits import hips2fits
from astropy.coordinates import SkyCoord, Longitude, Latitude, Angle
from astropy import wcs as astropy_wcs
from astroquery.hips2fits import conf

# from flux_counts import *



#--------------------------------------------------------------------------------------------------------------------
# INPUTS
#--------------------------------------------------------------------------------------------------------------------

Database = '2MASS'                #2MASS, DSS


height    = 1024                   #Pixel image sizes
width     = 1024

resolution1 = 10 # times arcmin   #zoom amount

#--------------------------------------------------------------------------------------------------------------------
# FUNCTIONS
#--------------------------------------------------------------------------------------------------------------------

def gaussian(x, mu, sig):
    return 1./(np.sqrt(2.*np.pi)*sig)*np.exp(-np.power((x - mu)/sig, 2.)/2)


#--------------------------------------------------------------------------------------------------------------------
# SPACECRAFT DATA OLD
#--------------------------------------------------------------------------------------------------------------------

# 15 "/sec / 0.34 "/px = 44 px/s
# 3 "/sec / 0.34 "/px = 9 px/s
xrate     = 9           # px/s
yrate     = 44          # px/s
countrate = 3554
step      = 0.1          # time step
seeing    = 9            # px FWHM
sunfrac   = 0.0          # intensity of reflected sunlight to laser light from spacecraft
frac      = 0.25         # fraction of laser cycle on
dur       = 2.0          # laser cycle duration in seconds
sigma     = seeing /2.355
times     = np.arange(1,91,step)


y     = yrate * times
x     = xrate * times
yint  = np.round(y).astype(int)
xint  = np.round(x).astype(int)
yfrac = y - yint
xfrac = x - xint

#--------------------------------------------------------------------------------------------------------------------
# SPACECRAFT DATA NEW
#--------------------------------------------------------------------------------------------------------------------

data = np.genfromtxt('satcoord.csv',delimiter=',',skip_header=1) # inputs data file

TimeEST = data[:,0]
RA      = data[:,1]
Dec     = data[:,2]
Az      = data[:,3]
Alt     = data[:,4]
Dist    = data[:,5]
R_Flux  = data[:,6]
Count1  = data[:,7]

print(RA)
print(Dec)

print ("INFO: SPACECRAFT DATA IMPORTED")

RA_import = RA[30000]
Dec_import = Dec[30000]

#--------------------------------------------------------------------------------------------------------------------
# SIMBAD REGION QUERY
#--------------------------------------------------------------------------------------------------------------------



#      First, RA, h   m  s      Dec,  d  m  s 
# Coord = SkyCoord('0   37  41.1       -33 42 59', unit=(u.hourangle, u.deg), frame='fk5') 
# query_results = Simbad.query_region(Coord, radius =queryrad)


# print(query_results)


# object_main_id = query_results[0]['MAIN_ID']
# object_coords = SkyCoord(ra=query_results['RA'], dec=query_results['DEC'], 
#                           unit=(u.hourangle, u.deg), frame='icrs')



# query_params = { 
#      'hips': Database,
#      'object': object_main_id, 
#      'ra': object_coords[0].ra.value, 
#      'dec': object_coords[0].dec.value, 
#      'fov': (resolution1 * u.arcmin).to(u.deg).value, 
#      'width': width, 
#      'height': height
# }

#--------------------------------------------------------------------------------------------------------------------
# HIPS2FITS QUERY FOR FITS FILE
#--------------------------------------------------------------------------------------------------------------------



w = astropy_wcs.WCS(header={
	'BITPIX': 16,
    'WCSAXES': 2,           # Number of coordinate axes
    'CTYPE1': 'RA---TAN', 
    'CUNIT1': 'deg', 
    'CDELT1': -0.0002777777778,        # [deg] Coordinate increment at reference point
    'CRPIX1': 512, 
    'CRVAL1': RA_import,
    'NAXIS1': height,
    'CTYPE2': 'DEC--TAN', 
    'CUNIT2': 'deg', 
    'CDELT2': 0.0002777777778, 
    'CRPIX2': 512, 
    'CRVAL2': Dec_import, 
    'NAXIS2': width
})


wcs_input_dict = {
    'CTYPE1': 'RA---TAN', 
    'CUNIT1': 'deg', 
    'CDELT1': -0.0002777777778, 
    'CRPIX1': 1, 
    'CRVAL1': RA_import, 
    'NAXIS1': height,
    'CTYPE2': 'DEC--TAN', 
    'CUNIT2': 'deg', 
    'CDELT2': 0.0002777777778, 
    'CRPIX2': 1, 
    'CRVAL2': Dec_import, 
    'NAXIS2': width
}

print ("INFO: WCS Header Created")

result = hips2fits.query_with_wcs(
    hips="CDS/P/{}/K".format(Database),
    wcs = w,
    get_query_payload=False,
   
)

print ("INFO: Fits file imported")


#--------------------------------------------------------------------------------------------------------------------
# DOWNLOAD FITS FILE
#--------------------------------------------------------------------------------------------------------------------


result.writeto("2MASS_FITS.fits",overwrite=True)



# hdul = fits.open("2MASS_FITS.fits")
# image = hdul[0].data
# plt.imshow(image)
# hdul.info()

# wcs2 = astropy_wcs.WCS(header=hdul[0].header)
# ax = plt.subplot(projection=wcs2)
# im = ax.imshow(image)
# plt.colorbar(im)

# dec_ll, ra_ll = Dec[0], RA[0]
# dec_ur, ra_ur = Dec[59999], RA[59999]

# (xmin, xmax), (ymin, ymax) = wcs2.all_world2pix([ra_ll, ra_ur], [dec_ll, dec_ur], 0)
# (xmin, xmax), (ymin, ymax)

# xmin_int, xmax_int = int(np.floor(xmin)), int(np.ceil(xmax))
# ymin_int, ymax_int = int(np.floor(ymin)), int(np.ceil(ymax))
# (xmin_int, xmax_int), (ymin_int, ymax_int)
# subregion = image[ymin_int:ymax_int,xmin_int:xmax_int]

# ax = plt.subplot(projection=wcs2)
# im = ax.imshow(subregion)
# plt.colorbar(im)
# ax.set(xlim=(xmin, xmax), ylim=(ymin, ymax))




#--------------------------------------------------------------------------------------------------------------------
#
#--------------------------------------------------------------------------------------------------------------------


wcs_helix_dict = astropy_wcs.WCS(wcs_input_dict)

header_data_unit_list = fits.open("2MASS_FITS.fits")

header_data_unit_list.info()

image1 = header_data_unit_list[0].data

header1 =header_data_unit_list[0].header

print(header1)

wcs_helix = astropy_wcs.WCS(header1)

print(wcs_helix)


#--------------------------------------------------------------------------------------------------------------------
# GRAB AND MODIFY FITS FILE OLD
#--------------------------------------------------------------------------------------------------------------------

#hdul3 = fits.getdata("TOI_5463.01_90.000s_R-0018_out.fits")
hdul3 = fits.getdata("2MASS_FITS.fits")

print ("INFO: Fits file grabbed for modification")


# data_frame = pd.DataFrame(hdul3)
# print(data_frame.shape)

# for i in range(len(y)):
# 	for j in range(-30,30):
# 		for k in range(-30,30):	
# 			if ((times[i] % dur) /dur < frac):
# 				hdul3[1024+xint[i]+j,yint[i]+k] += (1.0+sunfrac)*countrate*step*gaussian(np.sqrt((j+xfrac[i])*(j+xfrac[i])+(k+yfrac[i])*(k+yfrac[i])),0,sigma)
# 			else: 
# 				hdul3[1024+xint[i]+j,yint[i]+k] += (0.0+sunfrac)*countrate*step*gaussian(np.sqrt((j+xfrac[i])*(j+xfrac[i])+(k+yfrac[i])*(k+yfrac[i])),0,sigma)

# hdu1=fits.PrimaryHDU(hdul3)

# hdu1.writeto('test.fits',overwrite=True)

# hdu11 = fits.open("test.fits")



#--------------------------------------------------------------------------------------------------------------------
# GRAB AND MODIFY FITS FILE NEW
#--------------------------------------------------------------------------------------------------------------------

fig = plt.figure(figsize=(10, 10), frameon=False)
ax = plt.subplot(projection=wcs_helix)
ax.arrow(RA[0], Dec[0], (RA[60000-1]-RA[0]), (Dec[60000-1]-Dec[0]), 
         head_width=0, head_length=0, 
         fc='orange', ec='orange', width=0.0003, 
         transform=ax.get_transform('icrs'))
ax.arrow(RA[30000-1], Dec[30000-1], 0, -0.1, 
         head_width=0, head_length=0, 
         fc='red', ec='red', width=0.003, 
         transform=ax.get_transform('icrs'))
plt.text(RA[30000-1], -4.075, '0.1 deg', 
         color='white', rotation=90, 
         transform=ax.get_transform('icrs'))
plt.imshow(image1, origin='lower', cmap='cividis', aspect='equal')

overlay = ax.get_coords_overlay('galactic')
overlay.grid(color='white', ls='dotted')
plt.xlabel(r'RA')
plt.ylabel(r'Dec')

plt.savefig("Image_sim.png")
plt.show()


print ("INFO: Fits file modification complete")
#--------------------------------------------------------------------------------------------------------------------
# PLOTTING FITS FILES
#--------------------------------------------------------------------------------------------------------------------



# gc = aplpy.FITSFigure(result)
# gc.show_colorscale(cmap='inferno')
# gc.show_contour(data=result,filled=False,cmap='inferno')

       
# gc.save('2MASS_UNEDITED.png')


# gc1 = aplpy.FITSFigure(hdu11)
# gc1.show_colorscale(cmap='inferno')
# gc1.save('2MASS_FITS_MOD.png')

# print ("INFO: PNGs Created! Closing code.")