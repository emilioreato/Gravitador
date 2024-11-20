from Engine import Engine


class Universe:

    G = 6.674*10**(-11)

    px_to_m_ratio = None

    time_scale = (4)*10**2

    universe_color = (5, 5, 5)

    def set_px_m_ratio_based_on_bodies(bodies, zoom=1.3):  # this lets you set the bounders based on the particles in screen. zoom set as -20% (1.2)
        max_x = max(abs(body.x) for body in bodies.values())
        max_y = max(abs(body.y) for body in bodies.values())

        if max_x/Engine.window_width >= max_y/Engine.window_height:
            Universe.px_to_m_ratio = (2*max_x*zoom)/Engine.window_width
        else:
            Universe.px_to_m_ratio = (2*max_y*zoom)/Engine.window_height

    @staticmethod
    def pixels_to_meters(pos):
        return ((pos[0]-Engine.window_width / 2)*Universe.px_to_m_ratio, (pos[1]-Engine.window_height / 2)*Universe.px_to_m_ratio)

    @staticmethod
    def meters_to_pixels(pos):
        return (pos[0]/Universe.px_to_m_ratio+Engine.window_width / 2, pos[1]/Universe.px_to_m_ratio+Engine.window_height / 2)

    @staticmethod
    def scalar_pixels_to_meters(pixels):
        return pixels*Universe.px_to_m_ratio

    @staticmethod
    def scalar_meters_to_pixels(distance_module):
        return distance_module/Universe.px_to_m_ratio
