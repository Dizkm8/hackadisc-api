from calendar import monthrange
from collections import deque


class DateService:
    @staticmethod
    def time_delta_with_month(date_1, date_2):
        """
        Get the time difference between two dates.

        Parameters
        ----------
        date_1 : datetime
            The first date.
        date_2 : datetime
            The second date.

        Returns
        -------
        int
            The years difference.
        int
            The months difference.
        int
            The days difference.
        """
        years_delta = date_1.year - date_2.year
        months_delta = date_1.month - date_2.month
        if months_delta < 0:
            years_delta -= 1
            months_delta = 12 + months_delta
        days_delta = date_1.day - date_2.day
        if days_delta < 0:
            months_delta -= 1
            if months_delta < 0:
                years_delta -= 1
                months_delta = 12 + months_delta
            days_delta = monthrange(date_1.year, date_1.month)[1] + days_delta
        return years_delta, months_delta, days_delta

    @staticmethod
    def format_time_delta(date_1, date_2):
        """
        Generate a string with the difference between two dates.

        Parameters
        ----------
        date_1 : datetime
            The first date.
        date_2 : datetime
            The second date.

        Returns
        -------
        str
            The formatted string.
        """

        years_delta, months_delta, days_delta = DateService.time_delta_with_month(date_1, date_2)
        deltas = [(years_delta, "año", "años"), (months_delta, "mes", "meses"), (days_delta, "día", "días")]
        deltas_queue = deque()
        for delta in deltas:
            if delta[0] > 0:
                deltas_queue.appendleft(delta)
        result = ""
        while length := len(deltas_queue):
            delta, singular, plural = deltas_queue.pop()
            phrase = f"{delta} {singular if delta == 1 else plural}"
            match length:
                case 1:
                    result += phrase
                case 2:
                    result += f"{phrase} y "
                case _:
                    result += f"{phrase}, "
        return result