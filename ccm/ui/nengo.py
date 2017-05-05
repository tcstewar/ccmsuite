from __future__ import absolute_import
import nengo

class GridNode(nengo.Node):
    def __init__(self, world, dt=0.001):
        def svg(t):
            last_t = getattr(svg, '_nengo_html_t_', None)
            if last_t is not None and t <= last_t:
                last_t = None
            if last_t is None or t >= last_t + dt:
                svg._nengo_html_ = self.generate_svg(world)
                svg._nengo_html_t_ = t
        super(GridNode, self).__init__(svg)

    def generate_svg(self, world):
        cells = []
        for i in range(world.width):
            for j in range(world.height):
                cell = world.get_cell(i, j)
                color = cell.color
                if callable(color):
                    color = color()
                if color is not None:
                    cells.append('<rect x=%d y=%d width=1 height=1 style="fill:%s"/>' %
                        (i, j, color))

        agents = []
        for agent in world.agents:
            direction = agent.dir * 360.0 / world.directions
            color = getattr(agent, 'color', 'blue')
            if callable(color):
                color = color()
            agent = ('<polygon points="0.25,0.25 -0.25,0.25 0,-0.5"'
                     ' style="fill:%s" transform="translate(%f,%f) rotate(%f)"/>'
                     % (color, agent.x+0.5, agent.y+0.5, direction))
            agents.append(agent)

        svg = '''<svg width="100%%" height="100%%" viewbox="0 0 %d %d">
            %s
            %s
            </svg>''' % (world.width, world.height,
                         ''.join(agents), ''.join(cells))

        return svg
