import math
import numpy as np


class ConcentrationValueCalculator(object):
    def __init__(self, puff_molecular_amount):
        self._ampl_const = puff_molecular_amount / (8 * np.pi**3)**0.5

    def _puff_conc_dist(self, x, y, z, px, py, pz, r_sq):
        return (
            self._ampl_const / r_sq**1.5 *
            np.exp(-((x - px)**2 + (y - py)**2 + (z - pz)**2) / (2 * r_sq))
        )

    def calc_conc_point(self, puff_array, x, y, z=0):
        px, py, pz, r_sq = puff_array[~np.isnan(puff_array[:, 0]), :].T
        return self._puff_conc_dist(x, y, z, px, py, pz, r_sq).sum(-1)

    def calc_conc_list(self, puff_array, x, y, z=0):
        px, py, pz, r_sq = puff_array[~np.isnan(puff_array[:, 0]), :].T
        return self._puff_conc_dist(
            x[:, None], y[:, None], z, px[None], py[None], pz[None], r_sq[None]
        ).sum(-1)

    def calc_conc_grid(self, puff_array, x, y, z=0):
        px, py, pz, r_sq = puff_array[~np.isnan(puff_array[:, 0]), :].T
        return self._puff_conc_dist(
            x[..., None], y[..., None], z, px[None, None], py[None, None],
            pz[None, None], r_sq[None, None]).sum(-1)


class ConcentrationArrayGenerator(object):
    def __init__(self, array_xy_region, array_z, n_x, n_y, puff_mol_amount,
                 kernel_rad_mult=3):
        self.array_xy_region = array_xy_region
        self.array_z = array_z

        self.n_x = n_x
        self.n_y = n_y

        self.dx = array_xy_region.w / n_x
        self.dy = array_xy_region.h / n_y

        self._ampl_const = puff_mol_amount / (8*np.pi**3)**0.5
        self.kernel_rad_mult = kernel_rad_mult

    def _puff_kernel(self, shift_x, shift_y, z_offset, r_sq, even_w, even_h):
        shape = (2 * (r_sq * self.kernel_rad_mult**2 - z_offset**2)**0.5 /
                 np.array([self.dx, self.dy]))

        shape[0] = self._round_up_to_next_even_or_odd(shape[0], even_w)
        shape[1] = self._round_up_to_next_even_or_odd(shape[1], even_h)

        [x_grid, y_grid] = 0.5 + np.mgrid[-shape[0] // 2:shape[0] // 2,
                                          -shape[1] // 2:shape[1] // 2]

        x_grid = x_grid * self.dx + shift_x
        y_grid = y_grid * self.dy + shift_y

        r_sq_grid = x_grid**2 + y_grid**2 + z_offset**2
        return (self._ampl_const / r_sq**1.5) * np.exp(-r_sq_grid / (2 * r_sq))

    @staticmethod
    def _round_up_to_next_even_or_odd(value, to_even):
        value = math.ceil(value)
        if to_even:
            if value % 2 == 1:
                value += 1
        else:
            if value % 2 == 0:
                value += 1
        return value

    def generate_single_array(self, puff_array):
        conc_array = np.zeros((self.n_x, self.n_y))

        for (puff_x, puff_y, puff_z, puff_r_sq) in puff_array:
            if np.isnan(puff_x):
                break

            if not self.array_xy_region.contains(puff_x, puff_y):
                continue

            puff_z_offset = (self.array_z - puff_z)
            if abs(puff_z_offset) / puff_r_sq**0.5 > self.kernel_rad_mult:
                continue

            p = (puff_x - self.array_xy_region.x_min) / self.dx
            q = (puff_y - self.array_xy_region.y_min) / self.dy

            u = math.floor(2 * p + 0.5) / 2
            v = math.floor(2 * q + 0.5) / 2

            kernel = self._puff_kernel(
                (p - u) * self.dx, (q - v) * self.dy, puff_z_offset, puff_r_sq,
                u % 1 == 0, v % 1 == 0)

            (w, h) = kernel.shape

            r_rng_arr = slice(int(max(0, u - w / 2.)),
                              int(max(min(u + w / 2., self.n_x), 0)))
            c_rng_arr = slice(int(max(0, v - h / 2.)),
                              int(max(min(v + h / 2., self.n_y), 0)))
            r_rng_knl = slice(int(max(0, -u + w / 2.)),
                              int(min(-u + w / 2. + self.n_x, w)))
            c_rng_knl = slice(int(max(0, -v + h / 2.)),
                              int(min(-v + h / 2. + self.n_y, h)))

            conc_array[r_rng_arr, c_rng_arr] += kernel[r_rng_knl, c_rng_knl]
        return conc_array

    def generate_multiple_arrays(self, puff_arrays):
        conc_arrays = []

        for puff_array in puff_arrays:
            conc_arrays.append(self.generate_single_frame(puff_array))
        return conc_arrays
