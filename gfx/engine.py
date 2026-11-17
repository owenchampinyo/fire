import pygame
import pygame_gui
from util.math import lerp 

#
# this class runs the simulation and handles all the imput and graphics
#
class GfxEngine:
    __running = False
    __sim_running = False
    __sim_origin = (0, 0)
    __mouse_down = False
    __mouse_pos = (0, 0)

    def __init__(self, width, height, title, model):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption(title)
        self.model = model
        self.__sim_scale = self.model.get_scale()
        
        ### gui ###
        self.__screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.__manager = pygame_gui.UIManager((width, height), "theme.json")
        
        container_width = 250
        container_height = 320

        self.__container = pygame_gui.elements.UIWindow(
            rect = pygame.Rect(550, 10, container_width, container_height),
            manager = self.__manager,
            window_display_title = "parameters")

        label_width = 180
        input_width = 50
        gap_width = 10
        gap_depth = 10
        element_depth = 25

        allowed_chars = [".", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

        level = 1 

        # not great, not terrible 
     
        self.__veg_prob_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(gap_width, gap_depth * level, label_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "vegitation probability")
        self.__veg_prob_input = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(label_width + gap_width, gap_depth * level, input_width, element_depth),
            manager = self.__manager,
            container = self.__container)
        self.__veg_prob_input.set_text(str(self.model.get_veg_probability()))
        self.__veg_prob_input.set_allowed_characters(allowed_chars)

        self.__veg_density_decay_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(gap_width, 45, label_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "vegitation density decay")
        self.__veg_density_decay_input = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(label_width + gap_width, 45, input_width, element_depth),
            manager = self.__manager,
            container = self.__container)
        self.__veg_density_decay_input.set_text(str(self.model.get_veg_density_decay()))
        self.__veg_density_decay_input.set_allowed_characters(allowed_chars)

        self.__veg_humidity_decay_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(gap_width, 80, label_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "vegitation humidity decay")
        self.__veg_humidity_decay_input = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(label_width + gap_width, 80, input_width, element_depth),
            manager = self.__manager,
            container = self.__container)
        self.__veg_humidity_decay_input.set_text(str(self.model.get_veg_humidity_decay()))
        self.__veg_humidity_decay_input.set_allowed_characters(allowed_chars)

        self.__mex_ignition_time_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(gap_width, 115, label_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "max ignition time")
        self.__max_ignition_time_input = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(label_width + gap_width, 115, input_width, element_depth),
            manager = self.__manager,
            container = self.__container)
        self.__max_ignition_time_input.set_text(str(self.model.get_max_ignition_time()))
        self.__max_ignition_time_input.set_allowed_characters(allowed_chars)

        self.__mex_fire_time_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(gap_width, 150, label_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "max fire time")
        self.__max_fire_time_input = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(label_width + gap_width, 150, input_width, element_depth),
            manager = self.__manager,
            container = self.__container)
        self.__max_fire_time_input.set_text(str(self.model.get_max_fire_time()))
        self.__max_fire_time_input.set_allowed_characters(allowed_chars)

        self.__wind_direction_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(gap_width, 185, label_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "wind direction")
        self.__wind_direction_input = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(label_width + gap_width, 185, input_width, element_depth),
            manager = self.__manager,
            container = self.__container)
        self.__wind_direction_input.set_text(str(self.model.get_wind_direction()))
        self.__wind_direction_input.set_allowed_characters(allowed_chars)

        self.__sun_angle_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(gap_width, 220, label_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "sun angle")
        self.__sun_angle_input = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(label_width + gap_width, 220, input_width, element_depth),
            manager = self.__manager,
            container = self.__container)
        self.__sun_angle_input.set_text(str(self.model.get_sun_angle()))
        self.__sun_angle_input.set_allowed_characters(allowed_chars)

        self.__update_params_button = pygame_gui.elements.UIButton(
            relative_rect = pygame.Rect(container_width - 90, 255, 80, 25),
            manager = self.__manager,
            container = self.__container,
            text = "update")
    
    def update_model_parameters(self):
        self.model.set_veg_probability(float(self.__veg_prob_input.get_text()))
        self.model.set_veg_density_decay(float(self.__veg_density_decay_input.get_text()))
        self.model.set_veg_humidity_decay(float(self.__veg_humidity_decay_input.get_text()))
        self.model.set_max_ignition_time(int(self.__max_ignition_time_input.get_text()))
        self.model.set_max_fire_time(int(self.__max_fire_time_input.get_text()))
        self.model.set_wind_direction(int(self.__wind_direction_input.get_text()))
        self.model.set_sun_angle(int(self.__sun_angle_input.get_text()))

    def reset_surface(self):
        #self.__sim_scale = self.model.get_scale()
        self.__surface = pygame.Surface((self.model.get_shape()[1], self.model.get_shape()[0]))
        lerper = lerp(self.model.get_min_height(), self.model.get_max_height())
        for row in range(self.model.get_shape()[0]):
            for col in range(self.model.get_shape()[1]):
                state = self.model.get_full_state(row, col)
                color = "blue"
                if state[0] == self.model.STATE_VEGITATION:
                    color = pygame.Color(0, int(20 + 235 * (1 - self.model.get_state_veg_density(row, col))), 0)
                elif state[0] == self.model.STATE_NOTHING:
                    shade = lerper(self.model.get_height(row, col))
                    color = pygame.Color(int(255 * shade), int(255 * shade), int(255 * shade))
                self.__surface.set_at((col, row), color)

    def scale_surface(self):
        rect = (self.__surface.get_width() * self.__sim_scale, self.__surface.get_height() * self.__sim_scale)
        self.__render_surface = pygame.transform.scale(self.__surface, rect)

    def process_game_events(self, event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:
                self.__running = False
            if event.key == pygame.K_s:
                self.__sim_running = not self.__sim_running
            if event.key == pygame.K_r:
                self.reset()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed(num_buttons = 3)[2] == 1:
                self.__mouse_down = True
                self.__mouse_pos = pygame.mouse.get_pos()
            elif pygame.mouse.get_pressed(num_buttons = 3)[0] == 1:
                mouse_pos = pygame.mouse.get_pos()
                col = int((mouse_pos[0] - self.__sim_origin[0]) / self.__sim_scale)
                row = int((mouse_pos[1] - self.__sim_origin[1]) / self.__sim_scale)
                if self.model.is_valid_range(row, col):
                    self.set_state(row, col, self.model.STATE_IGNITION, self.model.get_max_ignition_time())
        elif event.type == pygame.MOUSEBUTTONUP:
            self.__mouse_down = False
        elif event.type == pygame.MOUSEMOTION and self.__mouse_down:
            mouse_pos = pygame.mouse.get_pos()
            mouse_delta = (mouse_pos[0] - self.__mouse_pos[0], mouse_pos[1] - self.__mouse_pos[1])
            self.__mouse_pos = mouse_pos
            self.__sim_origin = (self.__sim_origin[0] + mouse_delta[0], self.__sim_origin[1] + mouse_delta[1])
        elif event.type == pygame.MOUSEWHEEL:
            self.__sim_scale = max(1, self.__sim_scale + event.y)
            self.scale_surface()
    
    def process_window_events(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.__update_params_button:
                self.update_model_parameters()
                self.reset()

        return self.__manager.process_events(event) 

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
            elif event.type == pygame.VIDEORESIZE:
                self.__manager.set_window_resolution((self.__screen.get_width(), self.__screen.get_height()))
            elif not self.process_window_events(event):
                self.process_game_events(event)
     
    def set_surface(self, row, col, color):
        self.__surface.set_at((col, row), color)
        r = [col * self.__sim_scale, row * self.__sim_scale, self.__sim_scale, self.__sim_scale]
        pygame.draw.rect(self.__render_surface, color, r)

    def set_state(self, row, col, state, time_to_live):
        self.model.set_state(row, col, state, time_to_live)
        self.model.set_modified(row, col)
        if state == self.model.STATE_IGNITION:
            self.set_surface(row, col, "orange") 
        elif state == self.model.STATE_FIRE:
            self.set_surface(row, col, "red")
        elif state == self.model.STATE_BURNED:
            self.set_surface(row, col, "black")

    def update_sim(self, delta):
        if self.__sim_running:
            for row in range(self.model.get_rows()):
                for col in range(self.model.get_cols()):
                    state = self.model.get_state(row, col)
                    if not self.model.is_modified(row, col) and (state == self.model.STATE_IGNITION or state == self.model.STATE_FIRE):
                        state_time = self.model.get_state_time(row, col) + delta
                        state_time_to_live = self.model.get_state_time_to_live(row, col)
                        if state_time >= state_time_to_live:
                            state = self.model.STATE_BURNED
                            self.set_state(row, col, state, 0)
                        else:
                            self.model.update_state_time(row, col, state_time)
                            self.update(delta, row, col, self.model.get_valid_coordinates(row, col))
            self.model.reset_modified()
    
    def reset(self):
        self.model.init()
        self.reset_surface()
        self.scale_surface()
        
    def run(self):
        self.reset()
        self.__running = True
        clock = pygame.time.Clock()
        while self.__running:
            delta = clock.tick(60)
            self.model.reset_modified()
            self.process_events()
            self.update_sim(delta)
            self.__manager.update(delta * 0.001)
            self.__screen.fill("black")
            self.__screen.blit(self.__render_surface, self.__sim_origin)
            self.__manager.draw_ui(self.__screen)
            pygame.display.flip()
        pygame.quit()

