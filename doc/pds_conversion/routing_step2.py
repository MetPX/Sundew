import os,sys,re,string

# EXTRACTING ALL FILENAMES AND THEIR CLIENTS

# ---------------------------------------------------
# read in the log
# ---------------------------------------------------

f=open(sys.argv[1],'rb')
data=f.readlines()
f.close()

for l in data :

    if len(l) <= 0 :
       print(" empty line ??? %s " % l)
       continue

    parts    = l.split()
    if len(parts) != 2 :
       print(" parts != 2 ??? %s " % l)
       continue

    filename = parts[0]
    clients  = parts[1]
    fparts   = filename.split(':')

    # :20070409000009 trailing get rid of it
    if fparts[-1][:2] == '20' and len(fparts[-1]) == 14 :
       fparts = fparts[:-1]

    # '::' trailing get rid of it
    if fparts[-1] == '' :
       fparts = fparts[:-1]

    # SENDER part replace by .*
    if fparts[-1][:6] == 'SENDER' :
       fparts = fparts[:-1]
       fparts[-1] = fparts[-1] + '.*'

    # remove trailing .tmp
    if fparts[-1][-4:] == '.tmp' :
       fparts[-1] = fparts[-1][:-4]

    # AIRNOW : 20070409_0000_aq.txt:AQ:CAPMON:AIRNOW:ASCII::20070409001013
    if fparts[3] == 'AIRNOW' :
       fparts[0] = '.*'

    # ACC :  ACC-FQ21QX8608230437:barographe:CMQ:BULLETIN:ASCII::20070409000019
    if fparts[3] == 'BULLETIN' and fparts[0][:4] == 'ACC-' :
       name = fparts[0]
       fparts[0] = name[:10] + '.*'

    # GRIB : 2007.04.09.00Z.006.gem_cmc.grb:CASTOR:CMC:GRIB:BIN::20070409045947:pds1
    if fparts[3] == 'GRIB' :
       nparts = fparts[0].split('.')
       if len(nparts) == 7 and nparts[5] == 'gem_cmc' :
          fparts[0] = '.*.gem_cmc.grb'

    # HRPT : replace datetime parts by .*  noaa-15_20070408_2356_46283_weg_raw.gz:HRPT:WEG:RAW:BIN
    if fparts[1] == 'HRPT' and fparts[3] == 'RAW' and fparts[4] == 'BIN' :
       nparts = fparts[0].split('_')
       fparts[0] = nparts[0] + '.*'

    # 20070409_whx.txt:HRPT:WHX:RAW:TXT
    if fparts[1] == 'HRPT' and fparts[3] == 'RAW' and fparts[4] == 'TXT' :
       nparts = fparts[0].split('_')
       fparts[0] = '.*' + nparts[1]

    # W8510P_WEG_can_NIR_O_HRPTN18_70_0N_100_0W_2328z070409_V5_22:HRPT:WEG:PHOTO:GIF
    if fparts[1] == 'HRPT' and fparts[3] == 'PHOTO' :
       nparts = fparts[0].split('_')
       for i,np in enumerate(nparts) :
           if len(np) == 11 and np[4] == 'z' :
              nparts[i] = '.*'
              break
       fparts[0] = '_'.join(nparts) 

    # FOTO_A3100P_CMC_ATL_WV_O_GOES-12_GW_0045z070409_GW:GOES:CMC:PHOTO:GIF 
    if fparts[1] == 'GOES' and fparts[2] == 'CMC' and ( fparts[3] == 'PHOTO' or fparts[3] == 'SPECIAL' ) :
       nparts = fparts[0].split('_')
       for i,np in enumerate(nparts) :
           if len(np) == 11 and np[4] == 'z' :
              nparts[i] = '.*'
              break
       fparts[0] = '_'.join(nparts) 

    # LGFZVR41___200704091500_0000_200704091445.PNG:EDIGRAF:WEG:IMAGE:PNG
    if fparts[0][:3] == 'LGF' and fparts[1] == 'EDIGRAF' :
       nparts = fparts[0].split('_')
       fparts[0] = nparts[0] + '.*'

    # RVAS_BBC_FULL_20070409_0000_N.JPEG:RVAS:YVR:RVAS:JPEG
    if fparts[0][:4] == 'RVAS' and fparts[1] == 'RVAS' :
       nparts = fparts[0].split('_')
       fparts[0] = '_'.join(nparts[:3]) + '.*'

    # SCRIBE.FPHX57.04.09.19Z_12Z.g:SCRIBE:HX:METEOCODE:ASCII
    # TRANSMIT.FPHX51.04.09.19Z.1855:SCRIBE:HX:METEOCODE:ASCII 
    if fparts[1] == 'SCRIBE' and fparts[3] == 'METEOCODE' and fparts[4] == 'ASCII' :
       nparts = fparts[0].split('.')
       fparts[0] = '.'.join(nparts[:2]) + '.*'

    # SCRIBE.MARINE.04.09.00Z.g.Z:CASTOR:CMC:SCRIBE:G1SCBXM
    if fparts[1] == 'CASTOR' and fparts[2] == 'CMC' and fparts[3] == 'SCRIBE' :
       nparts = fparts[0].split('.')
       fparts[0] = '.'.join(nparts[:2]) + '.*' 

    #CFH03.09015002:RCIS:RAW:CHART:METSIS
    if fparts[1] == 'RCIS' and fparts[2] == 'RAW' and fparts[3] == 'CHART' and fparts[4] == 'METSIS' :
       nparts = fparts[0].split('.')
       fparts[0] = nparts[0] + '.*' 

    # 200704090100~PRECIP_NUMERIC~PRECIP,125,18,MPRATE:URP:XTI_NUMERIC:RADAR:NUMERIC
    if fparts[1] == 'URP' :
       name = fparts[0]
       if name[:2] == '20' :
          name = name[12:]
          fparts[0] = '.*' + name

    # WEBPRODS : 
    if fparts[3] == 'WEBPRODS' or fparts[3] == 'WEBPRODS_DEV' :
       if fparts[1][:9]  == 'analysis+'       : fparts[0] = '.*'
       if fparts[1][:8]  == 'chronos+'        : fparts[0] = '.*'
       if fparts[1][:4]  == 'eer+'            : fparts[0] = '.*'
       if fparts[1][:9]  == 'ensemble+'       : fparts[0] = '.*'
       if fparts[1][:8]  == 'saisons+'        : fparts[0] = '.*'
       if fparts[1][:10] == 'satellite+'      : fparts[0] = '.*'
       if fparts[1][:15] == 'model_forecast+' : fparts[0] = '.*'
       if fparts[1][-8:] == '+chronos'        : fparts[0] = '.*'
       if fparts[1][-3:] == '+nc'             : fparts[0] = '.*'
       if fparts[1][-4:] == '+wam'            : fparts[0] = '.*'
       if fparts[1][-4:] == '+lam'            : fparts[0] = '.*'

       if fparts[1][-6:] == 'global'         : 
          #t=fparts[0].replace('_054_G1_afghan_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_afghan_.*'
          #t=fparts[0].replace('_054_G1_canada_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_canada_.*'
          #t=fparts[0].replace('_054_G1_canad#ian@arctic@east_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_canadian@arctic@east_.*'
          #t=fparts[0].replace('_054_G1_canad#ian@arctic@west_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_canadian@arctic@west_.*'
          #t=fparts[0].replace('_054_G1_centrecan_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_centrecan_.*'
          #t=fparts[0].replace('_054_G1_east@coast@zoom_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_east@coast@zoom_.*'
          #t=fparts[0].replace('_054_G1_east_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_east_.*'
          #t=fparts[0].replace('_054_G1_ecoast_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_ecoast_.*'
          #t=fparts[0].replace('_054_G1_north@amer#ica_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_north@america_.*'
          #t=fparts[0].replace('_054_G1_npole_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_npole_.*'
          #t=fparts[0].replace('_054_G1_west_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_G1_west_.*'

          t1=fparts[0].replace('_054_G1_north@america@zoomout_I_4PAN_CLASSIC@012','')
          if t1 != fparts[0] : 
             fparts[0] = '.*' + fparts[0][11:]
          else :
             fparts[0] = '.*'

       if fparts[1][-8:] == 'regional'         : 
          #t=fparts[0].replace('_054_R1_canada_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_canada_.*'
          #t=fparts[0].replace('_054_R1_canad#ian@arctic@east_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_canadian@arctic@east_.*'
          #t=fparts[0].replace('_054_R1_canad#ian@arctic@west_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_canadian@arctic@west_.*'
          #t=fparts[0].replace('_054_R1_canada@asep_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_canada@asep_.*'
          #t=fparts[0].replace('_054_R1_centrecan_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_centrecan_.*'
          #t=fparts[0].replace('_054_R1_east_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_east_.*'
          #t=fparts[0].replace('_054_R1_east@coast@zoom_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_east@coast@zoom_.*'
          #t=fparts[0].replace('_054_R1_ecoast_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_ecoast_.*'
          #t=fparts[0].replace('_054_R1_lam@alberta_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_lam@alberta_.*'
          #t=fparts[0].replace('_054_R1_lam@east_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_lam@east_.*'
          #t=fparts[0].replace('_054_R1_lam@west_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_lam@west_.*'
          #t=fparts[0].replace('_054_R1_north@amer#ica@astro_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_north@america@astro_.*'
          #t=fparts[0].replace('_054_R1_north@amer#ica@northeast_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_north@america@northeast_.*'
          #t=fparts[0].replace('_054_R1_north@amer#ica@northwest_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_north@america@northwest_.*'
          #t=fparts[0].replace('_054_R1_north@amer#ica@southeast_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_north@america@southeast_.*'
          #t=fparts[0].replace('_054_R1_north@amer#ica@southwest_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_north@america@southwest_.*'
          #t=fparts[0].replace('_054_R1_west_','')
          #if #t != fparts[0] : fparts[0] = '.*_054_R1_west_.*'

          t1=fparts[0].replace('_054_R1_north@america_I_4PAN_CLASSIC@012','')
          t2=fparts[0].replace('_054_R1_north@america_I_QPFTYPES_t6','')
          t3=fparts[0].replace('_054_R1_canada_I_AQ_','')

          if t1 != fparts[0] or t2 != fparts[0] or t3 != fparts[0] : 
             fparts[0] = '.*' + fparts[0][11:]
          else :
	     fparts[0] = '.*'

    filename = ':'.join(fparts)
    print("%s %s" % (filename,clients) )
