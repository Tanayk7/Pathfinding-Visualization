import time 

class Node():
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position
    
    def __repr__(self):
        return str(self.position)


def getGridPosition(scale,position):
    position = [position[0]*scale,position[1]*scale]
    return position

def astar(maze, start,end,allowDiagonals=False):
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
            
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            path.reverse()  # Return reversed path
            return path

        # Generate children
        children = []
        if(allowDiagonals):
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0),(1,1),(-1,1),(1,-1),(-1,-1)]: # Adjacent squares
                
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

                if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                    continue
                if maze[node_position[0]][node_position[1]] != 0:
                    continue
                if(Node(current_node,node_position) in closed_list):
                    continue

                new_node = Node(current_node, node_position)
                
                children.append(new_node)
        else:
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares
                    
                    node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

                    if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                        continue
                    if maze[node_position[0]][node_position[1]] != 0:
                        continue
                    if(Node(current_node,node_position) in closed_list):
                        continue

                    new_node = Node(current_node, node_position)
                    
                    children.append(new_node)
            

        # Loop through children
        for child in children:
            # Child is on the closed list
            for closed_child in closed_list:
                if(child == closed_child):
                    break
            
            else:
                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])
                child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g >= open_node.g:
                    break
            else:
            # Add the child to the open list
                open_list.append(child)
    else:
        return -1


def main():

    maze = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    start = (0, 0)
    end = (9, 9) 

    path = astar(maze, start, end)
    print(path)
    
   

if __name__ == '__main__':
    main()
