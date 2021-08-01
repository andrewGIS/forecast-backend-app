# TODO make same model names everywhere
from config.settings import Config

# here stored all names of models
models = Config.MODELS

# check that conditions named as conditions_{model_name} (conditions_gfs axample)
class EventSubGroup(object):

    def __init__(self, name, alias, level_code, conditions_gfs, conditions_icon=[]):
        self.name = name
        self.alias = alias
        self.level_code = level_code
        self.conditions_gfs = conditions_gfs
        self.conditions_icon = conditions_icon


def calculation_list():
    # name of indicator for calc : # function for condition in array

    # TODO check it
    # !!!! Order in definition is important!!From high risk to low!!!!!
    eventGroups = [
        {
            "alias": "Шквалы",
            "name": "squall",
            "subgroups": [
                EventSubGroup(
                    name="squall_L1",
                    alias="Шквалы,грады высокий риск",
                    level_code=1,
                    conditions_gfs=[{
                        "cape_surface": lambda x: x > 1500,
                        "cape_255-0": lambda x: x > 2000,
                        "dls": lambda x: x > 26,
                        "wmaxshear": lambda x: x > 1100,
                    }],
                    conditions_icon=[{
                        "dls": lambda x: x > 26
                    }]
                ),
                EventSubGroup(
                    name="squall_L2",
                    alias="Шквалы,грады повышенный риск",
                    level_code=2,
                    conditions_gfs=[{
                        "cape_surface": lambda x: x > 1000,
                        "cape_255-0": lambda x: x > 1500,
                        "dls": lambda x: x > 21,
                        "wmaxshear": lambda x: x > 850,
                    }],
                    conditions_icon=[{
                        "dls": lambda x: x > 21,
                    }]
                ),
                EventSubGroup(
                    alias="Шквалы,град незначительный риск",
                    name="squall_L3",
                    level_code=3,
                    conditions_gfs=[
                        {
                            "cape_surface": lambda x: x > 600,
                            "cape_255-0": lambda x: x > 1000,
                            "dls": lambda x: x > 18,
                            "wmaxshear": lambda x: x > 600,
                        },
                        {
                            "cape_surface": lambda x: x > 1500,
                            "cape_255-0": lambda x: x > 2000,
                            "dls": lambda x: x > 15,
                            "wmaxshear": lambda x: x > 500,
                        }
                    ],
                    conditions_icon=[{
                        "dls": lambda x: x > 18,
                    }]
                ),
                EventSubGroup(
                    alias="Шквалы,град допустимый риск",
                    level_code=4,
                    name="squall_L4",
                    conditions_gfs=[
                        {
                            "cape_surface": lambda x: x > 400,
                            "cape_255-0": lambda x: x > 700,
                            "dls": lambda x: x > 15,
                            "wmaxshear": lambda x: x > 500,
                        },
                        {
                            "cape_surface": lambda x: x > 1500,
                            "cape_255-0": lambda x: x > 2000
                        },
                        {
                            "cape_surface": lambda x: x > 200,
                            "cape_255-0": lambda x: x > 400,
                            "dls": lambda x: x > 21,
                        }
                    ],
                    conditions_icon=[{
                        "dls": lambda x: x > 15,
                    }]
                )

            ]
        }
    ]

    ### windthrows group start
    stormsHighRisk = {
        "alias": "Имя",
        "name": "test",
        "conditions": {
            "wmaxshear": lambda x: x > 250
        }

    }

    stormsMediumRisk = {
        "alias": "Имя",
        "name": "test",
        "conditions": [{
            "wmaxshear": lambda x: x > 250
        }]

    }

    stormsLowRisk = {
        # name of indicator for calc : # function for condition in array
        "alias": "Имя",
        "name": "test",
        "conditions": [
            {
                "wmaxshear": lambda x: x > 250
            }
        ]

    }
    ### windthrows group end

    # return [squallHighRisk, stormsHighRisk,stormsMediumRisk,stormsLowRisk]
    return eventGroups


def event_group_list():
    groups = calculation_list()
    result = []
    keysToExtract = ["alias", "name"]
    for group in groups:
        result.append({key: group[key] for key in keysToExtract})
    return result
