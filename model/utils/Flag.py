class Flag(object):
    STANDBY = 1
    MOVE = 2
    PATROL = 4
    ATTACK = 8
    GATHER = 16
    BUILD = 32
    LAND = 64
    RESEARCH = 128
    DESTROY = 256
    CREATE = 512
    CHANGE_RALLY_POINT = 1024
    CANCEL_UNIT = 2048
    BUILD_UNIT = 4096
    CHANGE_FORMATION = 8192
    TRADE = 16384
    DESTROY_ALL = 32768
    DEMAND_ALLIANCE = 65536
    GROUND_MOVE = 131072
    GROUND_GATHER = 262144
    FINISH_BUILD = 524288
    BUY_TECH = 1048576
    GROUND_ATTACK = 2097152
    LOAD = 4194304
    NOTIFICATION = 8388608
    UNLOAD = 16777216
    HEAL = 33554432
    CANCEL_TECH = 67108864
    CHEAT = 134217728
    ATTACK_BUILDING = 268435456
    LINK_WAYPOINTS = 536870912
    WORMHOLE = 1073741824

    def __init__(self, initial_target=None, final_target=None, flag_state=STANDBY):
        self.initial_target = initial_target
        self.final_target = final_target
        self.flag_state = flag_state
            
    def to_string(self):
        return self.initial_target.to_string()
