
def calculation_list():
    # name of indicator for calc : # function for condition in array

    ### squall group start
    squall_L1 = {
        "alias": "Шквалы,грады высокий риск",
        "name": "squall_L1",
        "conditions": [{
            "cape_surface": lambda x: x > 1500,
            "cape_255-0": lambda x: x > 2000,
            "dls": lambda x: x > 26,
            "wmaxshear": lambda x: x > 1100,
        }]
    }

    squall_L2 = {
        "alias": "Шквалы,грады повышенный риск",
        "name": "squall_L2",
        "conditions": [{
            "cape_surface": lambda x: x > 1000,
            "cape_255-0": lambda x: x > 1500,
            "dls": lambda x: x > 21,
            "wmaxshear": lambda x: x > 850,
        }]

    }

    squall_L3 = {
        "alias": "Шквалы,град незначительный риск",
        "name": "squall_L3",
        "conditions": [
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
        ]

    }

    squall_L4 = {
        "alias": "Шквалы,град допустимый риск",
        "name": "squall_L4",
        "conditions": [
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
        ]

    }
    ### squall group end

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
    return [squall_L1, squall_L2, squall_L3, squall_L4]


def event_group_list():
    groups = calculation_list()
    result = []
    keysToExtract = ["alias","name"]
    for group in groups:
        result.append({key: group[key] for key in keysToExtract})
    return result
