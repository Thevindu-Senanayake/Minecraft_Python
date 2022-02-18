from random import randrange
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor, abs
import time
from perlin_noise import PerlinNoise
from Nmap import Nmap

app = Ursina()

window.color = color.rgb(0, 200, 211)
window.exit_button.enabled  = False

scene.fog_color = color.rgb(0, 222, 0)
scene.fog_density = 0 # TODO: set this back to 0.2

previous_time = time.time()

grass_stroke_texture = load_texture('grass_14.png')
mono_texture = load_texture('stroke_mono.png')
wire_texture = load_texture('wireframe.png')
stone_texture = load_texture('grass_mono.png')

build_tool_entity = Entity(model='cube', texture=wire_texture)

class BlockType():
	STONE = color.rgb(255, 255, 255)
	GRASS = color.rgb(0, 255, 0)
	SOIL = color.rgb(255, 80, 100)
	RUBY = color.rgb(255, 0, 0)

block_type = BlockType.GRASS
build_mode = -1 # -1 off and 1 on

def buildTool():
	if build_mode == -1:
		build_tool_entity.visible = False
		return
	else: build_tool_entity.visible = True
	build_tool_entity.position = round(player.position + camera.forward * 3)
	build_tool_entity.y += 2
	build_tool_entity.x = round(build_tool_entity.x)
	build_tool_entity.y = round(build_tool_entity.y)
	build_tool_entity.z = round(build_tool_entity.z)
	build_tool_entity.color = block_type

def buildCube():
	e = duplicate(build_tool_entity)
	e.collider = 'cube'
	e.texture = stone_texture
	e.color = block_type
	e.shake(duration=0.5,speed=0.01)

def input(key):
	global block_type, build_mode
	if key == 'escape':
		quit()
	if key == 'g': generateSubset()

	if build_mode == 1:
		if key == 'left mouse up':
			buildCube()
		elif key == 'right mouse up':
			e = mouse.hovered_entity
			destroy(e)

		if key == '1': block_type = BlockType.STONE
		if key == '2': block_type = BlockType.GRASS
		if key == '3': block_type = BlockType.SOIL
		if key == '4': block_type = BlockType.RUBY

	if key == 'b': build_mode *= -1

def update():
	global previous_z, previous_x, previous_time, amp
	if abs(player.z - previous_z) > 1 or abs(player.x - previous_x) > 1:
		generateShell()

	if time.time() - previous_time > 0.05:
		generateSubset()
		previous_time = time.time()

	# Safety net in case of glitching through terrain
	if player.y < -amp + 1:
		player.y = player.height + floor((noise([player.x / freq, player.z / freq])) * amp)
		player.land()

	buildTool()

noise = PerlinNoise(octaves=4, seed=99)
amp = 24
freq = 100

terrain = Entity(model=None, collider=None)
terrain_width = 40
sub_width = int(terrain_width / 2)
subsets = []
subcubes = []
subcube_index = 0
current_subset = 0

# Create our 'ghost' subset cubes
for i in range(sub_width):
	box = Entity(model='Cube')
	subcubes.append(box)

# Create our empty subsets
for i in range(int((terrain_width ** 2) / sub_width)):
	box = Entity(model=None)
	box.parent = terrain
	subsets.append(box)

def generateSubset():
	global subcube_index, current_subset, freq, amp
	if current_subset >= len(subsets):
		finishterrain()
		return
	for i in range(sub_width):
		x = subcubes[i].x = floor((i + subcube_index) / terrain_width)
		z = subcubes[i].z = floor((i + subcube_index) % terrain_width)
		y = subcubes[i].y = floor((noise([x / freq, z / freq])) * amp)
		subcubes[i].parent = subsets[current_subset]

		# Set colour of subCube
		y = randrange(-4, 4)
		r = 0
		g = 0
		b = 0
		if y > amp*0.3:
			b = 255
		if y == 4:
			r = g = b = 255
		else:
			g = Nmap(y, 0, amp*0.5, 0, 255)
		# Red zone
		if z > terrain_width/2:
			r = Nmap(y, 0, amp*0.5, 110, 255)
			g = b = 0
		subcubes[i].color = color.rgb(r,g,b)
		subcubes[i].visible = False

	subsets[current_subset].combine(auto_destroy=False)
	# subsets[current_subset].texture = mono_texture
	subcube_index += sub_width
	current_subset += 1

terrain_finished = False
def finishterrain():
	global terrain_finished
	if terrain_finished==True: return
	terrain.texture = grass_stroke_texture
	terrain.combine()
	terrain_finished = True
	terrain.texture = grass_stroke_texture


# for i in range(terrain_width * terrain_width):
# 	voxel = Entity(
# 		model='cube',
# 		color = color.green,
# 		parent=terrain,
# 	)
# 	voxel.x = floor(i / terrain_width)
# 	voxel.z = floor(i % terrain_width)
# 	voxel.y = floor((noise([voxel.x / freq, voxel.z / freq])) * amp)

# terrain.combine()
# terrain.collider = 'mesh'
# terrain.texture = grass_stroke_texture

shell = []
shell_width = 3
for i in range(shell_width ** 2):
	voxel = Entity(model='cube', collider='box')
	voxel.visible = False
	shell.append(voxel)

def generateShell():
	global shell_width, freq, amp
	for i in range(len(shell)):
		x = shell[i].x = floor((i/shell_width) + player.x  - 0.5 * shell_width)
		z = shell[i].z = floor((i%shell_width) + player.z - 0.5 * shell_width)
		shell[i].y = floor((noise([x / freq, z / freq])) * amp)

player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0.5
player.x = player.z = 5
player.y = 12
previous_z = player.z
previous_x = player.x

generateShell()

app.run()