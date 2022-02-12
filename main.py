from random import seed
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor
from perlin_noise import PerlinNoise

app = Ursina()

window.color = color.rgb(0, 200, 211)
window.exit_button.enabled  = False

scene.fog_color = color.rgb(0, 222, 0)
scene.fog_density = 0.1

grass_stroke_texture = load_texture('grass_14.png')

def input(key):
	if key == 'escape':
		quit()

def update():
	pass

ground = Entity(model=None, collider=None)
noise = PerlinNoise(octaves=2, seed=2022)
amp = 6
freq = 24

ground_width = 32
for i in range(ground_width * ground_width):
	voxel = Entity(
		model='cube',
		color = color.green,
		parent=ground,
	)
	voxel.x = floor(i / ground_width)
	voxel.z = floor(i % ground_width)
	voxel.y = floor((noise([voxel.x / freq, voxel.z / freq])) * amp)

ground.combine()
ground.collider = 'mesh'
ground.texture = grass_stroke_texture

player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0.5
player.x = player.z = 5
player.y = 12

app.run()