import numpy as np
import os

print(os.getcwd())

def draw_wind_direction_arrow(ax, x_coord, direction, y_offset=1.1, arrow_length=0.25):
    # Mapping mellom vindretninger og grader i meteorologisk konvensjon
    direction_to_angle = {
        "N": 0,
        "NNØ": 22.5,
        "NØ": 45,
        "ØNØ": 67.5,
        "Ø": 90,
        "ØSØ": 112.5,
        "SØ": 135,
        "SSØ": 157.5,
        "S": 180,
        "SSV": 202.5,
        "SV": 225,
        "VSV": 247.5,
        "V": 270,
        "VNV": 292.5,
        "NV": 315,
        "NNV": 337.5,
    }

    if direction not in direction_to_angle:
        print(f"Ukjent retning: {direction}")
        return None

    wind_direction_angle = direction_to_angle[direction]

    # Juster vinkelen for matplotlibs koordinatsystem
    matplotlib_angle_deg = (270 - wind_direction_angle) % 360
    matplotlib_angle = np.deg2rad(matplotlib_angle_deg)

    # Debug-utskrift
    #print(f"Retning: {direction}, Vinkel (meteorologisk): {wind_direction_angle}°, Vinkel (matplotlib): {matplotlib_angle_deg}°")


    # Beregn dx og dy
    dx = arrow_length * np.cos(matplotlib_angle)
    dy = arrow_length * np.sin(matplotlib_angle)

    # Tegn pilen
    annotation = ax.annotate(
        '',
        xy=(x_coord + dx, y_offset + dy),
        xytext=(x_coord, y_offset),
        xycoords=('data', 'axes fraction'),
        textcoords=('data', 'axes fraction'),
        arrowprops=dict(arrowstyle='->', color='black'),
        ha='center',
        va='center',
        annotation_clip=False
    )
    ax.text(
        x_coord,
        y_offset + dy + 0.05,  # Juster posisjonen etter behov
        direction,
        ha='center',
        va='bottom',
        fontsize=8,
        rotation=0,
        transform=ax.get_xaxis_transform()
    )
    return annotation
