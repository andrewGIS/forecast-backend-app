from typing import List, Callable


class Condition(object):
    """
    Simple calculation operation contains one index name and con value
    """

    def __init__(self, index_name: str, calculation: Callable):
        self.index_name = index_name
        self.calculation = calculation


class ConditionGroup(object):
    """
    Semantic connected group of simple calculation
    """

    def __init__(self, conditions: List[Condition]):
        self.conditions = conditions


class EventSubGroup(object):
    """
    Class for subgroup definition in event e.g. storm with high level confidence
    """
    def __init__(self, name, alias, level_code, condition_groups: List[ConditionGroup]):
        self.name = name  # squall L1
        self.alias = alias  # Шквалы, высокий риск
        self.level_code = level_code  # 1 very high risk 10 very low
        self.condition_groups = condition_groups  # some simple calculations joined in group


class EventGroup:
    """
    General class for group of event e.g. squalls
    """
    def __init__(self, alias, name, subgroups: List[EventSubGroup]):
        self.alias = alias  # Шквалы
        self.name = name  # squall
        self.subgroups = subgroups  # list of subevent e.g. huge squal risk, low squal risk and e.g.


class ModelParams(object):

    def __init__(self,
                 RASTER_X_SIZE,
                 RASTER_Y_SIZE,
                 RASTER_GEO_TRANSFORM,
                 DOWNLOAD_URL,
                 CALCULATIONS: List[EventGroup],
                 INDEXES: List[str]
    ):
        self.RASTER_X_SIZE = RASTER_X_SIZE
        self.RASTER_Y_SIZE = RASTER_Y_SIZE
        self.RASTER_GEO_TRANSFORM = RASTER_GEO_TRANSFORM
        self.DOWNLOAD_URL = DOWNLOAD_URL
        self.CALCULATIONS = CALCULATIONS
        self.INDEXES = INDEXES

