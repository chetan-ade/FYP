import math
import numpy as np
import scipy.interpolate as interp


class SlottedIterable(object):
    __slots__ = ()

    def __iter__(self):
        for name in self.__slots__:
            yield getattr(self, name)

    def __repr__(self):
        return '{cls}({attr})'.format(
            cls=self.__class__.__name__,
            attr=', '.join(['{0}={1}'.format(
                name, getattr(self, name)) for name in self.__slots__]))


class Puff(SlottedIterable):
    __slots__ = ('x', 'y', 'z', 'r_sq')

    def __init__(self, x, y, z, r_sq):
        assert r_sq >= 0., 'r_sq must be non-negative.'
        self.x = x
        self.y = y
        self.z = z
        self.r_sq = r_sq


class Rectangle(SlottedIterable):
    __slots__ = ('x_min', 'x_max', 'y_min', 'y_max')

    def __init__(self, x_min, x_max, y_min, y_max):
        assert x_min < x_max, 'Rectangle x_min must be < x_max.'
        assert y_min < y_max, 'Rectangle y_min must be < y_max.'
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    @property
    def w(self):
        return self.x_max - self.x_min

    @property
    def h(self):
        return self.y_max - self.y_min

    def contains(self, x, y):
        return (x >= self.x_min and x <= self.x_max and
                y >= self.y_min and y <= self.y_max)


class PlumeModel(object):
    def __init__(self, sim_region=None, source_pos=(5., 0., 0.),
                 wind_model=None, model_z_disp=True, centre_rel_diff_scale=2.,
                 puff_init_rad=0.0316, puff_spread_rate=0.001,
                 puff_release_rate=10, init_num_puffs=10, max_num_puffs=1000,
                 rng=None):
        if sim_region is None:
            sim_region = Rectangle(0., 50., -12.5, 12.5)
        if rng is None:
            rng = np.random
        self.sim_region = sim_region
        if wind_model is None:
            wind_model = WindModel()
        self.wind_model = wind_model
        self.rng = rng
        self.model_z_disp = model_z_disp
        self._vel_dim = 3 if model_z_disp else 2
        if model_z_disp and hasattr(centre_rel_diff_scale, '__len__'):
            assert len(centre_rel_diff_scale) == 2, (
                'When model_z_disp=True, centre_rel_diff_scale must be a '
                'scalar or length 1 or 3 iterable.')
        self.centre_rel_diff_scale = centre_rel_diff_scale
        assert sim_region.contains(source_pos[0], source_pos[1]), (
            'Specified source position must be within simulation region.')
        source_z = 0 if len(source_pos) != 3 else source_pos[2]
        self._new_puff_params = (
            source_pos[0], source_pos[1], source_z, puff_init_rad**2)
        self.puff_spread_rate = puff_spread_rate
        self.puff_release_rate = puff_release_rate
        self.max_num_puffs = max_num_puffs
        self.puffs = [
            Puff(*self._new_puff_params) for i in range(init_num_puffs)]

    def update(self, dt):
        if len(self.puffs) < self.max_num_puffs:
            num_to_release = min(
                self.rng.poisson(self.puff_release_rate * dt),
                self.max_num_puffs - len(self.puffs))
            self.puffs += [
                Puff(*self._new_puff_params) for i in range(num_to_release)]
        alive_puffs = []
        for puff in self.puffs:
            wind_vel = np.zeros(self._vel_dim)
            wind_vel[:2] = self.wind_model.velocity_at_pos(puff.x, puff.y)
            filament_diff_vel = (self.rng.normal(size=self._vel_dim) *
                                 self.centre_rel_diff_scale)
            vel = wind_vel + filament_diff_vel
            puff.x += vel[0] * dt
            puff.y += vel[1] * dt
            if self.model_z_disp:
                puff.z += vel[2] * dt
            puff.r_sq += self.puff_spread_rate * dt
            if self.sim_region.contains(puff.x, puff.y):
                alive_puffs.append(puff)
        self.puffs = alive_puffs

    @property
    def puff_array(self):
        return np.array([tuple(puff) for puff in self.puffs])


class WindModel(object):
    def __init__(self, sim_region=None, n_x=21, n_y=21, u_av=1., v_av=0.,
                 k_x=20., k_y=20., noise_gain=2., noise_damp=0.1,
                 noise_bandwidth=0.2, use_original_noise_updates=False,
                 rng=None, DirArray=[], SpdArray=[]):
        if sim_region is None:
            sim_region = Rectangle(0, 100, -50, 50)
        if rng is None:
            rng = np.random
        self.sim_region = sim_region
        self.u_av = u_av
        self.v_av = v_av
        self.n_x = n_x
        self.n_y = n_y
        self.k_x = k_x
        self.k_y = k_y
        self.noise_gen = ColouredNoiseGenerator(
            np.zeros((2, 8)), noise_damp, noise_bandwidth, noise_gain,
            use_original_noise_updates, rng)
        self.dx = sim_region.w / (n_x - 1)
        self.dy = sim_region.h / (n_y - 1)
        self._u = np.ones((n_x + 2, n_y + 2)) * u_av
        self._v = np.ones((n_x + 2, n_y + 2)) * v_av
        self._u_int = self._u[1:-1, 1:-1]
        self._v_int = self._v[1:-1, 1:-1]
        self._x_points = np.linspace(sim_region.x_min, sim_region.x_max, n_x)
        self._y_points = np.linspace(sim_region.y_min, sim_region.y_max, n_y)
        self._interp_set = True

        # OUR VARIABLES
        self.counter = 0
        self.magnitude = 1
        self.angle = 0
        self.newU = 0
        self.newV = 0
        self.day = ""
        self.array = DirArray
        self.speedArray = SpdArray
        self.minSpeed = min(self.speedArray)
        self.speedArray = [i/self.minSpeed for i in self.speedArray]
        # print(self.speedArray)
        self.newArray = []
        for i in range(len(self.array)-1):
            self.newArray.append(self.array[i])
            self.diff = self.array[i+1] - self.array[i]
            self.sign = np.sign(self.diff)
            self.magDiff = abs(self.diff)
            if self.magDiff > 180:
                self.magDiff = abs(self.magDiff - 360)
                self.sign = self.sign * -1
            self.diff = self.magDiff * self.sign
            self.diff = self.diff/600
            for j in range(1, 600):
                self.temp = self.array[i]+self.diff*j
                if self.temp < 0:
                    self.temp += 360
                elif self.temp > 360:
                    self.temp -= 360
                self.newArray.append(self.temp)
        self.newArray.append(self.array[-1])
        self.newSpeedArray = []
        for i in range(len(self.speedArray)-1):
            self.newSpeedArray.append(self.speedArray[i])
            self.diff = self.speedArray[i+1] - self.speedArray[i]
            self.diff = self.diff/600
            for j in range(1, 600):
                self.temp = self.speedArray[i]+self.diff*j
                self.newSpeedArray.append(self.temp)
        self.newSpeedArray.append(self.speedArray[-1])

    def _set_interpolators(self):
        self._interp_u = interp.RectBivariateSpline(
            self.x_points, self.y_points, self._u_int)
        self._interp_v = interp.RectBivariateSpline(
            self.x_points, self.y_points, self._v_int)
        self._interp_set = True

    @property
    def x_points(self):
        return self._x_points

    @property
    def y_points(self):
        return self._y_points

    @property
    def velocity_field(self):
        return np.dstack((self._u_int, self._v_int))

    def velocity_at_pos(self, x, y):
        if not self._interp_set:
            self._set_interpolators()
        return np.array([float(self._interp_u(x, y)),
                         float(self._interp_v(x, y))])

    def update(self, dt):
        try:
            self.angle = self.newArray[self.counter]
            self.magnitude = self.newSpeedArray[self.counter]
        except IndexError:
            pass
        self.newU = self.magnitude*math.cos(self.angle * (math.pi/180))
        self.newV = self.magnitude*math.sin(self.angle * (math.pi/180))
        self.du = self.newU - self._u_int[0][0]
        self.dv = self.newV - self._v_int[0][0]
        self.counter += 1
        self.day = "DAY "+str(self.counter//600)  # print(self.day)
        self._u_int += self.du
        self._v_int += self.dv
        self._interp_set = False


class ColouredNoiseGenerator(object):
    def __init__(self, init_state, damping=0.1, bandwidth=0.2, gain=1.,
                 use_original_updates=False,  rng=None):
        if rng is None:
            rng = np.random
        self.a_mtx = np.array([
            [0., 1.], [-bandwidth**2, -2. * damping * bandwidth]])
        self.b_mtx = np.array([[0.], [gain * bandwidth**2]])
        self.state = init_state
        self.rng = rng
        self.use_original_updates = use_original_updates

    @property
    def output(self):
        return self.state[0, :]

    def update(self, dt):
        n = self.rng.normal(size=(1, self.state.shape[1]))
        if self.use_original_updates:
            self.state += dt * (self.a_mtx.dot(self.state) + self.b_mtx.dot(n))
        else:
            self.state += (
                dt * self.a_mtx.dot(self.state) + self.b_mtx.dot(n) * dt**0.5)
