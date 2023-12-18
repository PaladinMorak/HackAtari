'''
curved_space_invaders.py implements a altered version of SpaceInvaders, in which the laser shoots 
in a parabolic curve instead of a straight line. 
'''

from time import sleep
import torch
import cv2
import pygame
import numpy as np
import gymnasium as gym
from ocatari.core import OCAtari, DEVICE
from ocatari.utils import load_agent

TOGGLE_HUMAN_MODE = 'False'
"""
A constant that toggles the state of the agent mode.

This constant is used to toggle between the human mode and the agent mode. 
The value 'True' indicates that the human mode is active, while the value
'False' indicates that the agent mode is active.
"""

class CurvedSpaceInvaders(OCAtari):
    '''
    CurvedSpaceInvaders: Enables agent play mode for the CurvedSpaceInvaders game.
    Modifies the Atari game "Space Invaders" such that the laser shoots in 
    a parabolic fashion instead of a straight line. The direction of the shooting curve is 
    dependend of the current position on the playing field.
    '''

    def __init__(self, env_name="SpaceInvaders-v4", mode="revised",
                 hud=True, obs_mode="dqn", *args, **kwargs):
        '''
        Initializes an OCAtari game environment with preset values for game name, mode, and 
        observation mode. The Heads-Up Display (HUD) is enabled by default.
        '''
        self.render_mode = kwargs["render_mode"] if "render_mode" in kwargs else None
        # Call __init__ to create the OCAtari environment
        super().__init__(env_name, mode, hud, obs_mode, *args, **kwargs)

    def alter_ram(self):
        '''
        alter_ram: Manipulates the RAM cell at position 87 to shift the position of
        the laser to the left or right. The direction is dependend of the current
        position on the playing field.
        The value in the cell is continually manipulated as long as the stored RAM values 
        are inside the defined boundaries.
        '''
        curr_laser_pos = self.get_ram()[87]
        # Manipulate the value in RAM cell 87 as long as the upper and the lower threshold
        # are not reached.
        if 40 < curr_laser_pos < 122:
            laser_displacement = calculate_x_displacement(curr_laser_pos)
            self.set_ram(87, laser_displacement)

    def _step_ram(self, *args, **kwargs):
        '''
        step_ram: Updates the environment by one RAM step.
        '''
        self.alter_ram()
        out = super()._step_ram(*args, **kwargs)
        return out

    def _fill_buffer_dqn(self):
        '''
        _fill_buffer_dqn: Fills the buffer for usage by the DQN agent.
        '''
        image = self._ale.getScreenGrayscale()
        state = cv2.resize(
            image, (84, 84), interpolation=cv2.INTER_AREA
        )
        self._state_buffer.append(torch.tensor(state, dtype=torch.uint8, device=DEVICE))

class CurvedSpaceInvadersHuman(OCAtari):
    '''
    CurvedSpaceInvadersHuman: Enables human play mode for the CurvedSpaceInvaders game.
    '''

    env: gym.Env

    def __init__(self, env_name: str):
        '''
        Initializes the CurvedSpaceInvadersHuman environment with the specified environment name.
        '''
        self.env = OCAtari(env_name, mode="revised", hud=True, render_mode="human",
                        render_oc_overlay=True, frameskip=1)
        self.env.reset()
        self.env.render()  # Initialize the pygame video system

        self.paused = False
        self.current_keys_down = set()
        self.keys2actions = self.env.unwrapped.get_keys_to_action()

    def run(self):
        '''
        run: Runs the CurvedSpaceInvadersHuman environment, allowing human interaction
        with the game.
        '''
        self.running = True
        while self.running:
            self._handle_user_input()
            if not self.paused:
                action = self._get_action()
                # Change RAM value
                curr_laser_pos = self.env.get_ram()[87]
                if 40 < curr_laser_pos < 122:
                    laser_displacement = calculate_x_displacement(curr_laser_pos)
                    self.env.set_ram(87, laser_displacement)
                self.env.step(action)
                self.env.render()
        pygame.quit()

    def _get_action(self):
        '''
        _get_action: Gets the action corresponding to the current key press.
        '''
        pressed_keys = list(self.current_keys_down)
        pressed_keys.sort()
        pressed_keys = tuple(pressed_keys)
        if pressed_keys in self.keys2actions.keys():
            return self.keys2actions[pressed_keys]
        else:
            return 0  # NOOP

    def _handle_user_input(self):
        '''
        _handle_user_input: Handles user input for the CurvedSpaceInvadersHuman environment.
        '''
        self.current_mouse_pos = np.asarray(pygame.mouse.get_pos())

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:  # Window close button clicked
                self.running = False

            elif event.type == pygame.KEYDOWN:  # Keyboard key pressed
                if event.key == pygame.K_p:  # 'P': Pause/Resume
                    self.paused = not self.paused

                if event.key == pygame.K_r:  # 'R': Reset
                    self.env.reset()

                elif (event.key,) in self.keys2actions.keys():  # Env action
                    self.current_keys_down.add(event.key)

            elif event.type == pygame.KEYUP:  # Keyboard key released
                if (event.key,) in self.keys2actions.keys():
                    self.current_keys_down.remove(event.key)

# calculates the x coordinate displacement based on a parabolic function
def calculate_x_displacement(current_x):
    '''
    calculate_x_displacement: calculates the displacement value based on a parabolic function
    and the current x position.
    '''
    if current_x < 81:
        x_out = -0.01 * current_x + current_x
    else:
        x_out = 0.01 * current_x + current_x
    x_out = int(np.round(x_out))
    return int(x_out)

# If statement for switching between human play mode and RL agent play mode
if TOGGLE_HUMAN_MODE == 'True':
    renderer = CurvedSpaceInvadersHuman('SpaceInvaders')
    renderer.run()
else:
    env = CurvedSpaceInvaders(render_mode="human")
    # The following path to the agent has to be modified according to individual user setup
    # and folder names
    dqn_agent = load_agent("../OC_Atari_master_HA_Testing/models/SpaceInvaders/dqn.gz",
                            env.action_space.n)
    env.reset()

    # Let the agent play the game for 10000 steps
    for i in range(10000):
        action = dqn_agent.draw_action(env.dqn_obs)
        _, _, done1, done2, _ = env.step(action)
        sleep(0.01)
        if done1 or done2:
            env.reset()
