import IPython
class Canvas:
    def __init__(self, width = 0, height = 0):
        self.width = width
        self.height = height

        self.stroke_style = ''
        self.fill_style = ''

        self.font = ''

        self.text_align = ''
        self.text_baseline = ''

        self.html = IPython.display.HTML(
            '''
              <canvas width = '{width}px' height = '{height}px' id = 'canvas'></canvas>
            '''.format(width = str(self.width), height = str(self.height))
        )

        self.javascript = IPython.display.Javascript('''
          var canvas = document.getElementById('canvas')
          var ctx = canvas.getContext('2d')
        ''')

        self.lines = []

        self.canvas = None

    def begin_path(self):
        self.javascript.data += '''
            ctx.beginPath()
        '''

    def move_to(self, x, y):
        self.javascript.data += '''
            ctx.moveTo(%d, %d)
        ''' % (x, y)

    def line_to(self, x, y):
        self.javascript.data += '''
            ctx.lineTo(%d, %d)
        ''' % (x, y)

    def stroke(self):
        self.javascript.data += '''
            ctx.stroke_style = %s
            ctx.stroke()
        ''' % (self.stroke_style)

    def fill_text(self, text, x, y):
        self.javascript.data += '''
            ctx.font = '{font}'
            ctx.fillStyle = '{fill}'
            ctx.textAlign = '{align}'
            ctx.textBaseline = '{baseline}'
            ctx.fillText('{text}', {x}, {y})
        '''.format(font = self.font, fill = self.fill_style, align = self.text_align, baseline = self.text_baseline, text = text, x = x, y = y)

    def fill_arc(self, x, y, r, start, end):
        self.javascript.data += '''
            ctx.beginPath()
            ctx.fillStyle = '{fill}'
            ctx.arc({x}, {y}, {r}, {start}, {end})
            ctx.fill()
        '''.format(fill = self.fill_style, x = x, y = y, r = r, start = start, end = end)

    def fill_rect(self, x, y, width, height):
        self.javascript.data += '''
              ctx.fillStyle = '{fill}'
              ctx.fillRect({x}, {y}, {width}, {height})
            '''.format(fill = self.fill_style, x = str(x), y = str(y), width = str(width), height = str(height))

    def draw_image(self, im, x, y):
        self.javascript.data += '''
            ctx.drawImage({im}, {x}, {y})
        '''.format(im = im, x = x, y = y)

    def get_canvas_from_javascript(self, canvas):
        self.canvas = canvas

    def get_canvas(self):
        google.colab.output.register_callback('get_canvas_from_javascript', get_canvas)

        IPython.display.Javascript(
        '''
            canvas = document.getElementById('canvas')
            google.colab.kernel.invokeFunction('get_canvas', [canvas])
        '''
        )

    def __call__(self):
        display(self.html)
        display(self.javascript)
