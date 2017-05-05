import math

from . import grid

class Body(grid.Body):
    def go_in_direction(self, dir, distance=1, return_obstacle=False):

        dir1=int(dir)
        dir2=(dir1+1)%self.world.directions

        dx1, dy1 = self.world.get_offset_in_direction(self.cell.x, self.cell.y, dir1)
        dx2, dy2 = self.world.get_offset_in_direction(self.cell.x, self.cell.y, dir2)

        scale=dir % 1

        x = self.x + distance*(dx2*scale + dx1*(1 - scale))
        y = self.y + distance*(dy2*scale + dy1*(1 - scale))

        closest = self.cell
        dist = (x-self.cell.x)**2 + (y-self.cell.y)**2
        for n in self.cell.neighbour:
            d = (x-n.x)**2 + (y-n.y)**2
            if d<dist:
                closest = n
                dist = d
        if closest is not self.cell:
            if closest.wall:
                if return_obstacle:
                    return closest
                else:
                    return False
            else:
                self.cell=closest

        self.x=x
        self.y=y

        if return_obstacle:
            return None
        else:
            return True

    def go_forward(self, distance=1):
        return self.go_in_direction(self.dir, distance=distance)

    def go_backward(self, distance=1):
        return self.go_in_direction(self.dir, distance=-distance)

    def detect(self, direction, max_distance=None):
        start_x = self.x
        start_y = self.y
        cell = self.cell
        distance = 0.0
        delta = 1.0
        min_delta = 1.0 / 64
        obstacle = None
        if max_distance is None:
            max_distance = self.world.width + self.world.height

        while distance < max_distance:
            obstacle = self.go_in_direction(direction, delta, return_obstacle=True)
            if obstacle is None:
                distance += delta
            elif delta > min_delta:
                delta = delta / 2
            else:
                distance = math.sqrt((start_x-self.x)**2 + (start_y-self.y)**2)
                break
        self.cell = cell
        self.x = start_x
        self.y = start_y
        return distance, obstacle
