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
    __mouse_hover_pos = (0, 0)

    def __init__(self, width, height, title, model):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption(title)
        self.model = model
        self.__sim_scale = self.model.get_parameter_value("scale")

        ### gui ###
        self.__screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.__manager = pygame_gui.UIManager((width, height), "themes/default.json")
        self.gen_param_window((100, 100), self.__manager)

    def gen_param_window(self, pos, manager):

        # not great, not terrible
        label_width = 180
        input_width = 80
        gap_width = 10
        gap_depth = 10
        element_depth = 25
        window_width = 3 * gap_width + label_width + input_width
        window_height = 27 + gap_depth + (len(self.model.get_parameters()) + 3) * (gap_depth + element_depth)
  
        self.__container = pygame_gui.elements.UIWindow(
            rect = pygame.Rect(500, 10, window_width, window_height),
            manager = self.__manager,
            window_display_title = "parameters")

        # cell data, clean up
        info_width = 60
        self.__row_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(gap_width, gap_depth, info_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "row")
        self.__row = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(2 * gap_width + info_width, gap_depth, info_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = str(self.__mouse_hover_pos[0]))

        self.__col_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(3 * gap_depth + 2 * info_width, gap_depth, info_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "col")
        self.__col = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(4 * gap_width + 3 * info_width, gap_depth, info_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = str(self.__mouse_hover_pos[1]))

        self.__veg_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(gap_depth, 2 * gap_depth + element_depth, info_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "vegitation")
        self.__veg = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(2 * gap_width + info_width, 2 * gap_depth + element_depth, info_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "0")

        self.__hum_label = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(3 * gap_depth + 2 * info_width, 2 * gap_depth + element_depth, info_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "humidity")
        self.__hum = pygame_gui.elements.UILabel(
            relative_rect = pygame.Rect(4 * gap_width + 3 * info_width, 2 * gap_depth + element_depth, info_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "0")

        allowed_chars = [".", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        seq = lambda n: 2 * (gap_depth + element_depth) + (gap_depth + element_depth) * (n + 1) - element_depth 
        self.__inputs = {}
        for i, parameter in enumerate(self.model.get_parameters()):
            y = seq(i)
            self.__inputs[parameter] = {}
            self.__inputs[parameter]["label"] = pygame_gui.elements.UILabel(
                relative_rect = pygame.Rect(gap_width, y, label_width, element_depth),
                manager = self.__manager,
                container = self.__container,
                text = self.model.get_parameter_title(parameter))
            self.__inputs[parameter]["input"] = pygame_gui.elements.UITextEntryLine(
                relative_rect = pygame.Rect(label_width + 2 * gap_width, y, input_width, element_depth),
                manager = self.__manager,
                container = self.__container)
            self.__inputs[parameter]["input"].set_text(str(self.model.get_parameter_value(parameter)))
            self.__inputs[parameter]["input"].set_allowed_characters(allowed_chars)

        self.__update_params_button = pygame_gui.elements.UIButton(
            relative_rect = pygame.Rect(window_width - (input_width + gap_width), seq(len(self.model.get_parameters())), input_width, element_depth),
            manager = self.__manager,
            container = self.__container,
            text = "update")
    
    def update_model_parameters(self):
        for parameter in self.model.get_parameters():
            typeStr = self.model.get_parameter_type(parameter)
            valueStr = self.__inputs[parameter]["input"].get_text()
            self.model.set_parameter_value(parameter, int(valueStr) if typeStr == "int" else float(valueStr)) 

    def reset_surface(self):
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
                    self.set_state(row, col, self.model.STATE_IGNITION, self.model.get_parameter_value("max_ignition_time"))
        elif event.type == pygame.MOUSEBUTTONUP:
            self.__mouse_down = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            col = int((mouse_pos[0] - self.__sim_origin[0]) / self.__sim_scale)
            row = int((mouse_pos[1] - self.__sim_origin[1]) / self.__sim_scale)
            if self.model.is_valid_range(row, col) and (row, col) != self.__mouse_hover_pos:
                self.__mouse_hover_pos = (row, col)
                self.__row.set_text(str(row))
                self.__col.set_text(str(col))
                self.__veg.set_text(str(self.model.get_state_veg_density(row, col)))
                self.__hum.set_text(str(self.model.get_state_veg_humidity(row, col)))
            if self.__mouse_down:
                mouse_delta = (mouse_pos[0] - self.__mouse_pos[0], mouse_pos[1] - self.__mouse_pos[1])
                self.__sim_origin = (self.__sim_origin[0] + mouse_delta[0], self.__sim_origin[1] + mouse_delta[1])
            self.__mouse_pos = mouse_pos
        elif event.type == pygame.MOUSEWHEEL:
            self.__sim_scale = max(1, self.__sim_scale - event.y)
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
            delta = clock.tick(40)
            self.model.reset_modified()
            self.process_events()
            self.update_sim(delta)
            self.__manager.update(delta * 0.001)
            self.__screen.fill("black")
            self.__screen.blit(self.__render_surface, self.__sim_origin)
            self.__manager.draw_ui(self.__screen)
            pygame.display.flip()
        pygame.quit()

