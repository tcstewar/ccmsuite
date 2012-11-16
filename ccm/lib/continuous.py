import grid

class Body(grid.Body):
    def go_in_direction(self, dir, distance=1):
    
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
                return False
            else:
                self.cell=closest
            
        self.x=x
        self.y=y

        return True

    def go_forward(self, distance=1):
        return self.go_in_direction(self.dir, distance=distance)

    def go_backward(self, distance=1):
        return self.go_in_direction(self.dir, distance=-distance)
