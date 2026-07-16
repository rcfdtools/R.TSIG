# R.TSIG 


## References

* Calculate Flow Direction with the Native QGIS Tool and Style with Arrows https://www.youtube.com/watch?v=ttLxQBe0HIo
* How to run SAGA GIS tools in Python using PySAGA-cmd | Part 1: Introduction https://www.youtube.com/watch?v=1jH23CsRhmg
* [Convert e57 to las](https://lastools.github.io/download/): 
* Mapas de pronósticos de clima en https://www.ecmwf.int/en/forecasts


## Quiz 10 Balances hidrológico distribuido con QGIS (alpha version)

1. Con la herramienta GDAL / Raster Projections / Warp (reproject), reproyecte al CRS 9377 los raster suministrados y defina en Output file resolution in target georeferenced units una resolución exacta de 30x30m.
2. Con la herramienta Raster Analysis / Raster Calculator, calcule el caudal potencial de escurrimiento en m³/s, asigne el CRS 9377:
3. PotEscTurc.tif = (("pmedmaidw_a_2003@1"-"etr_turc_eci@1")/1000)*(30*30)/(365*24*60*60)
4. PotEscCeni.tif = (("pmedmaidw_a_2003@1"-"etr_cenicafe_eci@1")/1000)*(30*30)/(365*24*60*60)
5. Con la herramienta QGIS / Vector Conversion / Rasterize (A fixed value to burn: 1, Output raster size units: Georeferenced units, Width: 30, Height: 30, Output extent: DrenajeNatural9377.shp)
6. Con la herramienta SAGA / Tools / Terrain Analysis / Preprocessing / Fill Sinks (Wang & Liu) con Minimum Slope (Degree): 0.01 o desde QGIS / Raster Terrain Analysis / Fill Sinks (Wang & Liu), cree el mapa de direcciones de flujo. (usar el sinkfill.tif gerenado desde HEC-HMS 4.13 y reproyectado a 30x30m). Guarde como COP30_sinkfill_fdr_qgis.tif.
7. Con la herramienta SAGA / Tools / Terrain Analysis / Hydrology / Flow Accumulation (Top-Down)


ArroyoElZorroCuencasQmCenicafe.csv, columna QCenic_
ArroyoElZorroCuencasQmTurc.csv, columna QTurc_

Label = 'Cenicafe (m³/s): '  ||  round("ArroyoElZorroCuencasQmCenicafe_QCenic_sum", 3) ||  '\n'  || 'Cenicafe (m³/s): '  ||  round("ArroyoElZorroCuencasQmTurc_QTurc_sum", 3) 
