class ScheduleParserFindError(Exception):
    """ Ошибка нахождения курса+группы+подгруппы в файле"""

    def __init__(self, message="ScheduleParserFindError parser didn't find required column", error_code=None):
        super().__init__(message)
        self.message = message


class ConnectionParamsError(Exception):
    def __init__(self, message="Can't access to postgeDB without some env variables"):
        super().__init__(message)
        self.message = message


class NotFoundListError(Exception):
    def __init__(self, message="Can't find required list in Excel"):
        super().__init__(message)
        self.message = message
