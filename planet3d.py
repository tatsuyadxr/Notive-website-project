import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LightSource

def create_planet_3d(planet_type='earth', rotation=0, save_fig=False):
    """
    Create a 3D visualization of a planet.
    
    Parameters:
    -----------
    planet_type : str
        Type of planet: 'earth', 'mars', 'jupiter', or 'venus'
    rotation : float
        Rotation angle in degrees for the planet
    save_fig : bool
        Whether to save the figure
    """
    
    # Create figure and 3D axis
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Define planet colors
    planet_colors = {
        'earth': plt.cm.Blues,
        'mars': plt.cm.Oranges,
        'jupiter': plt.cm.YlOrBr,
        'venus': plt.cm.YlOrRd,
        'moon': plt.cm.Greys
    }
    
    # Get colormap for selected planet
    colormap = planet_colors.get(planet_type, plt.cm.Blues)
    
    # Apply rotation if specified
    if rotation != 0:
        rotation_rad = np.radians(rotation)
        x_rot = x * np.cos(rotation_rad) - z * np.sin(rotation_rad)
        z_rot = x * np.sin(rotation_rad) + z * np.cos(rotation_rad)
        x = x_rot
        z = z_rot
    
    # Plot surface with coloring
    surf = ax.plot_surface(x, y, z, cmap=colormap, 
                          linewidth=0, antialiased=True, 
                          rstride=2, cstride=2, alpha=0.9)
    
    # Add lighting effect with LightSource
    ls = LightSource(azdeg=45, altdeg=45)
    rgb = ls.shade(z, cmap=colormap)
    ax.plot_surface(x, y, z, facecolors=rgb, shade=False)
    
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'3D {planet_type.capitalize()} Planet', fontsize=16, fontweight='bold')
    
    # Set equal aspect ratio
    ax.set_box_aspect([1, 1, 1])
    max_range = 1
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    # Add colorbar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Height')
    
    # Set viewing angle
    ax.view_init(elev=20, azim=45)
    
    if save_fig:
        plt.savefig(f'{planet_type}_3d.png', dpi=150, bbox_inches='tight')
        print(f"Saved {planet_type}_3d.png")
    
    return fig, ax


def create_multiple_planets():
    """Create a figure showing multiple planets"""
    fig = plt.figure(figsize=(16, 12))
    
    planets = ['earth', 'mars', 'jupiter', 'venus']
    rotations = [0, 45, 90, 135]
    
    for idx, (planet, rotation) in enumerate(zip(planets, rotations), 1):
        ax = fig.add_subplot(2, 2, idx, projection='3d')
        
        # Create sphere
        u = np.linspace(0, 2 * np.pi, 60)
        v = np.linspace(0, np.pi, 60)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        
        # Planet color mapping
        planet_colors = {
            'earth': plt.cm.Blues,
            'mars': plt.cm.Oranges,
            'jupiter': plt.cm.YlOrBr,
            'venus': plt.cm.YlOrRd
        }
        
        colormap = planet_colors[planet]
        
        # Plot
        ax.plot_surface(x, y, z, cmap=colormap, linewidth=0, 
                       antialiased=True, rstride=2, cstride=2)
        
        ax.set_title(f'{planet.capitalize()}', fontsize=12, fontweight='bold')
        ax.set_box_aspect([1, 1, 1])
        ax.view_init(elev=20, azim=rotation)
        
        # Hide axis labels for cleaner look
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])
    
    fig.suptitle('3D Planet Visualization', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig


if __name__ == '__main__':
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description='planet3d CLI - generate planet visuals')
    parser.add_argument('--planet', choices=['earth', 'mars', 'jupiter', 'venus', 'moon'], default='earth', help='which planet to render')
    parser.add_argument('--rotation', type=float, default=0.0, help='rotation in degrees')
    parser.add_argument('--out-file', help='path to save the generated image (e.g. static/myplanet.png)')
    parser.add_argument('--multiple', action='store_true', help='create multiple-planets grid')
    parser.add_argument('--show', action='store_true', help='display the figure interactively')
    parser.add_argument('name', nargs='?', help='optional context name')
    parser.add_argument('age', nargs='?', help='optional context age')
    parser.add_argument('country', nargs='?', help='optional context country')

    # detect whether the script was started with any command-line args
    had_args = len(sys.argv) > 1
    args = parser.parse_args()

    # If no CLI arguments were provided, run an interactive demo by default
    if not had_args:
        fig, ax = create_planet_3d(planet_type=args.planet, rotation=args.rotation, save_fig=False)
        try:
            plt.show()
        except Exception:
            # running headless or non-interactive backend — fall back to saving a file
            outp = os.path.join('static', f"{args.planet}_3d.png")
            os.makedirs(os.path.dirname(outp), exist_ok=True)
            fig.savefig(outp, dpi=150, bbox_inches='tight')
            print(outp)
        sys.exit(0)

    # Multiple-planet mode
    if args.multiple:
        fig = create_multiple_planets()
        if args.out_file:
            outp = args.out_file
            d = os.path.dirname(outp)
            if d:
                os.makedirs(d, exist_ok=True)
            fig.savefig(outp, dpi=150, bbox_inches='tight')
            print(outp)
            sys.exit(0)
        if args.show:
            plt.show()
        else:
            print('Created multiple-planet figure (not saved).')
        sys.exit(0)

    # Single-planet mode
    fig, ax = create_planet_3d(planet_type=args.planet, rotation=args.rotation, save_fig=False)
    if args.out_file:
        outp = args.out_file
        d = os.path.dirname(outp)
        if d:
            os.makedirs(d, exist_ok=True)
        fig.savefig(outp, dpi=150, bbox_inches='tight')
        print(outp)
        sys.exit(0)

    if args.show:
        plt.show()
    else:
        print('Created planet figure (not saved).')

