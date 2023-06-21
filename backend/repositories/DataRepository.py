from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.method != 'GET' and request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens


    # @staticmethod
    # def update_status_alle_lampen(status):
    #     sql = "UPDATE lampen SET status = %s"
    #     params = [status]
    #     return Database.execute_sql(sql, params)

    @staticmethod
    def create_log(deviceid, rideid, value, actionid):
        sql = 'INSERT INTO history (deviceid, rideid, value, actionid) VALUES (%s, %s, %s, %s)'

        params = [deviceid, rideid, value, actionid]

        return Database.execute_sql(sql, params)
    
    @staticmethod
    def create_ride():
        sql = 'INSERT INTO ride VALUES ()'
        return Database.execute_sql(sql)
    
    @staticmethod
    def update_ride(rideid, name, distance, max_speed, avg_speed, max_amb_temp, avg_amb_temp, max_eng_temp, avg_eng_temp, start_location, stop_location, max_tilt, min_tilt, max_accel, min_accel):
        sql = 'UPDATE ride SET name = %s,  distance = %s, stop_time = CURRENT_TIMESTAMP(), max_speed =%s, avg_speed =%s, max_amb_temp =%s, avg_amb_temp =%s, max_eng_temp =%s, avg_eng_temp =%s, start_location =%s, stop_location=%s, max_left_tilt=%s, max_right_tilt=%s, max_accel=%s, min_accel=%s WHERE id = %s'
        param = [name, distance, max_speed, avg_speed, max_amb_temp, avg_amb_temp, max_eng_temp, avg_eng_temp, start_location, stop_location, max_tilt, min_tilt, max_accel, min_accel, rideid]
        return Database.execute_sql(sql, param)
    
    @staticmethod
    def get_rides():
        sql = "SELECT *, date_format(start_time, '%H:%i | %d/%m/%Y') AS formatted_start_time FROM motorsysteem.ride order by id desc"
        return Database.get_rows(sql)
    
    @staticmethod
    def get_ride_by_id(rideid):
        sql = "SELECT *, date_format(start_time, '%H:%i | %d/%m/%Y') AS formatted_start_time FROM ride where id = %s"
        param = [rideid]
        return Database.get_one_row(sql, param)
    
    @staticmethod
    def get_total_distance():
        sql = "SELECT sum(distance) as distance FROM ride"
        return Database.get_one_row(sql)
    
    @staticmethod
    def get_speeds_by_rideid(rideid):
        sql = "SELECT max(value) ,avg(value) FROM history where deviceid = 5 and rideid = %s"
        param = [rideid]
        return Database.get_one_row(sql, param)
    
    @staticmethod
    def get_amb_temp_by_rideid(rideid):
        sql = "SELECT max(value) ,avg(value) FROM history where deviceid = 7 and rideid = %s"
        param = [rideid]
        return Database.get_one_row(sql, param)
    
    @staticmethod
    def get_eng_temp_by_rideid(rideid):
        sql = "SELECT max(value) ,avg(value) FROM history where deviceid = 6 and rideid = %s"
        param = [rideid]
        return Database.get_one_row(sql, param)
    
    @staticmethod
    def get_accel_by_rideid(rideid):
        sql = "SELECT max(value) ,min(value) FROM history where deviceid = 1 and rideid = %s"
        param = [rideid]
        return Database.get_one_row(sql, param)
    
    @staticmethod
    def get_tilt_by_rideid(rideid):
        sql = "SELECT min(value), max(value) FROM motorsysteem.history where deviceid = 2 and rideid = %s"
        param = [rideid]
        return Database.get_one_row(sql, param)
    
    @staticmethod
    def get_start_location_by_rideid(rideid):
        sql = "SELECT value FROM motorsysteem.history where deviceid = 4 and rideid = %s order by time asc limit 1"
        param = [rideid]
        return Database.get_one_row(sql, param)
    
    @staticmethod
    def get_stop_location_by_rideid(rideid):
        sql = "SELECT value FROM motorsysteem.history where deviceid = 4 and rideid = %s order by time desc limit 1"
        param = [rideid]
        return Database.get_one_row(sql, param)

    @staticmethod
    def get_locations_by_rideid(rideid):
        sql = "SELECT * FROM history where rideid = %s and deviceid = 4 and value != 0"
        param = [rideid]
        return Database.get_rows(sql,param)