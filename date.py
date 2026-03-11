from datetime import datetime

def format_trans_time(trans_time):

    if not trans_time or trans_time.lower() == "None":
        return trans_time

    try:
        formatted_time = datetime.strptime(trans_time, '%Y%m%d%H%M%S').strftime('%H:%M:%S %d-%m-%Y')
        return formatted_time
    except ValueError:
        return trans_time
    
