import requests
import decimal

class Logger(object):
    def __init__(self, driver):
        self.screen_name = driver

    def lap(self, lap):
        pass

    def delta(self, delta):
        pass

    def position(self, x, y):
        pass

class RacingLeagueCharts(Logger):
    def __init__(self, driver, status_bar, local_mode):
        super(RacingLeagueCharts, self).__init__(driver)
        self.session_id = 0
        self.status_bar = status_bar
        self.log = []
        self.local_mode = local_mode

        self.session_url = 'https://racingleaguecharts.com/sessions/register'
        self.lap_url = 'https://racingleaguecharts.com/laps'

    def update_status(self, lap_time = False):
        if lap_time:
            msg = 'Session id: {0}, Last lap: {1}'.format(self.session_id, self.format_time(lap_time))
        else:
            msg = 'Session id: {0}'.format(self.session_id)

        self.status_bar.SetStatusText(msg)

    def add_log_entry(self, msg):
        self.log.append(msg)

    def request_session(self, packet):
        if self.local_mode:
            return True
        self.add_log_entry('New session requested')
        track_length = decimal.Decimal(packet.track_length)
        payload = { "driver": self.screen_name, "track": round(track_length, 3), "type": packet.session_type }
        r = requests.post(self.session_url, data = payload, verify = False)
        if r.status_code == 200:
            self.session_id = r.json()['session_id']
            self.update_status()
            self.add_log_entry("Session id: {0}".format(self.session_id))
            return True
        return False

    def send_sector(self, sector):
        print sector.sector_number, sector.sector_time

    def lap(self, lap):
        raw_times, formatted_times = self.format_lap_times(lap)
        self.add_log_entry("Lap: {0:02d} {1} {2} {3} {4}".format(int(lap.lap_number), formatted_times['total'], formatted_times['s1'], formatted_times['s2'], formatted_times['s3']))
        if self.local_mode:
            return True
        payload = {
            "session_id": self.session_id, "lap_number": lap.lap_number,
            "sector_1": raw_times['s1'], "sector_2": raw_times['s2'], "sector_3": raw_times['s3'], "total": raw_times['total'],
            "speed": lap.top_speed, "fuel": lap.current_fuel, "position": lap.position }
        r = requests.post(self.lap_url, data = payload, verify = False)
        if r.status_code == 200:
            self.update_status(lap.lap_time)
            return True
        return False

    def format_time(self, seconds):
        m, s = divmod(seconds, 60)
        if m > 0:
            return '{0:.0f}:{1:06.3f}'.format(m, s)
        else:
            return '{0:06.3f}'.format(s)

    def format_lap_times(self, lap):
        if lap.sector_1:
            s1 = round(decimal.Decimal(lap.sector_1), 3)
        else:
            s1 = 0

        if lap.sector_2:
            s2 = round(decimal.Decimal(lap.sector_2), 3)
        else:
            s2 = 0

        if lap.lap_time:
            total = round(decimal.Decimal(lap.lap_time), 3)
            s3 = round(decimal.Decimal(total - s2 - s1), 3)
        else:
            total = 0
            s3 = 0

        fs1 = self.format_time(s1)
        fs2 = self.format_time(s2)
        fs3 = self.format_time(s3)
        fst = self.format_time(total)

        return [{"s1": s1, "s2": s2, "s3": s3, "total": total}, {"s1": fs1, "s2": fs2, "s3": fs3, "total": fst}]
