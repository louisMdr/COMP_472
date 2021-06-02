#    function reconstruct_path(cameFrom, current)
#       total_path := {current}
#       while current in cameFrom.Keys:
#           current := cameFrom[current]
#           total_path.prepend(current)
#       return total_path

# note: if start is at a playground tile, display "no path is found"

# note: if at any point the MIN of the 4 edges is infinite, then return
# "Path has reached a cost of infinite value, no solution path found"

# setting the value for each edge (based on the above tile values):
# for each edge:
#      if tile_two is set: edge_cost=AVG(tile_one+tile_two).. otherwise the edge cost is just that of tile_one

# setting the h_value of each node:
# for each n in nodelist...
#      go thru all its edges and take the min edge-cost
#      substract 1 from it... + abs(node_x - end_point[x]) + (abs(node_y - end_point[y])), and this gives the h_value


# //then we proceed with the A* Algorithm
# while end point is playground  { run the A* algo below}


# def A_Star_RoleP(graph: Map, start_point: Node, end_point:Node, h)
#     # solution_path_cost = 0
#     # if start_point is a Playground --> return "Arrived at destination, cost: 0, path {start_point}"
#
#     # elif start point is inside a tile (ie: x and y are decimals), we go to the nearest node
#       by walking horizontally once and vertically once at a total cost of (tile_value)*2 :
#       ==> to see if x and y are decimal: if ( !(x-int(x) == 0) AND !(y-int(y) ==0) )
#           print('start point is inside tile {tile #}:
#           print('  Moving {"left" (if (x-int(x))<0.5) or "right" if (x-int(x)>=0.5) }
#                    from x: (start_x) to x: (start_x.round()), at cost of (tile_type.value)
#                    and moving {"up" if y-int(y)>-0.5 or "down" if (y-int(y)<= -0.5))
#                    from y: (start_y) to y: (start_y.round()), at cost of (tile_type.value)  ')
#
#         # new starting point = (x.round(),y.round()) coordinate of the start_point
#
#         # g_value of the current node (starting node) = tile_type.value *2
#
#     #elif start point is on a vertical edge between 2 nodes, we go to the nearest node on that edge
#       ==> elif ( !(y-int(y) == 0)):
#                  new_y_coordinate = round(y)
#           print('  Moving {"up" if y-int(y)>-0.5 or "down" if (y-int(y)<= -0.5))
#                    from y: (start_y) to y: (start_y.round()), at cost of (edge_cost)  ')

#           new starting point = (x,y.round())
#
#           g_value of the current node (starting node) = edge_cost of the edge we just traversed
#
#    #elif start point is on a horizontal edge between 2 nodes, we go to the nearest node on that edge
#       ==> elif ( !(x-int(x) == 0)):
#                  new_x_coordinate = round(x)
#           print('  Moving {"left" (if (x-int(x))<0.5) or "right" if (x-int(x)>=0.5) }
#                    from x: (start_x) to x: (start_x.round()), at cost of (edge_cost) ')
#
#           new starting point = (x.round(),y)
#
#           g_value of the current node (starting node) = edge_cost of the edge we just traversed
#
#    #else (x,y)=(x,y) //leave as is
#
#    --------- same thing for the endpoint (if in a grid --> update to the closest node),
#              except we don't add the cost to the g_value but to another variable which we
#              will consider when displaying the final cost. Also we keep the print(f') in a string baraible
#              which we will display at the end. ---------
#
#
#     // So we have our updated starting point and the accumulated cost so far stored as the g_value of the curr node...
#     // We can start the algorithm..
#
#     // First we create an open list for the nodes that have been expanded but not yet visited.
#     // This is implemented as a list of nodes, where the node with lowest f(n) will be selected at every iteration
#     // Initially, only the start node is known.
#     openlist = [start]
#
#     //note: for each node we keep track of the preceding node (see Node attribute preceding_node),
#     //      this way we can back-track every node once we hit the end_point and get the solution path
#
#     //note: g_value is the path cost from start_point to current node
#     //      which is equal to the g value of the preceding node + the cost of the edge taken
#
#
#  #     gScore := map with default value of Infinity
#  #     gScore[start_point] := 0
#  #
#  #     // For node n, fScore[n] := gScore[n] + h(n). fScore[n] represents our current best guess as to
#  #     // how short a path from start to finish can be if it goes through n.
#  #     fScore := map with default value of Infinity
#  #     fScore[start_point] := h(start_point)
#  #
#
#     while openlist is not empty
#         current_node = the node in the openlist with the lowest f_value
#         if current = end_point
#             print(f' total cost is {current node g_value}')
#             print(f' solution path is: {reconstruct_path(cameFrom, current)}')
#
#         openlist.Remove(current)
#         neighbor_f_value={}
#         for each neighbor of current
#             tentative_g_value of neighbor = g_value of current + edge cost between current and neighbor
#             if  tentative_g_value < actual_g_value of neighbor (//then this path is shorter, therefore:)
#                  preceding_node of neighbor = current node
#
#             f_value of neighbor = g_value + neighbor node h_value
#             add the neighbor node with its f_value in the dict neighbor_f_value
#         take the node with the lowest neighbor_f_value
#
#             // d(current,neighbor) is the weight of the edge from current to neighbor
#             if tentative_gScore < gScore[neighbor]
#                 // This path to neighbor is better than any previous one. Record it!
#                 cameFrom[neighbor] := current
#                 gScore[neighbor] := tentative_gScore
#                 fScore[neighbor] := gScore[neighbor] + h(neighbor)
#                 if neighbor not in openlist
#                     openlist.add(neighbor)
#
#     // Open set is empty but end_point was never reached
#     return failure
#