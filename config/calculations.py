from .models import EventGroup, EventSubGroup, Condition, ConditionGroup

# gfs calculations
SQUALL_GFS: EventGroup = EventGroup(
    alias="Шквалы",
    name="squall",
    subgroups=[
        EventSubGroup(
            name="squall_L1",
            alias="Шквалы,грады высокий риск",
            level_code=1,
            condition_groups=[
                ConditionGroup([
                    Condition("cape_surface", lambda x: x > 1500),
                    Condition("cape_255-0", lambda x: x > 2000),
                    Condition("dls", lambda x: x > 26),
                    Condition("wmaxshear", lambda x: x > 1100)
                ])

            ]
        ),
        EventSubGroup(
            name="squall_L2",
            alias="Шквалы,грады повышенный риск",
            level_code=2,
            condition_groups=[
                ConditionGroup([
                    Condition("cape_surface", lambda x: x > 1000),
                    Condition("cape_255-0", lambda x: x > 1500),
                    Condition("dls", lambda x: x > 21),
                    Condition("wmaxshear", lambda x: x > 850),
                ])
            ]
        ),
        EventSubGroup(
            alias="Шквалы,град незначительный риск",
            name="squall_L3",
            level_code=3,
            condition_groups=[
                ConditionGroup([
                    Condition("cape_surface", lambda x: x > 600),
                    Condition("cape_255-0", lambda x: x > 1000),
                    Condition("dls", lambda x: x > 18),
                    Condition("wmaxshear", lambda x: x > 600),
                ]),
                ConditionGroup([
                    Condition("cape_surface", lambda x: x > 1500),
                    Condition("cape_255-0", lambda x: x > 2000),
                    Condition("dls", lambda x: x > 15),
                    Condition("wmaxshear", lambda x: x > 500),
                ])
            ]
        ),
        EventSubGroup(
            alias="Шквалы,град допустимый риск",
            level_code=4,
            name="squall_L4",
            condition_groups=[
                ConditionGroup([
                    Condition("cape_surface", lambda x: x > 400),
                    Condition("cape_255-0", lambda x: x > 700),
                    Condition("dls", lambda x: x > 15),
                    Condition("wmaxshear", lambda x: x > 500),
                ]),
                ConditionGroup([
                    Condition("cape_surface", lambda x: x > 1500, ),
                    Condition("cape_255-0", lambda x: x > 2000)
                ]),
                ConditionGroup([
                    Condition("cape_surface", lambda x: x > 200),
                    Condition("cape_255-0", lambda x: x > 400),
                    Condition("dls", lambda x: x > 21),
                ])
            ]
        )
    ]
)

# icon calculations
SQUALL_ICON: EventGroup = EventGroup(
    alias="Шквалы",
    name="squall",
    subgroups=[
        EventSubGroup(
            name="squall_L1",
            alias="Шквалы, высокий риск",
            level_code=1,
            condition_groups=[
                ConditionGroup([
                    Condition("dls", lambda x: x > 21)
                ])
            ]
        )
    ]
)
