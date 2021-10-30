"""
Project: RadarBook
File: rectangular_aperture_example.py
Created by: Lee A. Harrison
On: 7/30/2018
Created with: PyCharm

Copyright (C) 2019 Artech House (artech@artechhouse.com)
This file is part of Introduction to Radar Using Python and MATLAB
and can not be copied and/or distributed without the express permission of Artech House.
"""
import sys
from Chapter03.ui.RectangularAperture_ui import Ui_MainWindow
from Libs.antenna.aperture import rectangular_uniform_ground_plane, rectangular_te10_ground_plane, \
    rectangular_uniform_free_space
from numpy import linspace, meshgrid, log10, sin, cos, amax, sqrt, degrees, finfo
from scipy.constants import pi
from PyQt5.QtWidgets import QApplication, QMainWindow
from matplotlib.backends.qt_compat import QtCore
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class RectangularAperture(QMainWindow, Ui_MainWindow):
    def __init__(self):

        super(self.__class__, self).__init__()

        self.setupUi(self)

        # Connect to the input boxes, when the user presses enter the form updates
        self.frequency.returnPressed.connect(self._update_canvas)
        self.width.returnPressed.connect(self._update_canvas)
        self.height.returnPressed.connect(self._update_canvas)
        self.antenna_type.currentIndexChanged.connect(self._update_canvas)
        self.plot_type.currentIndexChanged.connect(self._update_canvas)

        # Set up a figure for the plotting canvas
        fig = Figure()
        self.fig = fig
        self.axes1 = fig.add_subplot(111)
        self.my_canvas = FigureCanvas(fig)

        # Add the canvas to the vertical layout
        self.verticalLayout.addWidget(self.my_canvas)
        self.addToolBar(QtCore.Qt.TopToolBarArea, NavigationToolbar(self.my_canvas, self))

        # Update the canvas for the first display
        self._update_canvas()

    def _update_canvas(self):
        """
        Update the figure when the user changes an input value
        :return:
        """
        # Get the parameters from the form
        frequency = float(self.frequency.text())
        width = float(self.width.text())
        height = float(self.height.text())

        # Get the selected antenna from the form
        antenna_type = self.antenna_type.currentIndex()

        # Set the range and angular span
        r = 1.0e9

        # Set up the theta and phi arrays
        n = 200
        m = int(n/4)
        theta, phi = meshgrid(linspace(finfo(float).eps, 0.5 * pi, n), linspace(finfo(float).eps, 2.0 * pi, n))

        # Get the antenna parameters and antenna pattern for the selected antenna
        if antenna_type == 0:
            half_power_eplane, half_power_hplane, first_null_eplane, first_null_hplane = \
                rectangular_uniform_ground_plane.beamwidth(width, height, frequency)
            directivity = rectangular_uniform_ground_plane.directivity(width, height, frequency)
            sidelobe_level_eplane = rectangular_uniform_ground_plane.side_lobe_level()
            sidelobe_level_hplane = sidelobe_level_eplane
            _, et, ep, _, _, _ = rectangular_uniform_ground_plane.far_fields(width, height, frequency, r, theta, phi)
        elif antenna_type == 1:
            half_power_eplane, half_power_hplane, first_null_eplane, first_null_hplane = \
                rectangular_uniform_free_space.beamwidth(width, height, frequency)
            directivity = rectangular_uniform_free_space.directivity(width, height, frequency)
            sidelobe_level_eplane = rectangular_uniform_free_space.side_lobe_level()
            sidelobe_level_hplane = sidelobe_level_eplane
            _, et, ep, _, _, _ = rectangular_uniform_free_space.far_fields(width, height, frequency, r, theta, phi)
        else:
            half_power_eplane, half_power_hplane, first_null_eplane, first_null_hplane = \
                rectangular_te10_ground_plane.beamwidth(width, height, frequency)
            directivity = rectangular_te10_ground_plane.directivity(width, height, frequency)
            sidelobe_level_eplane, sidelobe_level_hplane = rectangular_te10_ground_plane.side_lobe_level()
            _, et, ep, _, _, _ = rectangular_te10_ground_plane.far_fields(width, height, frequency, r, theta, phi)

        # The the text boxes on the form to the correct values
        self.sll_eplane.setText('{:.2f}'.format(sidelobe_level_eplane))
        self.sll_hplane.setText('{:.2f}'.format(sidelobe_level_hplane))
        self.directivity.setText('{:.2f}'.format(directivity))

        # Remove the color bar
        try:
            self.cbar.remove()
        except:
            # Initial plot
            pass

        # Clear the axes for the updated plot
        self.axes1.clear()

        # U-V coordinates for plotting the antenna pattern
        uu = sin(theta) * cos(phi)
        vv = sin(theta) * sin(phi)

        # Normalized electric field magnitude for plotting
        e_mag = sqrt(abs(et * et + ep * ep))
        e_mag /= amax(e_mag)

        if self.plot_type.currentIndex() == 0:

            # Create the color plot
            im = self.axes1.pcolor(uu, vv, e_mag, cmap="jet", shading = 'auto')
            self.cbar = self.fig.colorbar(im, ax=self.axes1, orientation='vertical')
            self.cbar.set_label("Normalized Electric Field(V/m)")

            # Set the x- and y-axis labels
            self.axes1.set_xlabel("U (sines)", size=12)
            self.axes1.set_ylabel("V (sines)", size=12)

        elif self.plot_type.currentIndex() == 1:

            # Create the contour plot
            self.axes1.contour(uu, vv, e_mag, 20, cmap="jet", vmin=-0.2, vmax=1.0)

            # Turn on the grid
            self.axes1.grid(linestyle=':', linewidth=0.5)

            # Set the x- and y-axis labels
            self.axes1.set_xlabel("U (sines)", size=12)
            self.axes1.set_ylabel("V (sines)", size=12)

        else:

            # Create the line plot
            self.axes1.plot(degrees(theta[0]), 20.0 * log10(e_mag[m]), '', label='E Plane')
            self.axes1.plot(degrees(theta[0]), 20.0 * log10(e_mag[0]), '--', label='H Plane')

            # Set the y axis limit
            self.axes1.set_ylim(-60, 5)

            # Set the x and y axis labels
            self.axes1.set_xlabel("Theta (degrees)", size=12)
            self.axes1.set_ylabel("Normalized |E| (dB)", size=12)

            # Turn on the grid
            self.axes1.grid(linestyle=':', linewidth=0.5)

            # Place the legend
            self.axes1.legend(loc='upper right', prop={'size': 10})

        # Set the plot title and labels
        self.axes1.set_title('Rectangular Aperture Antenna Pattern', size=14)

        # Set the tick label size
        self.axes1.tick_params(labelsize=12)

        # Update the canvas
        self.my_canvas.draw()


def start():
    form = RectangularAperture()  # Set the form
    form.show()                   # Show the form


def main():
    app = QApplication(sys.argv)        # A new instance of QApplication
    form = RectangularAperture()        # Set the form
    form.show()                         # Show the form
    app.exec_()                         # Execute the app


if __name__ == '__main__':
    main()
