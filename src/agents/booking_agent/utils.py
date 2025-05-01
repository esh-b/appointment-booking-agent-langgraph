import datetime
import pytz


def change_timezone_iso_dt(
		iso_dt_str: str,
		target_timezone: str) -> str:
	return datetime.datetime.fromisoformat(iso_dt_str).astimezone(pytz.timezone(target_timezone)).isoformat()
