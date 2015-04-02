# -*- coding: UTF-8 -*-
import math


class Helper(object):

    def get_angled_point(angle, longueur, cx, cy):
        """ angle est en radians"""
        return (math.cos(angle)*longueur)+cx, (math.sin(angle)*longueur)+cy
    get_angled_point = staticmethod(get_angled_point)

    def calc_angle(x1, y1, x2, y2):
        return math.atan2(y2 - y1, x2 - x1)
    calc_angle = staticmethod(calc_angle)

    def calc_distance(x1, y1, x2, y2):
        return math.sqrt(abs(x2-x1)**2 + abs(y2-y1)**2)
    calc_distance = staticmethod(calc_distance)

    def calc_slope(p1, p2):
        return (p2[1] - p1[1])/(p2[0] - p1[0])
    calc_slope = staticmethod(calc_slope)

    def calc_origin_ordinate(x, y, slope):
        return -1*(slope*x - y)
    calc_origin_ordinate = staticmethod(calc_origin_ordinate)