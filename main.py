import matplotlib

matplotlib.use('TkAgg')  # 'tkAgg' if Qt not present
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation


class Pendulum:
    def __init__(self, theta1, theta2, dt):
        self.theta1 = theta1
        self.theta2 = theta2

        self.p1 = 0.0
        self.p2 = 0.0

        self.dt = dt

        self.g = 9.81
        self.length = 1.0

        self.trajectory = [self.polar_to_cartesian()]

    def polar_to_cartesian(self):
        x1 = self.length * np.sin(self.theta1)
        y1 = -self.length * np.cos(self.theta1)

        #x2 = x1 + self.length * sp.sin(self.theta2)
        #y2 = y1 - self.length * sp.cos(self.theta2)

        print(self.theta1, self.theta2)
        return np.array([[0.0, 0.0], [x1, y1]])

    def evolve(self):
        theta1 = self.theta1
        theta2 = self.theta2
        p1 = self.p1
        p2 = self.p2
        g = self.g
        l = self.length

        expr1 = np.cos(theta1 - theta2)
        expr2 = np.sin(theta1 - theta2)
        expr3 = (1 + expr2 ** 2)
        expr4 = p1 * p2 * expr2 / expr3
        expr5 = (p1 ** 2 + 2 * p2 ** 2 - p1 * p2 * expr1) \
                * np.sin(2 * (theta1 - theta2)) / 2 / expr3 ** 2
        expr6 = expr4 - expr5

        self.theta1 += self.dt * (p1 - p2 * expr1) / expr3
        self.theta2 += self.dt * (2 * p2 - p1 * expr1) / expr3
        self.p1 += self.dt * (-2 * g * l * np.sin(theta1) - expr6)
        self.p2 += self.dt * (-g * l * np.sin(theta2) + expr6)

        new_position = self.polar_to_cartesian()
        self.trajectory.append(new_position)
        print(new_position)
        return new_position


class Animator:
    def __init__(self, pendulum, draw_trace=False):
        self.pendulum = pendulum
        self.draw_trace = draw_trace
        self.time = 0.0

        # set up the figure
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim(-2.5, 2.5)
        self.ax.set_xlim(-2.5, 2.5)

        # prepare a text window for the timer
        self.time_text = self.ax.text(0.05, 0.95, '',
                                      horizontalalignment='left',
                                      verticalalignment='top',
                                      transform=self.ax.transAxes)

        # initialize by plotting the last position of the trajectory
        self.line, = self.ax.plot(
            self.pendulum.trajectory[-1][:, 0],
            self.pendulum.trajectory[-1][:, 1],
            marker=(3, 0, 180))

        # trace the whole trajectory of the second pendulum mass
        if self.draw_trace:
            self.trace, = self.ax.plot(
                [a[1][0] for a in self.pendulum.trajectory],
                [a[1][1] for a in self.pendulum.trajectory])

    def advance_time_step(self):
        while True:
            self.time += self.pendulum.dt
            yield self.pendulum.evolve()

    def update(self, data):
        self.time_text.set_text(f'Elapsed time: {round(self.time, 2)} s')

        self.line.set_ydata(data[:, 1])
        self.line.set_xdata(data[:, 0])

        if self.draw_trace:
            self.trace.set_xdata([a[1, 0] for a in self.pendulum.trajectory])
            self.trace.set_ydata([a[1, 1] for a in self.pendulum.trajectory])
        return self.line,

    def animate(self):
        self.animation = animation.FuncAnimation(self.fig, self.update,
                                                 self.advance_time_step, interval=25, blit=False)


pendulum = Pendulum(theta1=np.pi, theta2=np.pi - 0.01, dt=0.01)
animator = Animator(pendulum=pendulum, draw_trace=True)
animator.animate()
plt.show()
