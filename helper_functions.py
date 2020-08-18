from ipywidgets import *
from ipycanvas import Canvas
import IPython
from math import pi
import datetime
import xnat
import csv

class Scanner:
    def __init__(self, num):
        self.num = int(num)

        self.gsr_x_points = []
        self.gsr_y_points = []
        self.tsnr_points = []

    def __repr__(self):
        return str(self.num)

class Point:
    def __init__(self, x, y, name = None):
        self.x = x
        self.y = y

        self.name = name

    def __str__(self):
        return str('(%s, %s)' % (str(self.x), str(self.y)))

class Date:
    def __init__(self, date):
        self.year = date[:4]
        self.month = date[4:6]
        self.day = date[6:8]

    def __str__(self):
        return '%s-%s-%s' % (self.year, self.month, self.day)

    def __int__(self):
        return int(datetime.datetime.strptime(str(self), '%Y-%m-%d').timestamp())

class Line:
    def __init__(self, points, label, point_color = 'blue', line_color = 'blue'):
        points.sort(key = point_sort)

        self.points = points

        self.label = label

        self.point_color = point_color
        self.line_color = line_color

        self.x = [float(point.x) for point in self.points]
        self.y = [int(point.y) for point in self.points]

        self.screen_points = []

        self.maxx = max(self.x)
        self.minx = min(self.x)

        self.maxy = max(self.y)
        self.miny = min(self.y)

    def save_state(self, canvas, graph):
        global mousex, mousey

        if not len(self.screen_points) > 0:
            for point in self.points:
                canvas.fill_style = self.point_color

                xpos, ypos = graph.get_screen_point(point, canvas)

                if self.points.index(point) == 0:
                    canvas.begin_path()
                    canvas.move_to(xpos, ypos)
                    canvas.line_to(xpos, ypos)
                else:
                    canvas.line_to(xpos, ypos)

            canvas.stroke_style = self.line_color
            canvas.stroke()

            for point in self.points:
                canvas.fill_style = self.point_color

                xpos, ypos = graph.get_screen_point(point, canvas)

                self.screen_points.append(Point(xpos, ypos, name = point.name))

                canvas.fill_style = self.point_color
                canvas.fill_arc(xpos, ypos, 4, 0, 2 * pi)

                if abs(graph.mousex - xpos) < 10 and abs(graph.mousey - ypos) < 10:
                    canvas.font = 'bold 15px arial'
                    canvas.fill_style = 'black'
                    canvas.text_align = 'left'
                    canvas.text_baseline = 'middle'
                    canvas.fill_text('(%s, %f)' % (str(point.y), round(float(point.x), 5)), xpos + 8, ypos)

    def show(self, canvas, graph):
        for point in self.screen_points:
            if abs(graph.mousex - point.x) < 10 and abs(graph.mousey - point.y) < 10:
                canvas.font = 'bold 15px arial'
                canvas.fill_style = 'black'
                canvas.text_align = 'left'
                canvas.text_baseline = 'middle'
                canvas.fill_text('(%s, %f)' % (str(self.points[self.screen_points.index(point)].y), round(float(self.points[self.screen_points.index(point)].x), 5)), point.x + 8, point.y)


class Graph:
    def __init__(self, title, get_link = None):
        self.lines = []

        self.title = title

        self.get_link = get_link

        self.maxx = 0
        self.minx = 0
        self.maxy = 0
        self.miny = 0

        self.markers = []

        self.canvas = Canvas(width = 950, height = 500)
        self.graph_canvas = Canvas(width = 950, height = 500)

        self.mousex = 0
        self.mousey = 0

        self.highlighted_point = None

    def add_line(self, line):
        self.lines.append(line)

        maxxs = [line.maxx for line in self.lines]
        minxs = [line.minx for line in self.lines]
        maxys = [line.maxy for line in self.lines]
        minys = [line.miny for line in self.lines]

        self.maxx = max(maxxs)
        self.minx = min(minxs)
        self.maxy = max(maxys)
        self.miny = min(minys)

    def save_state(self):
        self.canvas.on_mouse_move(self.mouse_move)
        self.canvas.on_mouse_down(self.mouse_press)

        for line in self.lines:
            line.save_state(self.graph_canvas, self)

        for line in self.lines:
            self.graph_canvas.fill_style = 'black'
            self.graph_canvas.text_align = 'center'
            self.graph_canvas.text_baseline = 'middle'
            self.graph_canvas.font = '15px arial'
            ypos = 75 + (35 * self.lines.index(line))
            self.graph_canvas.fill_text(line.label, self.graph_canvas.width - 75, ypos)

            self.graph_canvas.stroke_style = line.line_color
            self.graph_canvas.begin_path()
            self.graph_canvas.move_to(self.graph_canvas.width - 100, ypos + 15)
            self.graph_canvas.line_to(self.graph_canvas.width - 50, ypos + 15)
            self.graph_canvas.stroke()

            self.graph_canvas.fill_style = line.point_color
            self.graph_canvas.fill_arc(self.graph_canvas.width - 75, ypos + 15, 4, 0, 2 * pi)

        self.graph_canvas.stroke_style = 'black'
        self.graph_canvas.stroke_rect(self.graph_canvas.width - 130, 50, 110, 25 + 35 * len(self.lines))

        self.graph_canvas.begin_path()
        self.graph_canvas.move_to(75, 0)
        self.graph_canvas.line_to(75, self.graph_canvas.height - 25)
        self.graph_canvas.line_to(self.graph_canvas.width - 25, self.graph_canvas.height - 25)
        self.graph_canvas.stroke_style = 'black'
        self.graph_canvas.stroke()

        self.graph_canvas.fill_style = 'black'
        self.graph_canvas.text_align = 'center'
        self.graph_canvas.text_baseline = 'middle'
        self.graph_canvas.font = 'bold 20px arial'
        self.graph_canvas.fill_text(self.title, self.graph_canvas.width / 2, 10)

        for marker in range(10):
            valuex = self.minx + ((self.maxx - self.minx) / 10) * marker
            decimals = str(valuex)[::-1].find('.')
            valuex = round(valuex, int(decimals / 3))
            valuey = int(self.miny + ((self.maxy - self.miny) / 10) * marker)

            pos_x, pos_y = self.get_screen_point(Point(valuex, valuey), self.graph_canvas)

            self.markers.append([Point(pos_x, pos_y), Point(valuex, valuey)])

            self.graph_canvas.begin_path()
            self.graph_canvas.move_to(70, pos_y)
            self.graph_canvas.line_to(80, pos_y)
            self.graph_canvas.stroke()

            self.graph_canvas.begin_path()
            self.graph_canvas.move_to(pos_x, self.graph_canvas.height - 20)
            self.graph_canvas.line_to(pos_x, self.graph_canvas.height - 30)
            self.graph_canvas.stroke()

            self.graph_canvas.font = '12px arial'
            self.graph_canvas.fill_style = 'black'
            self.graph_canvas.text_align = 'right'
            self.graph_canvas.text_baseline = 'middle'
            self.graph_canvas.fill_text(valuex, 70, pos_y)
            self.graph_canvas.text_align = 'center'
            self.graph_canvas.text_baseline = 'top'
            self.graph_canvas.fill_text(datetime.datetime.fromtimestamp(valuey).strftime('%m/%d/%Y'), pos_x, self.graph_canvas.height - 20)

    def show(self):
        self.canvas.draw_image(self.graph_canvas, 0, 0)

        for line in self.lines:
            line.show(self.canvas, self)

    def get_screen_point(self, point, canvas):
        ypos = canvas.height - (float(point.x) - self.minx) * ((canvas.height - 100) / (self.maxx - self.minx)) - 75
        xpos = (int(point.y) - self.miny) * ((canvas.width - 250) / (self.maxy - self.miny)) + 75
        return xpos, ypos

    def mouse_move(self, x, y):
        self.mousex, self.mousey = int(x), int(y)

        if self.highlighted_point:
            if not abs(self.mousex - self.highlighted_point.x) < 10 and abs(self.mousey - self.highlighted_point.y) < 10:
                self.canvas.clear_rect(0, 0, self.canvas.width, self.canvas.height)
                self.highlighted_point = None
                self.show()

        for line in self.lines:
            for point in line.screen_points:
                if abs(self.mousex - point.x) < 10 and abs(self.mousey - point.y) < 10:
                    if not point == self.highlighted_point:
                        self.highlighted_point = point
                        self.canvas.clear_rect(0, 0, self.canvas.width, self.canvas.height)
                        self.show()

    def mouse_press(self, x, y):
        self.mousex, self.mousey = int(x), int(y)

        for line in self.lines:
            for point in line.screen_points:
                if abs(self.mousex - point.x) < 10 and abs(self.mousey - point.y) < 10:
                    if self.get_link:
                        display(IPython.display.Javascript('''
                            window.location.replace({url})
                        ''')).format(url = self.get_link(point.name))
                        self.canvas.clear_rect(0, 0, self.canvas.width, self.canvas.height)
                        self.show()



def point_sort(point):
    return int(point.y)

def get_date(row_id):
    for char_index in range(len(row_id)):
        if row_id[char_index: char_index + 4] == 'ses-':
            return Date(row_id[char_index + 4: char_index + 12])
