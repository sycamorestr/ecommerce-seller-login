
import math
import random


def linspace(start, stop, num=50):
    if num < 1:
        return []
    step = (stop-start) / (num-1)
    return [start + step*i for i in range(num)]


def normal(mean=0.0, std_dev=1.0, size=None):
    if size is None:
        return random.gauss(mean, std_dev)
    else:
        return [random.gauss(mean, std_dev) for _ in range(size)]

class XTrace(object):
    def __init__(self):
        self.__pos_x = []
        self.__pos_y = []
        self.__pos_z = []

    def __set_pt_time(self):
        __end_pt_time = []
        __move_pt_time = []
        __move_cur_time = []
        self.__pos_z = []

        total_move_time = self.__need_time * random.uniform(0.8, 0.9)
        start_point_time = random.uniform(110, 200)
        __start_pt_time = [0, 0, int(start_point_time)]

        sum_move_time = 0

        _tmp_total_move_time = total_move_time
        while True:
            delta_time = random.uniform(15, 20)
            if _tmp_total_move_time < delta_time:
                break

            sum_move_time += delta_time
            _tmp_total_move_time -= delta_time
            __move_pt_time.append(int(start_point_time+sum_move_time))
            __move_cur_time.append(delta_time)

        last_pt_time = __move_pt_time[-1]
        __move_pt_time.append(last_pt_time+_tmp_total_move_time)

        sum_end_time = start_point_time + total_move_time
        other_point_time = self.__need_time - sum_end_time
        end_first_ptime = other_point_time / 2

        while True:
            delta_time = random.uniform(110, 200)
            if end_first_ptime - delta_time <= 0:
                break

            end_first_ptime -= delta_time
            sum_end_time += delta_time
            __end_pt_time.append(int(sum_end_time))

        __end_pt_time.append(int(sum_end_time + (other_point_time/2 + end_first_ptime)))
        self.__pos_z.extend(__start_pt_time)
        self.__pos_z.extend(__move_cur_time)
        self.__pos_z.extend([delta_time])

    def __set_distance(self, _dist):
        self.__distance = _dist

        if _dist < 100:
            self.__need_time = int(random.uniform(500, 1500))
        else:
            self.__need_time = int(random.uniform(1000, 2000))

    def __get_pos_z(self):
        return self.__pos_z

    def __get_pos_y(self):
        _pos_y = [random.uniform(-40, -18), 0]
        point_count = len(self.__pos_z)
        x = linspace(-10, 15, point_count - len(_pos_y))


        arct_y = [math.atan(item) for item in x]

        for _, val in enumerate(arct_y):
            _pos_y.append(val)

        return _pos_y

    def __get_pos_x(self, _distance):
        _pos_x = [random.uniform(-40, -18), 0]
        self.__set_distance(_distance)
        self.__set_pt_time()

        point_count = len(self.__pos_z)
        x = linspace(-1, 19, point_count-len(_pos_x))

        ss = [math.atan(item) for item in x]
        th = [math.tanh(item) for item in x]

        for idx in range(0, len(th)):
            if th[idx] < ss[idx]:
                th[idx] = ss[idx]

        th = [item + 1 for item in th]
        th = [item * (_distance / 2.5) for item in th]

        i = 0
        start_idx = int(point_count/10)
        end_idx = int(point_count/50)

        delta_pt = [abs(random.gauss(0, 1) * 1.1) for _ in range(point_count-start_idx-end_idx)]
        for idx in range(start_idx, point_count):
            if idx*1.3 > len(delta_pt):
                break

            th[idx] += delta_pt[i]
            i+=1

        _pos_x.extend(th)
        return _pos_x[-1], _pos_x

    def get_mouse_pos_path(self, distance):
        result = []
        _distance, x = self.__get_pos_x(distance)
        y = self.__get_pos_y()
        z = self.__get_pos_z()

        for idx in range(len(x)):
            result.append([int(x[idx]), int(y[idx]), int(z[idx])])

        return int(_distance), result

