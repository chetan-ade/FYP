import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.animation import FuncAnimation
import numpy as np
import models
import processors
import getData
import datetime
import matplotlib.animation
# import matplotlib
# matplotlib.use("Agg")
# Writer = animations.FFMpegWriter()
# writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

DEFAULT_SEED = 20181108


def set_up_figure(fig_size=(10, 5)):
    fig, ax = plt.subplots(1, 1, figsize=fig_size)
    title = ax.set_title('')
    return fig, ax, title


def update_decorator(dt, title, steps_per_frame, models):
    def inner_decorator(update_function):
        def wrapped_update(i):
            for j in range(steps_per_frame):
                for model in models:
                    model.update(dt)
            t = i * steps_per_frame * dt
            title.set_text('')
            return [title] + update_function(i)
        return wrapped_update
    return inner_decorator


def plume_model_demo(dt=0.03, t_max=100, steps_per_frame=20,
                     seed=DEFAULT_SEED):
    # apiList, location = getData.getData(
    #     '19.0368,73.0158', datetime.datetime(2018, 10, 15))
    # array = []
    # speedArray = []
    # dateArray = []
    # for i in apiList:
    #     array.append(int(i['Direction']))
    #     speedArray.append(int(i['Speed']))
    #     d = datetime.datetime.strptime(i['Date'], '%Y-%m-%d')
    #     dateArray.append(d.strftime('%b %d,%Y'))
    # print("Demo: Dir", array)
    # print("Demo: Spd", speedArray)
    # print("Demo: Dte", dateArray)

    # array = [200, 192, 185, 213, 189, 194, 218,
    #          144, 180, 187, 246, 179, 255, 237, 199, 241]
    # speedArray = [8, 10, 9, 9, 12, 8, 10, 9, 8, 9, 10, 10, 12, 12, 8, 9]
    # dateArray = ['Mar 21,2020', 'Mar 22,2020', 'Mar 23,2020', 'Mar 24,2020', 'Mar 25,2020', 'Mar 26,2020', 'Mar 27,2020', 'Mar 28,2020', 'Mar 29,2020', 'Mar 30,2020', 'Mar 31,2020', 'Apr 01,2020', 'Apr 02,2020', 'Apr 03,2020',
    #              'Apr 04,2020', 'Apr 05,2020']

    array = [200, 192, 185]
    speedArray = [8, 10, 9]
    dateArray = ['Mar 21,2020', 'Mar 22,2020', 'Mar 23,2020']

    rng = np.random.RandomState(seed)
    sim_region = models.Rectangle(x_min=0., x_max=100, y_min=-25., y_max=25.)
    wind_model = models.WindModel(
        sim_region, 21, 11, rng=rng, DirArray=array, SpdArray=speedArray, dateArray=dateArray)
    plume_model = models.PlumeModel(
        sim_region, (50., 0., 0.), wind_model, rng=rng)
    fig, ax, title = set_up_figure()
    vf_plot = plt.quiver(
        wind_model.x_points, wind_model.y_points,
        wind_model.velocity_field.T[0], wind_model.velocity_field.T[1],
        width=0.000000000001)
    # width = 0.003 for normal arrows, width = 0.000000000001 for jhugaad
    ax.axis(ax.axis() + np.array([-0.25, 0.25, -0.25, 0.25]))
    radius_mult = 200
    pp_plot = plt.scatter(
        plume_model.puff_array[:, 0], plume_model.puff_array[:, 1],
        radius_mult * plume_model.puff_array[:, 3]**0.5, c='r',
        edgecolors='none')
    # c = color
    ax.set_xlabel('x-coordinate / m')
    ax.set_ylabel('y-coordinate / m')
    # dayText = ax.text(99, 25, "DAY ")
    dayText = ax.text(90, 25, "DateTime")
    ax.set_aspect(1)
    fig.tight_layout()
    @update_decorator(dt, title, steps_per_frame, [wind_model, plume_model])
    def update(i):
        vf_plot.set_UVC(wind_model.velocity_field[:, :, 0].T,
                        wind_model.velocity_field[:, :, 1].T)
        pp_plot.set_offsets(plume_model.puff_array[:, :2])
        pp_plot._sizes = radius_mult * plume_model.puff_array[:, 3]**0.5
        dayText.set_text(wind_model.day)
        if(wind_model.counter > len(wind_model.newArray)):
            anim.event_source.stop()
        return [vf_plot, pp_plot, dayText]

    n_frame = int(t_max / (dt * steps_per_frame) + 0.5)
    anim = FuncAnimation(fig, update, frames=n_frame, blit=True)
    # anim.save('plume.mp4', dpi=100, fps=20, extra_args=['-vcodec', 'libx264'])
    # anim.save("plume.html")
    return fig, ax, anim

# def conc_point_val_demo(dt=0.01, t_max=5, steps_per_frame=1, x=10., y=0.0,
#                         seed=DEFAULT_SEED):
#     rng = np.random.RandomState(seed)
#     sim_region = models.Rectangle(
#         x_min=0., x_max=100, y_min=-25., y_max=25.)
#     wind_model = models.WindModel(sim_region, 21, 11, rng=rng)
#     plume_model = models.PlumeModel(
#         sim_region, (5., 0., 0.), wind_model, rng=rng)
#     for t in np.arange(0, 10, dt):
#         wind_model.update(dt)
#         plume_model.update(dt)
#     val_calc = processors.ConcentrationValueCalculator(1.)
#     conc_vals = []
#     conc_vals.append(val_calc.calc_conc_point(plume_model.puff_array, x, y))
#     ts = [0.]
#     fig, ax, title = set_up_figure()
#     conc_line, = plt.plot(ts, conc_vals)
#     ax.set_xlim(0., t_max)
#     ax.set_ylim(0., 150.)
#     ax.set_xlabel('Time / s')
#     ax.set_ylabel('Normalised concentration')
#     ax.grid(True)
#     fig.tight_layout()
#     @update_decorator(dt, title, steps_per_frame, [wind_model, plume_model])
#     def update(i):
#         ts.append(dt * i * steps_per_frame)
#         conc_vals.append(
#             val_calc.calc_conc_point(plume_model.puff_array, x, y))
#         conc_line.set_data(ts, conc_vals)
#         return [conc_line]
#     n_frame = int(t_max / (dt * steps_per_frame) + 0.5)
#     anim = FuncAnimation(fig, update, frames=n_frame, blit=True)
#     return fig, ax, anim


fig, ax, anim = plume_model_demo()
# fig, ax, anim = conc_point_val_demo()
plt.show()
