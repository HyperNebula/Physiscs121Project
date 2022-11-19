import matplotlib

matplotlib.use('TkAgg')  # 'tkAgg' if Qt not present
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation


class Arrow:
    def __init__(self, height, speed, angle, dt):
        self.height = height
        self.speed = speed
        self.angle = self.degree_to_radians(angle)

        self.touched_ground = False

        self.x = 0.0
        self.y = height

        self.max_x = self.x
        self.max_y = self.y
        self.max = self.max_y

        self.dt = dt

        self.g = -9.81

        self.x_speed, self.y_speed = self.split_speed()

        self.time_final = (-self.y_speed - (self.y_speed ** 2 - (2 * self.g * self.height)) ** 0.5) / self.g
        self.x_final = self.x_speed * self.time_final

        print(self.x_final)

        self.trajectory = [np.array([[0.0, self.height], [self.x, self.y]])]

    @staticmethod
    def degree_to_radians(degree):
        return degree * np.pi / 180

    def split_speed(self):
        return np.cos(self.angle) * self.speed, np.sin(self.angle) * self.speed

    def update_max_height(self):
        if self.x > self.max_x:
            self.max_x = self.x
        if self.y > self.max_y:
            self.max_y = self.y

        if self.max_y > self.max_x:
            self.max = self.max_y
        else:
            self.max = self.max_x

    def evolve(self):
        self.y += self.y_speed * self.dt
        self.x += self.x_speed * self.dt

        self.y_speed += self.g * self.dt

        if self.y < 0.0:
            # self.y = 0.0
            # self.x = self.x_final
            self.touched_ground = True
        self.update_max_height()

        new_position = np.array([[0.0, self.height], [self.x, self.y]])
        self.trajectory.append(new_position)
        print(new_position)
        return new_position


class Animator:
    def __init__(self, drawn_object, draw_trace=False):
        self.object = drawn_object
        self.draw_trace = draw_trace
        self.time = 0.0

        # set up the figure
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim(bottom=0)
        self.ax.set_xlim(left=0)

        # prepare a text window for the timer
        self.time_text = self.ax.text(0.05, 0.95, '',
                                      horizontalalignment='left',
                                      verticalalignment='top',
                                      transform=self.ax.transAxes)

        # initialize by plotting the last position of the trajectory
        self.line, = self.ax.plot(
            self.object.trajectory[-1][:, 0],
            self.object.trajectory[-1][:, 1],
            linestyle='None',
            marker=(3, 0, 180))

        # trace the whole trajectory of the arrow
        if self.draw_trace:
            self.trace, = self.ax.plot(
                [a[1][0] for a in self.object.trajectory],
                [a[1][1] for a in self.object.trajectory])

    def advance_time_step(self):
        while not self.object.touched_ground:
            self.time += self.object.dt
            yield self.object.evolve()

    def update_frame(self):
        self.ax.set_ylim(top=self.object.max)
        self.ax.set_xlim(right=self.object.max)

        plt.savefig(f'frame{self.time}.png')

    def update(self, data):
        self.time_text.set_text(f'Elapsed time: {round(self.time, 2)} s')

        self.line.set_ydata(data[:, 1])
        self.line.set_xdata(data[:, 0])

        self.update_frame()

        if self.draw_trace:
            self.trace.set_xdata([a[1, 0] for a in self.object.trajectory])
            self.trace.set_ydata([a[1, 1] for a in self.object.trajectory])
        return self.line

    def animate(self):
        self.animation = animation.FuncAnimation(self.fig, self.update,
                                                 self.advance_time_step, interval=25, blit=False)


arrow = Arrow(height=2, speed=10, angle=40, dt=0.01)
animator = Animator(drawn_object=arrow, draw_trace=True)
animator.animate()
plt.show()
