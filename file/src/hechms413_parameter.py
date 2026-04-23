# https://github.com/rcfdtools
# Geometric properties calculator, .gage and .met sentences generator
# This script has to be run in QGIS 3+
# Subbasin layer and CN map has to use the same projection system
# Before run set Settings / Options / Processing / General / Invalid features filtering / Do not filter

import processing
from qgis.core import QgsRasterLayer, QgsVectorLayer

# General parameters
main_path = 'D:/R.TSIG/file/hec/HECHMS_v0/'
subbasin_path = main_path+'shp/ArroyoElZorroCuencasTest.shp' # ● Subbasin shapefile exported from HEC-HMS
cn_path = main_path+'grid/CNII_v1.tif' # ● CN grid map
cn_prefix = 'CNII_' # ● CN prefix for statistical fields
total_gages = 39 # ● Gages correspond with the number of subbasins for PMax24h
subbasin_prefix = 'W' # ● Subbasin prefix assigned in HEC-HMS
# HEC-DSS database file parameters assigned for time series records
dss_file_name = 'HECHMS_v0.dss' # ● Your HEC-DSS database file
path_a = 'ArroyoElZorro' # ● Basin name
path_f = 'P_TR2.33_6h_FSCalif057' # ● Hyetograph
start_time = '1 January 2004, 06:00' # ● Start time
end_time = '6 January 2004, 06:00' # ● End time
output_file = main_path+'table/'+path_a+'CuencasCN.csv'
new_field_list = ['Akm2', # Subbasin area
                  'Pkm', # Subbasin perimeter
                  'APD', #Area Percentual Distribution
                  'ReachLTkm', # Subbasin total river length
                  'LagTimeSCS' # Lag time for Parameters / Transform / SCS Unit Hydrograph
                  ]


# Geometric properties calculation
print('****************************************\nGeometric properties and CN statistics\n****************************************\n')
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
    print(f'Total area (km²): {total_area}')
    
    # Perimeter calculator
    field_index = layer.fields().indexOf('Pkm')
    for feature in layer.getFeatures():
        fid = feature.id()
        geom = feature.geometry()
        perimeter = geom.length()/1000
        layer.changeAttributeValue(fid, field_index, perimeter)
    
    # Area Percentual Distribution - ADP calculator
    field_index = layer.fields().indexOf('APD')
    for feature in layer.getFeatures():
        fid = feature.id()
        areadp = (feature[layer.fields().indexFromName('Akm2')] / total_area) * 100
        layer.changeAttributeValue(fid, field_index, areadp) 
    
    # Subbasin total river length = "Akm2" * "drain_den" / 1000
    total_river_length = 0.0
    field_index = layer.fields().indexOf('ReachLTkm')
    for feature in layer.getFeatures():
        fid = feature.id()
        reachltkm = feature[layer.fields().indexFromName('Akm2')] * 1000000 * feature[layer.fields().indexFromName('drain_den')] / 1000
        total_river_length += reachltkm
        layer.changeAttributeValue(fid, field_index, reachltkm)    
    print(f'Total river length (km): {total_river_length}')        

else:
    print('Please use a valid polygon layer')
layer.commitChanges()


# CN zonal statistics
print(f'CN map stats: {output_file}\n')
alg_params = {
    'COLUMN_PREFIX': cn_prefix,
    'INPUT': subbasin_path,
    'INPUT_RASTER': cn_path,
    'RASTER_BAND': 1,
    'STATISTICS': [0,2,4],  # 0-Count,1-Sum,2-Mean,3-Median,4-Standard deviation,5-Minimum,6-Maximum,7-Range,8-Minority (least common value),9-Majority (most common value),10-Variety (unique value count),11-Variance
    'OUTPUT': output_file
}
processing.run('native:zonalstatisticsfb', alg_params)


'''

    # Subbasin LagTIme = 0.6*(0.0526*("long_len"/0.3048)^0.8*((1000/ "CNII_mean")-9)^0.7*("basin_slo"*100)^-0.5)
    mean_lagtime = 0.0
    field_index = layer.fields().indexOf('LagTimeSCS')
    for feature in layer.getFeatures():
        fid = feature.id()
        lagtimescs = 0.6*(0.0526*(feature[layer.fields().indexFromName('long_len')]/0.3048)**0.8*((1000/feature[layer.fields().indexFromName('CNII_mean')])-9)**0.7)
        mean_lagtime += lagtimescs
        layer.changeAttributeValue(fid, field_index, lagtimescs)    
    print(f'Mean LagTimeSCS (minutes): {mean_lagtime / total_gages}')  

'''


# .gage file sentences
print('****************************************\n.gage file sentences\n****************************************\n')
for i in range(total_gages):
    print(f'Gage: {subbasin_prefix}{i+1}\n     Gage: {subbasin_prefix}{i+1}\n     Gage Type: Precipitation\n     Last Modified Date: 01 January 2026\n     Last Modified Time: 06:00:00\n     Reference Height Units: Meters\n     Reference Height: 9.9999\n     Data Source Type: External DSS\n     Filename: {dss_file_name}\n     Pathname: /{path_a}/{subbasin_prefix}{i+1}/PRECIP-INC//15Minute/{path_f}/\n     Variant: Variant-1\n       Start Time: {start_time}\n       End Time: {end_time}\n     End Variant: Variant-1\nEnd:\n')

# .met file sentences
print('\n****************************************\n.met file sentences\n****************************************\n')
for i in range(total_gages):
    print(f'Subbasin: {subbasin_prefix}{i+1}\n     Last Modified Date: 01 January 2026\n     Last Modified Time: 06:00:00\n     Gage: W{i+1}\nEnd:\n')

