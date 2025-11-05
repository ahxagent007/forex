from common_functions import isNowInTimePeriod
import datetime as dt

def timming_test(start_hour, start_min, end_hour, end_min, current_time, skip_min):
    end_min = end_min + skip_min
    try:
        if end_min >= 60:
            end_hour += 1
            end_min -= 60
            if end_hour >= 24:
                end_hour = 0

        if isNowInTimePeriod(dt.time(start_hour, start_min), dt.time(end_hour, end_min), current_time):
            #print(symbol, 'TRADE SKIPPED for TIME MULTIPLE [',orders,']', json_file_name)
            print(True)
            return True
        else:
            None
    except Exception as e:
        print(e)

    print(False)
    return False



time_str = "23:58:30"
time_obj = dt.datetime.strptime(time_str, "%H:%M:%S").time()

last_h = 23
last_m = 58
timming_test(last_h,last_m,last_h,last_m,time_obj,2)