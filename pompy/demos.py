from __future__ import division
import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.animation import FuncAnimation
import numpy as np
import models
import processors

DEFAULT_SEED = 20181108


def set_up_figure(fig_size=(10, 5)):
    fig, ax = plt.subplots(1, 1, figsize=fig_size)
    title = ax.set_title('Simulation time = ---- seconds')
    return fig, ax, title


def update_decorator(dt, title, steps_per_frame, models):
    def inner_decorator(update_function):
        def wrapped_update(i):
            for j in range(steps_per_frame):
                for model in models:
                    model.update(dt)
            t = i * steps_per_frame * dt
            title.set_text('Simulation time = {0:.3f} seconds'.format(t))
            return [title] + update_function(i)
        return wrapped_update
    return inner_decorator


def wind_model_demo(dt=0.01, t_max=100, steps_per_frame=20, seed=DEFAULT_SEED):
    rng = np.random.RandomState(seed)
    wind_region = models.Rectangle(x_min=0., x_max=100., y_min=-25., y_max=25.)
    wind_model = models.WindModel(wind_region, 21, 11, rng=rng)
    for t in np.arange(0, 10, dt):
        wind_model.update(dt)
    fig, ax, title = set_up_figure()
    vf_plot = ax.quiver(wind_model.x_points, wind_model.y_points,
                        wind_model.velocity_field.T[0],
                        wind_model.velocity_field.T[1], width=0.003)
    ax.axis(ax.axis() + np.array([-0.25, 0.25, -0.25, 0.25]))
    ax.set_xlabel('x-coordinate / m')
    ax.set_ylabel('y-coordinate / m')
    ax.set_aspect(1)
    fig.tight_layout()
    @update_decorator(dt, title, steps_per_frame, [wind_model])
    def update(i):
        vf_plot.set_UVC(
            wind_model.velocity_field.T[0], wind_model.velocity_field.T[1])
        return [vf_plot]
    n_frame = int(t_max / (dt * steps_per_frame) + 0.5)
    anim = FuncAnimation(fig, update, n_frame, blit=True)
    return fig, ax, anim


def plume_model_demo(dt=0.03, t_max=100, steps_per_frame=20,
                     seed=DEFAULT_SEED):
    rng = np.random.RandomState(seed)
    sim_region = models.Rectangle(x_min=0., x_max=100, y_min=-25., y_max=25.)
    wind_model = models.WindModel(sim_region, 21, 11, rng=rng)
    for t in np.arange(0, 10, dt):
        wind_model.update(dt)
    plume_model = models.PlumeModel(
        sim_region, (15., 0., 0.), wind_model, rng=rng)
    fig, ax, title = set_up_figure()
    vf_plot = plt.quiver(
        wind_model.x_points, wind_model.y_points,
        wind_model.velocity_field.T[0], wind_model.velocity_field.T[1],
        width=0.003)
    ax.axis(ax.axis() + np.array([-0.25, 0.25, -0.25, 0.25]))
    radius_mult = 200
    pp_plot = plt.scatter(
        plume_model.puff_array[:, 0], plume_model.puff_array[:, 1],
        radius_mult * plume_model.puff_array[:, 3]**0.5, c='r',
        edgecolors='none')
    ax.set_xlabel('x-coordinate / m')
    ax.set_ylabel('y-coordinate / m')
    ax.set_aspect(1)
    fig.tight_layout()
    @update_decorator(dt, title, steps_per_frame, [wind_model, plume_model])
    def update(i):
        vf_plot.set_UVC(wind_model.velocity_field[:, :, 0].T,
                        wind_model.velocity_field[:, :, 1].T)
        pp_plot.set_offsets(plume_model.puff_array[:, :2])
        pp_plot._sizes = radius_mult * plume_model.puff_array[:, 3]**0.5
        return [vf_plot, pp_plot]
    n_frame = int(t_max / (dt * steps_per_frame) + 0.5)
    anim = FuncAnimation(fig, update, frames=n_frame, blit=True)
    return fig, ax, anim


def conc_point_val_demo(dt=0.01, t_max=5, steps_per_frame=1, x=10., y=0.0,
                        seed=DEFAULT_SEED):
    rng = np.random.RandomState(seed)
    sim_region = models.Rectangle(x_min=0., x_max=100, y_min=-25., y_max=25.)
    wind_model = models.WindModel(sim_region, 21, 11, rng=rng)
    plume_model = models.PlumeModel(
        sim_region, (5., 0., 0.), wind_model, rng=rng)
    for t in np.arange(0, 10, dt):
        wind_model.update(dt)
        plume_model.update(dt)
    val_calc = processors.ConcentrationValueCalculator(1.)
    conc_vals = []
    conc_vals.append(val_calc.calc_conc_point(plume_model.puff_array, x, y))
    ts = [0.]
    fig, ax, title = set_up_figure()
    conc_line, = plt.plot(ts, conc_vals)
    ax.set_xlim(0., t_max)
    ax.set_ylim(0., 150.)
    ax.set_xlabel('Time / s')
    ax.set_ylabel('Normalised concentration')
    ax.grid(True)
    fig.tight_layout()
    @update_decorator(dt, title, steps_per_frame, [wind_model, plume_model])
    def update(i):
        ts.append(dt * i * steps_per_frame)
        conc_vals.append(
            val_calc.calc_conc_point(plume_model.puff_array, x, y))
        conc_line.set_data(ts, conc_vals)
        return [conc_line]
    n_frame = int(t_max / (dt * steps_per_frame) + 0.5)
    anim = FuncAnimation(fig, update, frames=n_frame, blit=True)
    return fig, ax, anim


def concentration_array_demo(dt=0.01, t_max=100, steps_per_frame=50,
                             seed=DEFAULT_SEED):
    rng = np.random.RandomState(seed)
    sim_region = models.Rectangle(x_min=0., x_max=100, y_min=-25., y_max=25.)
    wind_model = models.WindModel(sim_region, 21, 11, rng=rng)
    plume_model = models.PlumeModel(
        sim_region, (5., 0., 0.), wind_model, rng=rng)
    for t in np.arange(0, 10, dt):
        wind_model.update(dt)
        plume_model.update(dt)
    array_gen = processors.ConcentrationArrayGenerator(
        sim_region, 0.01, 500, 250, 1.)
    fig, ax, title = set_up_figure()
    conc_array = array_gen.generate_single_array(plume_model.puff_array)
    conc_im = plt.imshow(conc_array.T, extent=sim_region, cmap='Reds',
                         vmin=0., vmax=1.)
    ax.set_xlabel('x-coordinate / m')
    ax.set_ylabel('y-coordinate / m')
    ax.set_aspect(1)
    fig.tight_layout()
    @update_decorator(dt, title, steps_per_frame, [wind_model, plume_model])
    def update(i):
        conc_im.set_data(
            array_gen.generate_single_array(plume_model.puff_array).T)
        return [conc_im]
    n_frame = int(t_max / (dt * steps_per_frame) + 0.5)
    anim = FuncAnimation(fig, update, frames=n_frame, blit=True)
    return fig, ax, anim


fig, ax, anim = plume_model_demo()
plt.show()
