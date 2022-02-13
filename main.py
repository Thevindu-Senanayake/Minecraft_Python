from random import seed
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor, abs
import time
from perlin_noise import PerlinNoise

app = Ursina()

window.color = color.rgb(0, 200, 211)
window.exit_button.enabled  = False

scene.fog_color = color.rgb(0, 222, 0)
scene.fog_density = 0.02

previous_time = time.time()

grass_stroke_texture = load_texture('grass_14.png')

def input(key):
	if key == 'escape':
		quit()
	if key == 'g': generateSubset()

def update():
	global previous_z, previous_x, previous_time
	if abs(player.z - previous_z) > 1 or abs(player.x - previous_x) > 1:
		generateShell()

	if time.time() - previous_time > 0.05:
		generateSubset()
		previous_time = time.time()

	# Safety net in case of glitching through ground
	if player.y < -amp + 1:
		player.y = player.height + floor((noise([player.x / freq, player.z / freq])) * amp)
		player.land()

noise = PerlinNoise(octaves=2, seed=2022)
amp = 32
freq = 100

ground = Entity(model=None, collider=None)
ground_width = 100
sub_width = int(ground_width / 2)
subsets = []
subcubes = []
subcube_index = 0
current_subset = 0

# Create our 'ghost' subset cubes
for i in range(sub_width):
	box = Entity(model='Cube')
	subcubes.append(box)

# Create our empty subsets
for i in range(int((ground_width ** 2) / sub_width)):
	box = Entity(model=None)
	box.parent = ground
	subsets.append(box)

def generateSubset():
	global subcube_index, current_subset, freq, amp
	if current_subset >= len(subsets):
		finishGround()
		return
	for i in range(sub_width):
		x = subcubes[i].x = floor((i + subcube_index) / ground_width)
		z = subcubes[i].z = floor((i + subcube_index) % ground_width)
		y = subcubes[i].y = floor((noise([x / freq, z / freq])) * amp)
		subcubes[i].parent = subsets[current_subset]
		subcubes[i].color = color.green
		subcubes[i].visible = False

	subsets[current_subset].combine(auto_destroy=False)
	subsets[current_subset].texture = grass_stroke_texture
	subcube_index += sub_width
	current_subset += 1

ground_finished = False
def finishGround():
	global ground_finished
	if ground_finished==True: return
	application.pause()
	ground.combine()
	ground_finished = True
	player.y = 32
	ground.texture = grass_stroke_texture
	application.resume()


# for i in range(ground_width * ground_width):
# 	voxel = Entity(
# 		model='cube',
# 		color = color.green,
# 		parent=ground,
# 	)
# 	voxel.x = floor(i / ground_width)
# 	voxel.z = floor(i % ground_width)
# 	voxel.y = floor((noise([voxel.x / freq, voxel.z / freq])) * amp)

# ground.combine()
# ground.collider = 'mesh'
# ground.texture = grass_stroke_texture

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