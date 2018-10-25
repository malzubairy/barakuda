#!/usr/bin/env python

#       B a r a K u d a
#
#  Prepare 2D maps (monthly) that will later become a GIF animation!
#  NEMO output and observations needed
#
#    L. Brodeau, May 2018

import sys
import os
from string import replace
import numpy as nmp

from netCDF4 import Dataset

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.image as image
import matplotlib.cbook as cbook

import warnings
warnings.filterwarnings("ignore")

from calendar import isleap
import datetime

import barakuda_colmap as bcm

import barakuda_tool as bt
import barakuda_ncio as bnc


vmn = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
vml = [ 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]

color_top = 'white'
#color_top = 'k'

cv_out = 'unknown'

jt0 = 0


i2=0
j2=0
l_show_lsm = True
l_do_ice  = True
l_show_cb = True
l_log_field = False
l_pow_field = False
l_annotate_name = True
l_show_clock = True

l_add_logo = True
cf_logo = '/home/brodeau/Dropbox/OceanNext/Graphic_Identity/0LOGO/logo_trans_white_H14_20180917.png'

l_apply_lap = False

narg = len(sys.argv)
if narg < 7: print 'Usage: '+sys.argv[0]+' <NEMOCONF> <BOX> <file> <variable> <LSM_file> <YYYYMMDD (start)>'; sys.exit(0)
CNEMO  = sys.argv[1]
CBOX   = sys.argv[2]
cf_in = sys.argv[3] ; cv_in=sys.argv[4]
cf_lsm=sys.argv[5]  ; cf_clock0=sys.argv[6]

x_logo  = 50 ; y_logo  = 50


if CNEMO == 'eNATL60':
    Ni0 = 8354
    Nj0 = 4729
    l_do_ice  = False
    l_show_cb = False
    l_show_clock = True
    cdt = '1h'
    
    if   CBOX == 'ALL':
        i1=0   ; j1=0    ; i2=Ni0 ; j2=Nj0  ; rfact_zoom=0.3047 ; vcb=[0.59, 0.1, 0.38, 0.018]  ; font_rat=8.*rfact_zoom
        x_clock = 1600 ; y_clock = 200 ; x_logo = 2200 ; y_logo  = 50
        
    elif CBOX == 'FullMed':
        i1=5400; j1=1530; i2=Ni0 ; j2=3310 ; rfact_zoom=0.79   ; vcb=[0.5, 0.875, 0.485, 0.02] ; font_rat=2.*rfact_zoom
        l_annotate_name=False
    
    elif CBOX == 'BlackSea':
        i1=Ni0-1920; j1=3330-1080; i2=Ni0 ; j2=3330 ; rfact_zoom=1.   ; vcb=[0.5, 0.875, 0.485, 0.02] ; font_rat=2.*rfact_zoom
        x_clock = 30 ; y_clock = 1040 ; x_logo = 1500 ; y_logo = 16 ; l_annotate_name=False
    
    elif CBOX == 'Portrait':
        i1=2760; j1=1000; i2=4870; j2=4000 ; rfact_zoom=1.     ; vcb=[0.59, 0.1, 0.38, 0.018]  ; font_rat=1.*rfact_zoom
        l_annotate_name=False; l_show_clock=False
        
    elif CBOX == 'EATL':
        i1=3100; j1=2290; i2=4900; j2=3370 ; rfact_zoom=1.     ; vcb=[0.59, 0.1, 0.38, 0.018] ; font_rat = 2.           ; l_annotate_name=False
        x_clock = 1420 ; y_clock = 1030 ; x_logo = 1500 ; y_logo = 16

    elif CBOX == 'Balear':
        i1=5750; j1=1880; i2=6470; j2=2600 ; rfact_zoom=1. ; vcb=[0.59, 0.1, 0.38, 0.018] ; font_rat = 2. ; l_annotate_name=False
        x_clock = 1420 ; y_clock = 1030 ; x_logo = 1500 ; y_logo = 16

    else:
        print ' ERROR: unknow box "'+CBOX+'" for config "'+CNEMO+'" !!!'
        sys.exit(0)


    
if CNEMO == 'NATL60':
    Ni0 = 5422
    Nj0 = 3454
    #l_pow_field = True ; pow_field = 1.5
    l_do_ice  = False
    l_show_cb = False
    l_show_clock = False
    cdt = '1h'
    #CBOX = 'zoom1' ; i1 = 1800 ; j1 = 950 ; i2 = i1+1920 ; j2 = j1+1080 ; rfact_zoom = 1. ; vcb=[0.5, 0.875, 0.485, 0.02] ; font_rat = 8.*rfact_zoom ; l_show_lsm = False
    #CBOX = 'zoom1' ; i1 = 1800 ; j1 = 950 ; i2 = i1+2560 ; j2 = j1+1440 ; rfact_zoom = 1. ; vcb=[0.5, 0.875, 0.485, 0.02] ; font_rat = 8.*rfact_zoom
    CBOX = 'ALL' ; i1=0 ; j1=0 ; i2=Ni0 ; j2=Nj0 ; rfact_zoom = 0.4 ; vcb=[0.59, 0.1, 0.38, 0.018] ; font_rat = 4.*rfact_zoom
    x_clock = 350 ; y_clock = 7 ; # where to put the date


if CNEMO == 'NANUK025':
    l_do_ice = True
    cdt = '3h'; CBOX = 'ALL' ; i1 = 0 ; j1 = 0 ; i2 = 492 ; j2 = 614 ; rfact_zoom = 2. ; vcb=[0.5, 0.875, 0.485, 0.02] ; font_rat = 8.*rfact_zoom
    x_clock = 350 ; y_clock = 7 ; # where to put the date


print '\n rfact_zoom = ', rfact_zoom
print ' font_rat = ', font_rat, '\n'


print ' i1,i2,j1,j2 =>', i1,i2,j1,j2

nx_res = i2-i1
ny_res = j2-j1

print ' *** nx_res, ny_res =', nx_res, ny_res




yx_ratio = float(ny_res)/float(nx_res)

nxr = int(rfact_zoom*nx_res) ; # widt image (in pixels)
nyr = int(rfact_zoom*ny_res) ; # height image (in pixels)

print ' *** nxr, nyr =', nxr, nyr, '\n'

dpi = 110

rw_fig = round(float(nxr)/float(dpi),2) ; # width of figure
rh_fig = rw_fig*yx_ratio

print ' *** size figure =>', rw_fig, rh_fig, '\n'

fig_type='png'



cyr0=cf_clock0[0:4]
cmn0=cf_clock0[4:6]
cdd0=cf_clock0[6:8]


l_3d_field = False

# Ice:
if l_do_ice:
    cv_ice  = 'siconc'
    cf_ice = replace(cf_in, 'grid_T', 'icemod')
    rmin_ice = 0.5
    cpal_ice = 'ncview_bw'
    vcont_ice = nmp.arange(rmin_ice, 1.05, 0.05)

if cv_in in ['sosstsst','tos']:
    cfield = 'SST'
    tmin=0. ;  tmax=30.   ;  df = 2. ; cpal_fld = 'ncview_nrl'
    #tmin=0. ;  tmax=32.   ;  df = 2. ; cpal_fld = 'viridis'
    #tmin=4. ;  tmax=20.   ;  df = 1. ; cpal_fld = 'PuBu'
    cunit = r'SST ($^{\circ}$C)'
    cb_jump = 2
    l_show_cb = True

if cv_in == 'sossheig':
    cfield = 'SSH'
    #tmin=-0.5 ;  tmax=0.5   ;  df = 0.05
    #tmin=-1.2 ;  tmax=2.3   ;  df = 0.05 ; l_apply_lap = True
    #cpal_fld = 'ncview_jaisnc'
    #cpal_fld = 'PuBu'
    #cpal_fld = 'RdBu'
    #cpal_fld = 'BrBG'
    #
    #cpal_fld = 'on3' ; tmin=-1.2 ;  tmax=2.3   ;  df = 0.05 ; l_apply_lap = True
    cpal_fld = 'on2' ; tmin=-1.2 ;  tmax=1.2   ;  df = 0.05 ; l_apply_lap = True
    #cpal_fld = 'coolwarm' ; tmin=-1. ;  tmax=1.   ;  df = 0.05 ; l_apply_lap = True
    #cpal_fld = 'RdBu_r' ; tmin=-0.9 ;  tmax=-tmin   ;  df = 0.05 ; l_apply_lap = True
    #cpal_fld = 'gray_r' ; tmin=-0.3 ;  tmax=0.3   ;  df = 0.05 ; l_apply_lap = True
    #cpal_fld = 'bone_r' ; tmin=-0.9 ;  tmax=-tmin   ;  df = 0.05 ; l_apply_lap = True ; l_pow_field = True ; pow_field = 2.
    cunit = r'SSH (m)'
    cb_jump = 1

if cv_in == 'socurloverf':
    cfield = 'RV'
    cpal_fld = 'on2' ; tmin=-1. ;  tmax=1. ;  df = 0.05 ; l_apply_lap = False
    cunit = ''
    cb_jump = 1



else:
    print 'ERROR: we do not know cv!'
    sys.exit(0)



    

if l_do_ice: bt.chck4f(cf_ice)

bt.chck4f(cf_lsm)
bt.chck4f(cf_in)
id_fld = Dataset(cf_in)
vtime = id_fld.variables['time_counter'][:]
id_fld.close()
Nt = len(vtime)

if l_show_lsm or l_apply_lap:
    bt.chck4f(cf_lsm)
    id_lsm = Dataset(cf_lsm)
    nb_dim = len(id_lsm.variables['tmask'].dimensions)
    print ' The mesh_mask has '+str(nb_dim)+' dimmensions!'
    if l_show_lsm:
        if nb_dim==4: XMSK  = id_lsm.variables['tmask'][0,0,j1:j2,i1:i2]
        if nb_dim==3: XMSK  = id_lsm.variables['tmask'][0,j1:j2,i1:i2]
        if nb_dim==2: XMSK  = id_lsm.variables['tmask'][j1:j2,i1:i2]
        (nj,ni) = nmp.shape(XMSK)
    if l_apply_lap:
        XE1T2 = id_lsm.variables['e1t'][0,j1:j2,i1:i2]
        XE2T2 = id_lsm.variables['e2t'][0,j1:j2,i1:i2]
        (nj,ni) = nmp.shape(XE1T2)
        XE1T2 = XE1T2*XE1T2
        XE2T2 = XE2T2*XE2T2
        id_lsm.close()

    print 'Shape Arrays => ni,nj =', ni,nj
    
    print 'Done!\n'

    
if l_show_lsm: pmsk = nmp.ma.masked_where(XMSK[:,:] > 0.2, XMSK[:,:]*0.+40.)



params = { 'font.family':'Helvetica Neue',
           'font.weight':    'normal',
           'font.size':       int(9.*font_rat),
           'legend.fontsize': int(9.*font_rat),
           'xtick.labelsize': int(9.*font_rat),
           'ytick.labelsize': int(9.*font_rat),
           'axes.labelsize':  int(9.*font_rat) }
mpl.rcParams.update(params)
cfont_clb  = { 'fontname':'Helvetica Neue', 'fontweight':'medium', 'fontsize':int(8.*font_rat), 'color':'w'}
cfont_clock = { 'fontname':'Ubuntu Mono', 'fontweight':'normal', 'fontsize':int(10.*font_rat), 'color':'w' }
cfont_mail = { 'fontname':'Times New Roman', 'fontweight':'normal', 'fontstyle':'italic', 'fontsize':int(14.*font_rat), 'color':'0.8'}
cfont_titl = { 'fontname':'Helvetica Neue', 'fontweight':'light', 'fontsize':int(30.*font_rat), 'color':'w' }


# Colormaps for fields:
pal_fld = bcm.chose_colmap(cpal_fld)
if l_log_field:
    norm_fld = colors.LogNorm(  vmin = tmin, vmax = tmax, clip = False)
if l_pow_field:
    norm_fld = colors.PowerNorm(gamma=pow_field, vmin = tmin, vmax = tmax, clip = False)
else:
    norm_fld = colors.Normalize(vmin = tmin, vmax = tmax, clip = False)


if l_show_lsm:
    pal_lsm = bcm.chose_colmap('land_dark')
    norm_lsm = colors.Normalize(vmin = 0., vmax = 1., clip = False)

if l_do_ice:
    pal_ice = bcm.chose_colmap(cpal_ice)
    norm_ice = colors.Normalize(vmin = rmin_ice, vmax = 1, clip = False)



if cdt == '3h':
    dt = 3
elif cdt == '1h':
    dt = 1
else:
    print 'ERROR: unknown dt!'


rw_img = rw_fig*float(dpi)
rh_img = rw_fig*yx_ratio*float(dpi)    
print ' *** Forecasted dimension of image =>', rw_img , rh_img,'\n'



ntpd = 24/dt


vm = vmn
if isleap(int(cyr0)): vm = vml
#print ' year is ', vm, nmp.sum(vm)

jd = int(cdd0) - 1
jm = int(cmn0)

for jt in range(jt0,Nt):

    jh = (jt*dt)%24
    jdc = (jt*dt)/24 + 1

    if jt%ntpd == 0: jd = jd + 1

    if jd == vm[jm-1]+1 and (jt)%ntpd == 0 :
        jd = 1
        jm = jm + 1

    ch = '%2.2i'%(jh)
    #cdc= '%3.3i'%(jdc)
    cd = '%3.3i'%(jd)
    cm = '%2.2i'%(jm)

    #print '\n\n *** jt, ch, cd, cm =>', jt, ch, cd, cm


    ct = str(datetime.datetime.strptime(cyr0+'-'+cm+'-'+cd+' '+ch, '%Y-%m-%j %H'))
    ct=ct[:5]+cm+ct[7:] #lolo bug !!! need to do that to get the month and not "01"
    print ' ct = ', ct
    cday  = ct[:10]   ; print ' *** cday  :', cday
    chour = ct[11:13] ; print ' *** chour :', chour



    cfig = 'figs/'+cv_in+'_NEMO_'+CNEMO+'_'+cbox+'_'+cday+'_'+chour+'_'+cpal_fld+'.'+fig_type

    ###### FIGURE ##############
    
    fig = plt.figure(num = 1, figsize=(rw_fig, rh_fig), dpi=None, facecolor='w', edgecolor='0.5')

    ax  = plt.axes([0., 0., 1., 1.], axisbg = '0.5')

    vc_fld = nmp.arange(tmin, tmax + df, df)


    print "Reading record #"+str(jt)+" of "+cv_in+" in "+cf_in
    id_fld = Dataset(cf_in)
    XFLD  = id_fld.variables[cv_in][jt,j1:j2,i1:i2] ; # t, y, x
    id_fld.close()
    print "Done!"

    if l_apply_lap:
        lx = nmp.zeros((nj,ni))
        ly = nmp.zeros((nj,ni))
        lx[:,1:ni-1] = 1.E9*(XFLD[:,2:ni] -2.*XFLD[:,1:ni-1] + XFLD[:,0:ni-2])/XE1T2[:,1:ni-1]
        ly[1:nj-1,:] = 1.E9*(XFLD[2:nj,:] -2.*XFLD[1:nj-1,:] + XFLD[0:nj-2,:])/XE2T2[1:nj-1,:]
        XFLD[:,:] = lx[:,:] + ly[:,:]
        del lx, ly

    if not l_show_lsm and jt == jt0: ( nj , ni ) = nmp.shape(XFLD)
    print '  *** dimension of array => ', ni, nj

    print "Ploting"
    cf = plt.imshow(XFLD[:,:], cmap = pal_fld, norm = norm_fld, interpolation='none')
    del XFLD

    # Ice
    if not cfield == 'MLD' and l_do_ice:
        print "Reading record #"+str(jt)+" of "+cv_ice+" in "+cf_ice
        id_ice = Dataset(cf_ice)
        XICE  = id_ice.variables[cv_ice][jt,:,:] ; # t, y, x
        id_ice.close()
        print "Done!"

        #XM[:,:] = XMSK[:,:]
        #bt.drown(XICE, XM, k_ew=2, nb_max_inc=10, nb_smooth=10)
        #ci = plt.contourf(XICE[:,:], vcont_ice, cmap = pal_ice, norm = norm_ice) #

        pice = nmp.ma.masked_where(XICE < rmin_ice, XICE)
        ci = plt.imshow(pice, cmap = pal_ice, norm = norm_ice, interpolation='none') ; del pice, ci
        del XICE


    if l_show_lsm: cm = plt.imshow(pmsk, cmap = pal_lsm, norm = norm_lsm, interpolation='none')

    plt.axis([ 0, ni, 0, nj])

    #plt.title('NEMO: '+cfield+', coupled '+CNEMO+', '+cday+' '+chour+':00', **cfont_title)



    if l_show_cb:
        color_top='w'
        ax2 = plt.axes(vcb)
        clb = mpl.colorbar.ColorbarBase(ax2, ticks=vc_fld, cmap=pal_fld, norm=norm_fld, orientation='horizontal', extend='both')
        if cb_jump > 1:
            cb_labs = [] ; cpt = 0
            for rr in vc_fld:
                if cpt % cb_jump == 0:
                    if df >= 1.: cb_labs.append(str(int(rr)))
                    if df <  1.: cb_labs.append(str(rr))
                else:
                    cb_labs.append(' ')
                    cpt = cpt + 1
                    clb.ax.set_xticklabels(cb_labs, **cfont_clb)
                    clb.set_label(cunit, **cfont_clb)
                    clb.ax.yaxis.set_tick_params(color=color_top) ; # set colorbar tick color
                    clb.outline.set_edgecolor(color_top) ; # set colorbar edgecolor
                    plt.setp(plt.getp(clb.ax.axes, 'xticklabels'), color=color_top) ; # set colorbar ticklabels

    del cf





    if l_show_clock:
        xl = float(x_clock)/rfact_zoom
        yl = float(y_clock)/rfact_zoom
        ax.annotate('Date: '+cday+' '+chour+':00', xy=(1, 4), xytext=(xl,yl), **cfont_clock)

    #ax.annotate('laurent.brodeau@ocean-next.fr', xy=(1, 4), xytext=(xl+150, 20), **cfont_mail)

    if l_annotate_name:
        xl = float(nxr)/20./rfact_zoom
        yl = float(nyr)/1.33/rfact_zoom
        ax.annotate(CNEMO, xy=(1, 4), xytext=(xl, yl), **cfont_titl)

    if l_add_logo:
        datafile = cbook.get_sample_data(cf_logo, asfileobj=False)
        im = image.imread(datafile)
        #im[:, :, -1] = 0.5  # set the alpha channel
        fig.figimage(im, x_logo, y_logo, zorder=9)
                

    plt.savefig(cfig, dpi=dpi, orientation='portrait', facecolor='k')
    print cfig+' created!\n'
    plt.close(1)


    del cm, fig, ax
    if l_show_cb: del clb
