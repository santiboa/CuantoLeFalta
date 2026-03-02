"""Shared countdown logic for Cuánto Le Falta bot."""
import datetime
from calendar import monthrange

import pytz

timezone = pytz.timezone("America/Mexico_City")

# Sexenio: Claudia Sheinbaum (Oct 1, 2024 - Oct 1, 2030)
end = timezone.localize(
    datetime.datetime(year=2030, month=10, day=1, hour=0, minute=0, second=0)
)
start = timezone.localize(
    datetime.datetime(year=2024, month=10, day=1, hour=0, minute=0, second=0)
)


def remaining_time() -> str:
    """Calculate and format the remaining time until end of sexenio."""
    now = datetime.datetime.now(timezone)
    diff_time = end - now

    if diff_time.total_seconds() <= 0:
        return "Ya acabó."

    sexenio = end - start
    elapsed_t = now - start

    elapsed_time_percent = (elapsed_t.total_seconds() / sexenio.total_seconds()) * 100
    elapsed_time_percent = f"{elapsed_time_percent:.3f}"
    elapsed_days = elapsed_t.days
    remaining_days = diff_time.days

    total_seconds = diff_time.total_seconds()
    total_hours = total_seconds // 3600
    minutes = round((total_seconds % 3600) // 60)
    seconds = round(total_seconds % 60)
    hours = int(total_hours % 24)

    years = remaining_days // 365
    months = ((end.year - now.year) * 12 + end.month - now.month - 1) % 12
    endday = monthrange(now.year, now.month)
    days = endday[1] - now.day

    years_text = " año" if years == 1 else " años"
    months_text = " mes" if months == 1 else " meses"
    days_text = " día" if days == 1 else " días"
    hours_text = " hora" if hours == 1 else " horas"
    minutes_text = " minuto" if minutes == 1 else " minutos"
    seconds_text = " segundo" if seconds == 1 else " segundos"

    elapsed_days_text = (
        f"Ya pasó {elapsed_time_percent}% del sexenio ({elapsed_days} días). #cuantolefalta"
    )
    remaining_days_text = f"(o bien, {remaining_days} días). "

    status = (
        f"Le faltan {years}{years_text}, {months}{months_text}, {days}{days_text}, "
        f"{hours}{hours_text}, {minutes}{minutes_text}, {seconds}{seconds_text} "
        f"{remaining_days_text} {elapsed_days_text}"
    )
    return status
