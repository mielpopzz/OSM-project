import overpass
import numpy as np
import smopy
import csv
import matplotlib.pyplot as plt
import math

api = overpass.API()

area = 'Московская область'  # <--area can be changed
station_response = api.get(f'area[name="{area}"];node(area)[railway=station];',
                           responseformat='csv(::id,::type,"name",::lat,::lon)')
station_lats = []
station_lons = []
for station in station_response[1:]:
    station_lats.append(float(station[-2]))
    station_lons.append(float(station[-1]))
station_lats = np.asarray(station_lats)
station_lons = np.asarray(station_lons)
rail_response = api.get(f'area[name="{area}"];way(area)[railway=rail][usage=main];(._;>;);', responseformat="json")
elements = rail_response['elements']
ways = [el for el in elements if 'type' in el and el['type'] == 'way']
nodes = [el for el in elements if 'type' in el and el['type'] == 'node']

nodes = {node['id']: node for node in nodes}
map = smopy.Map((np.min(station_lats), np.min(station_lons), np.max(station_lats), np.max(station_lons)), z=12)
ax = map.show_mpl(figsize=(8, 6))


# Рисуем пути
for way in ways:
    way_nodes_id = way['nodes']
    way_x = []
    way_y = []
    # Сохраняем набор точек, образующих путь
    for node_id in way_nodes_id:
        node = nodes[node_id]
        lat, lon = node['lat'], node['lon']
        x, y = map.to_pixels(lat, lon)
        way_x.append(x)
        way_y.append(y)
    ax.plot(way_x, way_y, color='green', linewidth=3)
# Рисуем станции
#for lat, lon in zip(station_lats, station_lons):
#    x, y = map.to_pixels(lat, lon)
#   ax.scatter(x, y, alpha=0.8, c="blue", edgecolors='none', s = 50)

    
g1 = []
i = 0
for w in ways:

    way_nodes_id = w['nodes']
    if "maxspeed" in w["tags"]:
        speed = w["tags"]["maxspeed"]
    else:
        speed = 90
    coord = []
    for node_id in way_nodes_id:
        node = nodes[node_id]
        lat, lon = node['lat'], node['lon']
        x, y = map.to_pixels(lat, lon)
        coord.append([x, y])
    g1.append([i, int(speed), coord])
    i += 1
g2 = []
for n in station_response:
    if n[0] != '@id':
        id = n[0]

        lat, lon = float(n[-2]), float(n[-1])
        x, y = map.to_pixels(lat, lon)

        g2.append([id, [x, y]])

for station in g2:

    x1, y1 = station[1]
    station.append([])

    for el in g1:
        h = 0
        for node in el[2]:
            x2, y2 = node
            dist = (x2 - x1) ** 2 + (y2 - y1) ** 2
            if dist < 500 and h == 0:
                station[2].append(el)
                h = 1

res = g2
d = []
d2 = []
l = []
t = 0
chek = 0
for i in range(0, len(res)):
    for j in range(0, len(res[i][2])):
        d2.append(res[i][2][j][0])
    d.append(d2)
    d2 = []
l2 = []
for i in range(0, len(d)):
    for j in range(0, len(d[i])):
        l2.append(-1)
    l.append(l2)
    l2 = []

for i in range(0, len(d)):
    for j in range(0, len(d[i])):
        for k in range(0, len(d)):
            for h in range(0, len(d[k])):
                if d[i][j] == d[k][h] and i != k:
                    l[i][j] = k

flug = 1
r1 = []
r2 = []
r3 = []
distances1 = []
for i in range(0, len(l)):
    for j in range(0, len(l[i])):
        if l[i][j] != -1:
            if flug == 1:
                r1.append(str(res[i][0]))
                flug = 0
            r3.append(str(res[l[i][j]][0]))
            r3.append(res[i][2][j][1])
            r2.append(r3)
            r3 = []
    flug = 1
    r1.append(r2)
    distances1.append(r1)
    r1 = []
    r2 = []

i = 0
k = 0
while [[]] in distances1:
    distances1.remove([[]])
node1 = {}
p = []
for i in range(0, len(distances1)):
    p.append(distances1[i][0])
node1 = set(p)
distances = {}
for i in range(0, len(distances1)):
    for j in range(0, len(distances1[i])):
        distances[distances1[i][0]] = dict(distances1[i][1])

current = res[len(res) // 2][0]
unvisited = {node: [0, current] for node in node1}  # using None as +inf
visited = {}
currentSave = current
currentDistance = [0, current]
unvisited[current] = currentDistance
minimumprev = 1000
while True:
    for neighbour, distance in distances[current].items():
        if neighbour not in unvisited: continue
        if distance < minimumprev:
            minimum = distance
        else:
            minimum = minimumprev
        if unvisited[neighbour][0] is None or unvisited[neighbour][0] < minimum:
            unvisited[neighbour][0] = minimum
            if current != neighbour:
                unvisited[neighbour][1] = current
    visited[current] = currentDistance
    del unvisited[current]
    if not unvisited: break
    k = 0
    candidates = [node for node in unvisited.items() if node[1]]
    current, currentDistance = sorted(candidates, key = lambda x: x[1], reverse=True)[0]
    minimumprev = unvisited[current][0]
print("--------------------------------------------------------------------------------")
print(visited)
print("--------------------------------------------------------------------------------")

dst = []
for i in visited:
    dst.append(0)
    cur = visited[f'{i}']
    while cur[0] != 0 and cur[1] != currentSave:
        dst[len(dst) - 1] += 1
        cur = visited[cur[1]]
    if cur[0] == 0 and cur[1] != currentSave:
        dst[len(dst) - 1] = 0
print(dst)
k = 0
for i in range(len(dst)):
    if dst[i] == max(dst):
        k = i
        break
k1 = 0
crt = ''
for i in visited:
    if k1 == k:
        crt = i
        break
    k1 += 1
print(f'{crt}')
for r in range(len(res)):
    if res[r][0] == f'{crt}':
        cur = res[r][0]

route = []
#cur = res[k][0]
curSave = cur
while cur != currentSave:
    route.append(cur)
    cur = visited[cur][1]
route.append(currentSave)
print(route)

node_lats = np.asarray([node['lat'] for id, node in nodes.items()])
node_lons = np.asarray([node['lon'] for id, node in nodes.items()])
'''
#
#print(nodes)
#2005745397
way_x = []
way_y = []
for k in range(len(route)):
    for i in range(len(res)):
        if res[i][0] == route[k]:
            way_x.append(res[i][1][0])
            way_y.append(res[i][1][1])
ax.plot(way_x, way_y, color='blue', linewidth=3)
'''
way_x = []
way_y = []
for t in range(len(route) - 1):
    save_ind = []
    for r in range(len(res)):
        if res[r][0] == route[t]:
            save_ind.append(r)
    for r in range(len(res)):
        if res[r][0] == route[t + 1]:
            save_ind.append(r)       
    print("--------------------------------------------------------------------------------")
    print(save_ind)
    print("--------------------------------------------------------------------------------")
    save_ind2 = 0           
    for i in range(len(res[save_ind[0]][2])):
        for j in range(len(res[save_ind[1]][2])):
            if res[save_ind[0]][2][i][0] == res[save_ind[1]][2][j][0]:
                save_ind2 = i
    way_x.append(res[save_ind[1]][1][0])
    way_y.append(res[save_ind[1]][1][1])
    for k in range(len(res[save_ind[0]][2][save_ind2][2])):
        way_x.append(res[save_ind[0]][2][save_ind2][2][k][0])
        way_y.append(res[save_ind[0]][2][save_ind2][2][k][1])    
    way_x.append(res[save_ind[0]][1][0])
    way_y.append(res[save_ind[0]][1][1])    
    ax.plot(way_x, way_y, color="violet", linewidth=3)    
    way_x = []
    way_y = []


for i in range(len(res)):
    if res[i][0] == curSave:
        x = res[i][1][0] 
        y = res[i][1][1] 
        continue
ax.scatter(x, y, alpha=0.8, c = "blue", edgecolors='none', s=100)
for i in range(len(res)):
    if res[i][0] == currentSave:
        x = res[i][1][0] 
        y = res[i][1][1] 
        continue
print(x)
print(y)

ax.scatter(x, y, alpha=0.8, c = "red", edgecolors='none', s=100)
plt.show()
