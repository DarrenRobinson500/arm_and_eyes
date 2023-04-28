from sql import *
from datetime import datetime, timedelta
now = datetime.now

# def db_write_model_run_log(model, date, run, epochs, time, map50, map95, folder):

# date = now()
# db_write_model_run_log("Ball", date, 15, "large", 200, 5.3, 0.9, 0.7)
#
result = db_read_model_run_log("Ball")
print(result)

n = 0.2221112
print("%.3f" % n)


# start = now() - timedelta(seconds=380)
# end = now()
# time = end - start
# print(round(time.seconds / 60,2))
# time = round((now() - start_time).seconds / 60, 2)

