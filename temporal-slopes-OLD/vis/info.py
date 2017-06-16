import datetime

def temporal_slopes_info(process_seconds, sensors, start_year, end_year):
    """
    Print process information
    """
    process_time = str(datetime.timedelta(seconds=process_seconds))
        
    info_string = ('\nPROCESS_INFO:'
                    '\nProcess-Time : {}'
                    '\nDate-Range : {}-{}'
                    '\nSensors : {}\n'.format(process_time,
                                              start_year,
                                              end_year,
                                              sensors))                                                                      
    return info_string