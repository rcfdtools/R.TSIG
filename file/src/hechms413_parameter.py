# https://github.com/rcfdtools
# HEC-HMS 4.13 - Geometric properties calculator, .gage and .met sentences generator
# This script has to be run in QGIS 3+
# Subbasin layer and CN map has to use the same projection system
# Before run set Settings / Options / Processing / General / Invalid features filtering / Do not filter

import processing
from qgis.core import QgsRasterLayer, QgsVectorLayer
import pandas as pd
from math import pi


# General parameters
main_path = 'D:/R.TSIG/file/hec/HECHMS_v0/'
subbasin_path = main_path+'shp/ArroyoElZorroCuencasTest.shp' # ● Subbasin shapefile exported from HEC-HMS
cn_path = main_path+'grid/CNII_v1.tif' # ● Curve Number has to be always normal CNII grid map
total_gages = 39 # ● Gages correspond with the number of subbasins for PMax24h
cn_prefix = 'CNII_' # ● CN prefix for statistical fields
compute_tc_with_cn = 'CNII' # ● Compute ConcentrationTime Tc with curve number CNI-Dry, CNII-Normal or CNIII-Wet
subbasin_prefix = 'W' # ● Subbasin prefix assigned in HEC-HMS
# HEC-DSS database file parameters assigned for time series records
dss_file_name = 'HECHMS_v0.dss' # ● Your HEC-DSS database file
path_a = 'ArroyoElZorro' # ● Basin name
path_f = 'P_TR2.33_6h_FSCalif057' # ● Hyetograph
start_time = '1 January 2004, 06:00' # ● Start time
end_time = '6 January 2004, 06:00' # ● End time
lagtime_multiplier = 0.6
compute_tc_lt = True # Compute Concentration Time Tc and LagTime
create_hms_sentences = True # Create .gage and .met sentences
new_field_list = ['Akm2', # Subbasin area
                  'Pkm', # Subbasin perimeter
                  'APD', #Area Percentual Distribution
                  'ReachLTkm' # Subbasin total river length
                  ]
output_file = main_path+'table/'+path_a+'CuencasCN.csv' # ● Output .csv results file


# Geometric properties calculation
print('\n****************************************\nGeometric properties and CN statistics\n****************************************\n\nhttps://www.hec.usace.army.mil/confluence/hmsdocs/hmstrm/geographic-information-system-gis/basin-characteristics')
layer = QgsVectorLayer(subbasin_path, 'InputLayer', 'ogr')
if layer and layer.geometryType() == QgsWkbTypes.PolygonGeometry:
    
    # Delete existing fields
    for field in new_field_list:
        field_index = layer.fields().indexFromName(field)
        if field_index != -1:
            with edit(layer):
                 layer.dataProvider().deleteAttributes([field_index])
        layer.updateFields()
    
    # Create fields
    for field in new_field_list:
        layer.startEditing()
        layer.dataProvider().addAttributes([QgsField(field, QVariant.Double)])
    layer.commitChanges()
    layer.startEditing()
    
    # Area calculator
    total_area = 0.0
    field_index = layer.fields().indexOf('Akm2')
    for feature in layer.getFeatures():
        fid = feature.id()
        geom = feature.geometry()
        area = geom.area()/1000000 
        total_area += area
        layer.changeAttributeValue(fid, field_index, area)
    print(f'[Akm2] Total area (km²): {total_area}')
    
    # Perimeter calculator
    field_index = layer.fields().indexOf('Pkm')
    for feature in layer.getFeatures():
        fid = feature.id()
        geom = feature.geometry()
        perimeter = geom.length()/1000
        layer.changeAttributeValue(fid, field_index, perimeter)
    
    # Area Percentual Distribution - APD calculator
    field_index = layer.fields().indexOf('APD')
    total_apd = 0.0
    for feature in layer.getFeatures():
        fid = feature.id()
        apd = (feature[layer.fields().indexFromName('Akm2')] / total_area) * 100
        total_apd += apd
        layer.changeAttributeValue(fid, field_index, apd) 
    print(f'[APD] Area Percentual Distribution - APD (%): {total_apd}')
    
    # Subbasin total river length = "Akm2" * "drain_den" / 1000
    total_river_length = 0.0
    field_index = layer.fields().indexOf('ReachLTkm')
    for feature in layer.getFeatures():
        fid = feature.id()
        reachltkm = feature[layer.fields().indexFromName('Akm2')] * 1000000 * feature[layer.fields().indexFromName('drain_den')] / 1000
        total_river_length += reachltkm
        layer.changeAttributeValue(fid, field_index, reachltkm)    
    print(f'[ReachLTkm] Total river length (km): {total_river_length}')        
else:
    print('Please use a valid polygon layer')
layer.commitChanges()


# CN zonal statistics
alg_params = {
    'COLUMN_PREFIX': cn_prefix,
    'INPUT': subbasin_path,
    'INPUT_RASTER': cn_path,
    'RASTER_BAND': 1,
    'STATISTICS': [4,2],  # 0-Count,1-Sum,2-Mean,3-Median,4-Standard deviation,5-Minimum,6-Maximum,7-Range,8-Minority (least common value),9-Majority (most common value),10-Variety (unique value count),11-Variance
    'OUTPUT': output_file
}
processing.run('native:zonalstatisticsfb', alg_params)


# CNI, CNIII and Concentration time - Tc and LagTime
df = pd.read_csv(output_file, sep=',')
df.rename(columns={'CNII_mean': 'CNII'}, inplace=True)
# CNI & CNIII
df['CNI'] =  df['CNII'] / (2.3 - 0.013 * df['CNII'])
df['CNIII'] = df['CNII'] / (0.43 + 0.0057 * df['CNII'])
if compute_tc_lt:
    # Tc in hours
    print('Concentration time - Tc (hours)')
    print(f'[TcSCS] Soil Conservation Service - SCS (USDA): done with {compute_tc_with_cn}')
    df['TcSCS'] = (0.0526*(df['long_len']/0.3048)**0.8*((1000/ df[compute_tc_with_cn])-9)**0.7*(df['basin_slo']*100)**-0.5)/60
    print('TcPilgrim] Pilgrim: done')
    df['TcPilgrim'] = 0.76*(df['Akm2'])**0.38
    print('TcTemez] Témez: done')
    df['TcTemez'] =  0.30*((df['10_85_len']/1000)/(df['10_85_slo']**0.25))**0.76
    print('TcKirpich] Kirpich: done')
    df['TcKirpich'] = 0.00013*((df['10_85_len']/0.3048)**0.77/(df['10_85_slo']**0.385))
    print('TcGiandott] Giandotti: done')
    df['TcGiandott'] = (4*df['Akm2']**0.5+1.5*df['10_85_len']/1000)/(25.3*(df['10_85_slo']*df['10_85_len']/1000)**0.5)
    print('TcValenZul] Valencia y Zuluaga: done')
    df['TcValenZul'] = 1.7694*df['Akm2']**0.325*(df['10_85_len']/1000)**-0.096*(df['10_85_slo']*100)**-0.29
    print('[TcClark] Clark: done')
    df['TcClark'] = 0.335*(df['Akm2']/df['10_85_slo']**0.5)**0.593
    print('[TcJCross] Johnstone y Cross: done')
    df['TcJCross'] = 2.6*((df['10_85_len']/1000)/((df['10_85_slo']*1000)**0.5))**0.5
    print('[TcRanser] SCS – Ranser: done')
    df['TcRanser'] = 0.947*((df['10_85_len']/1000)**3/df['basin_rel'])**0.385
    print('[TcVentura] Ventura - Heras: done')
    df['TcVentura'] = 0.30*((df['10_85_len']/1000)/(df['10_85_slo']*100)**0.25)**0.75
    print('[TcVTChow] Ven Te Chow: done')
    df['TcVTChow'] = 0.273*((df['10_85_len']/1000)/(df['10_85_slo']**0.5))**0.64
    print('[TcUSArmyC] U.S. Army Corps: done')
    df['TcUSArmyC'] = 0.28*((df['10_85_len']/1000)/(df['10_85_slo']**0.25))**0.76
    print('[TcWilliams] Williams: done')
    df['TcWilliams'] = 0.683*((df['10_85_len']/1000)*(df['Akm2'])**0.40/((2*(df['Akm2']/pi)**0.5)*(df['10_85_slo']*100)**0.25))
    # LagTime in minutes
    a="df['LTSCS']"
    b="lagtime_multiplier * df['TcSCS'] * 60"
    df['LTSCS'] = lagtime_multiplier * df['TcSCS'] * 60
    df['LTPilgrim'] = lagtime_multiplier * df['TcPilgrim'] * 60
    df['LTTemez'] = lagtime_multiplier * df['TcTemez'] * 60  
    df['LTKirpich'] = lagtime_multiplier * df['TcKirpich'] * 60 
    df['LTGiandott'] = lagtime_multiplier * df['TcGiandott'] * 60
    df['LTValenZul'] = lagtime_multiplier * df['TcValenZul'] * 60 
    df['LTClark'] = lagtime_multiplier * df['TcClark'] * 60 
    df['LTJCross'] = lagtime_multiplier * df['TcJCross'] * 60 
    df['LTRanser'] = lagtime_multiplier * df['TcRanser'] * 60 
    df['LTVentura'] = lagtime_multiplier * df['TcVentura'] * 60 
    df['LTVTChow'] = lagtime_multiplier * df['TcVTChow'] * 60 
    df['LTUSArmyC'] = lagtime_multiplier * df['TcUSArmyC'] * 60 
    df['LTWilliams'] = lagtime_multiplier * df['TcWilliams'] * 60 
    print('LagTime - LT (minutes): done') 
df.to_csv(output_file, index=False)
df = df.sort_values(by='name')
df.index.name = 'FID'
#print(df.select_dtypes(include='number').agg(['mean', 'max', 'min', 'sum']))
stats = ['mean'] # 'sum', 'min', 'max'
print(f'Subbasin parameters: {output_file}')
for i in stats:
    print(f'\nStatistics: {i}')
    print(eval(f'df.{i}(numeric_only=True)'))


# Process .gage and .met file sentences 
if create_hms_sentences:
    # .gage file sentences
    print('****************************************\n.gage file sentences\n****************************************\n')
    for i in range(total_gages):
        print(f'Gage: {subbasin_prefix}{i+1}\n     Gage: {subbasin_prefix}{i+1}\n     Gage Type: Precipitation\n     Last Modified Date: 01 January 2026\n     Last Modified Time: 06:00:00\n     Reference Height Units: Meters\n     Reference Height: 9.9999\n     Data Source Type: External DSS\n     Filename: {dss_file_name}\n     Pathname: /{path_a}/{subbasin_prefix}{i+1}/PRECIP-INC//15Minute/{path_f}/\n     Variant: Variant-1\n       Start Time: {start_time}\n       End Time: {end_time}\n     End Variant: Variant-1\nEnd:\n')

    # .met file sentences
    print('\n****************************************\n.met file sentences\n****************************************\n')
    for i in range(total_gages):
        print(f'Subbasin: {subbasin_prefix}{i+1}\n     Last Modified Date: 01 January 2026\n     Last Modified Time: 06:00:00\n     Gage: W{i+1}\nEnd:\n')

print('Process completed...')