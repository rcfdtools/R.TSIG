# https://github.com/rcfdtools/R.TSIG
# Calculate the hipotetical stations year length
# This script has to be loaded in QGIS into a Field Calculator function
# Call function for full length (Field LYearS): len_year_serie("FECHA_INST", "FECHA_SUSP")[0]
# Call function for an specified time period (Field LYearSTW): len_year_serie("FECHA_INST", "FECHA_SUSP")[1]
# You must set in the Panel de Control / Region, short dates as d/MM/yyyy.
# Tested in QGIS 3.44.6

from qgis.core import *
from qgis.gui import *
from datetime import date
from PyQt5.QtCore import QDate

@qgsfunction(group='_TSIG', referenced_columns=[])
def len_year_serie(installation_date, suspension_date):
    date_format = '%d/%m/%Y'
    #tw_start_date = datetime.strptime('01/01/1980', date_format) # Time-window start. Use '' for set 01/01/1900
    #tw_end_date = datetime.strptime('31/12/2023', date_format) # Time-window end. Use '' for use the current date and prevent over-time wrong suspension dates
    tw_start_date = QDate(1980, 1, 1)
    tw_end_date = QDate(2025, 12, 31)
    if not tw_start_date: tw_start_date = datetime.strptime('01/01/1900', date_format)
    if not tw_end_date: tw_end_date = str(datetime.today().date())
    if installation_date:
        if installation_date <= tw_start_date:
            tw_installation_date = tw_start_date
        else:
            tw_installation_date = installation_date
        if suspension_date:
            if suspension_date >= tw_end_date:
                tw_suspension_date = tw_end_date
            else:
                tw_suspension_date = suspension_date
            #diff_date = suspension_date - installation_date
            diff_date = installation_date.daysTo(suspension_date)
            #tw_diff_date = tw_suspension_date - tw_installation_date
            tw_diff_date = tw_installation_date.daysTo(tw_suspension_date)
        else:
            diff_date = tw_end_date - installation_date
            tw_diff_date = tw_end_date - tw_installation_date
        diff_date = float(diff_date)/365
        tw_diff_date = float(tw_diff_date)/365
        if diff_date < 0: diff_date = 0
        if tw_diff_date < 0: tw_diff_date = 0
    else:
        diff_date = 0
        tw_diff_date = 0
    return [diff_date, tw_diff_date] # First value is complete length. Second value is time window length
