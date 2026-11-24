"""
FUTURESCAPE 2050 - Smart Sustainable City Diorama
Blender 5.x Python Automation Script for College Master Project
Author: Aryan (Assisted by Antigravity)
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import os

def clear_scene():
    """Removes all objects, meshes, materials, and collections for a clean build."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
            
    # Clean up empty collections except Scene Collection
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)


def get_collection(name, parent=None):
    """Retrieves or creates a named collection in the scene."""
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent:
            parent.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col


def create_material(name, base_color=(0.8, 0.8, 0.8, 1.0), roughness=0.5, metallic=0.0, 
                    transmission=0.0, ior=1.45, emission_color=(0,0,0,1), emission_strength=0.0):
    """Creates or updates a Principled BSDF material compatible with Blender 4.x and 5.x."""
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Locate Principled BSDF
    principled = None
    for n in nodes:
        if n.type == 'BSDF_PRINCIPLED':
            principled = n
            break
    if not principled:
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.get('Material Output') or nodes.new(type='ShaderNodeOutputMaterial')
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
    # Set inputs safely based on socket names
    for inp in principled.inputs:
        if inp.name == "Base Color":
            inp.default_value = base_color
        elif inp.name == "Roughness":
            inp.default_value = roughness
        elif inp.name == "Metallic":
            inp.default_value = metallic
        elif inp.name in ["Transmission", "Transmission Weight"]:
            inp.default_value = transmission
        elif inp.name == "IOR":
            inp.default_value = ior
        elif inp.name == "Emission Color":
            inp.default_value = emission_color
        elif inp.name == "Emission Strength":
            inp.default_value = emission_strength
            
    return mat


def setup_materials():
    """Initializes the cohesive futuristic smart city material palette."""
    m = {}
    # Base / Architecture
    m['platform'] = create_material("Mat_Platform", base_color=(0.09, 0.10, 0.13, 1.0), roughness=0.35, metallic=0.05)
    m['plinth'] = create_material("Mat_PlinthBorder", base_color=(0.14, 0.16, 0.20, 1.0), roughness=0.25, metallic=0.3)
    m['road'] = create_material("Mat_Road", base_color=(0.11, 0.12, 0.14, 1.0), roughness=0.65, metallic=0.0)
    m['sidewalk'] = create_material("Mat_Sidewalk", base_color=(0.82, 0.85, 0.90, 1.0), roughness=0.32, metallic=0.0)
    m['curb'] = create_material("Mat_Curb", base_color=(0.65, 0.68, 0.73, 1.0), roughness=0.4, metallic=0.0)
    m['marking_white'] = create_material("Mat_MarkingWhite", base_color=(0.95, 0.95, 0.95, 1.0), roughness=0.2, emission_color=(1,1,1,1), emission_strength=0.1)
    m['marking_yellow'] = create_material("Mat_MarkingYellow", base_color=(1.0, 0.78, 0.12, 1.0), roughness=0.2)
    
    # Buildings
    m['bldg_white'] = create_material("Mat_BuildingWhite", base_color=(0.93, 0.94, 0.96, 1.0), roughness=0.22, metallic=0.05)
    m['bldg_grey'] = create_material("Mat_BuildingGrey", base_color=(0.55, 0.58, 0.64, 1.0), roughness=0.35, metallic=0.1)
    m['bldg_dark'] = create_material("Mat_BuildingDark", base_color=(0.18, 0.20, 0.24, 1.0), roughness=0.4, metallic=0.2)
    m['glass'] = create_material("Mat_GlassCyan", base_color=(0.04, 0.16, 0.26, 1.0), roughness=0.05, transmission=0.88, ior=1.45)
    m['glass_warm'] = create_material("Mat_GlassWarm", base_color=(0.35, 0.25, 0.15, 1.0), roughness=0.08, transmission=0.75, ior=1.45)
    m['window_glow'] = create_material("Mat_WindowWarmGlow", base_color=(1.0, 0.92, 0.78, 1.0), roughness=0.2, emission_color=(1.0, 0.88, 0.65, 1.0), emission_strength=3.5)
    
    # Accents & Futuristic Elements
    m['teal_neon'] = create_material("Mat_TealNeon", base_color=(0.0, 0.95, 0.85, 1.0), roughness=0.1, emission_color=(0.0, 0.95, 0.85, 1.0), emission_strength=4.5)
    m['orange_neon'] = create_material("Mat_OrangeNeon", base_color=(1.0, 0.45, 0.05, 1.0), roughness=0.1, emission_color=(1.0, 0.45, 0.05, 1.0), emission_strength=4.0)
    m['solar'] = create_material("Mat_SolarPanel", base_color=(0.04, 0.09, 0.22, 1.0), roughness=0.12, metallic=0.92)
    
    # Nature & Park
    m['grass'] = create_material("Mat_ParkGrass", base_color=(0.28, 0.58, 0.20, 1.0), roughness=0.85, metallic=0.0)
    m['water'] = create_material("Mat_PondWater", base_color=(0.08, 0.42, 0.45, 1.0), roughness=0.03, transmission=0.82, ior=1.33)
    m['stone'] = create_material("Mat_ParkStone", base_color=(0.38, 0.41, 0.46, 1.0), roughness=0.5, metallic=0.0)
    m['bark'] = create_material("Mat_TreeBark", base_color=(0.28, 0.20, 0.14, 1.0), roughness=0.8, metallic=0.0)
    m['foliage_light'] = create_material("Mat_FoliageLight", base_color=(0.32, 0.65, 0.24, 1.0), roughness=0.6, metallic=0.0)
    m['foliage_deep'] = create_material("Mat_FoliageDeep", base_color=(0.18, 0.46, 0.16, 1.0), roughness=0.6, metallic=0.0)
    m['flowers'] = create_material("Mat_Flowers", base_color=(0.95, 0.25, 0.45, 1.0), roughness=0.5, metallic=0.0)
    
    # Vehicles & Smart Mobility
    m['bus_body'] = create_material("Mat_BusBody", base_color=(0.96, 0.97, 0.99, 1.0), roughness=0.2, metallic=0.08)
    m['bus_teal'] = create_material("Mat_BusTeal", base_color=(0.0, 0.82, 0.72, 1.0), roughness=0.25, metallic=0.1)
    m['bus_black'] = create_material("Mat_BusTrim", base_color=(0.08, 0.08, 0.09, 1.0), roughness=0.4, metallic=0.2)
    m['tire'] = create_material("Mat_TireRubber", base_color=(0.06, 0.06, 0.07, 1.0), roughness=0.85, metallic=0.0)
    m['alloy'] = create_material("Mat_AlloyRim", base_color=(0.82, 0.85, 0.89, 1.0), roughness=0.18, metallic=0.92)
    m['headlight'] = create_material("Mat_HeadlightLED", base_color=(1.0, 1.0, 1.0, 1.0), roughness=0.1, emission_color=(1.0, 1.0, 1.0, 1.0), emission_strength=8.0)
    m['taillight'] = create_material("Mat_TaillightLED", base_color=(1.0, 0.08, 0.08, 1.0), roughness=0.1, emission_color=(1.0, 0.08, 0.08, 1.0), emission_strength=6.0)
    m['led_display'] = create_material("Mat_LEDDisplay", base_color=(0.0, 0.95, 0.85, 1.0), roughness=0.2, emission_color=(0.0, 0.95, 0.85, 1.0), emission_strength=5.0)
    
    # Infrastructure & Hardware
    m['metal_pole'] = create_material("Mat_MetalPole", base_color=(0.60, 0.64, 0.70, 1.0), roughness=0.25, metallic=0.85)
    m['streetlight_glow'] = create_material("Mat_StreetlightLED", base_color=(1.0, 0.95, 0.88, 1.0), roughness=0.1, emission_color=(1.0, 0.95, 0.88, 1.0), emission_strength=7.5)
    m['traffic_green'] = create_material("Mat_TrafficGreen", base_color=(0.1, 0.9, 0.3, 1.0), roughness=0.2, emission_color=(0.1, 0.9, 0.3, 1.0), emission_strength=6.0)
    m['traffic_red'] = create_material("Mat_TrafficRed", base_color=(0.95, 0.1, 0.1, 1.0), roughness=0.2, emission_color=(0.95, 0.1, 0.1, 1.0), emission_strength=6.0)
    m['tank_metal'] = create_material("Mat_TankMetal", base_color=(0.75, 0.80, 0.86, 1.0), roughness=0.2, metallic=0.9)
    m['water_gauge'] = create_material("Mat_WaterGauge", base_color=(0.1, 0.6, 0.7, 1.0), roughness=0.1, emission_color=(0.1, 0.6, 0.7, 1.0), emission_strength=2.5)

    return m


def assign_material(obj, mat):
    """Assigns or replaces material on an object."""
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def add_box(name, size, location, col, mat=None, bevel=0.0):
    """Creates an aligned cuboid box with optional bevel modifier."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    if mat:
        assign_material(obj, mat)
    
    if bevel > 0.0:
        bm = obj.modifiers.new(name="Bevel", type='BEVEL')
        bm.width = bevel
        bm.segments = 2
        bm.limit_method = 'ANGLE'
        
    # Relink to target collection
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def add_cylinder(name, radius, depth, location, col, mat=None, vertices=24, rotation=(0,0,0)):
    """Creates an aligned cylinder with specified materials."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        assign_material(obj, mat)
        
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def build_platform(col, mats):
    """Builds the 40x40 diorama base platform with beveled slate border and stepped plinth."""
    # Main platform slab
    base = add_box("Diorama_Base_Platform", (40.0, 40.0, 1.5), (0.0, 0.0, -0.75), col, mats['platform'], bevel=0.15)
    
    # Lower beveled architectural footing plinth
    plinth = add_box("Diorama_Plinth_Footing", (41.4, 41.4, 0.6), (0.0, 0.0, -1.8), col, mats['plinth'], bevel=0.12)
    
    # Outer accent perimeter trim line (subtle futuristic aesthetic)
    trim = add_box("Diorama_Perimeter_Trim", (40.4, 40.4, 0.08), (0.0, 0.0, 0.02), col, mats['bldg_dark'])
    
    # Corner architectural pylons / brand tags
    for sx in [-19.5, 19.5]:
        for sy in [-19.5, 19.5]:
            pylon = add_box(f"Corner_Pylon_{sx}_{sy}", (1.0, 1.0, 0.5), (sx, sy, 0.25), col, mats['plinth'], bevel=0.05)
            # Glowing accent dot on each corner
            dot = add_cylinder(f"Pylon_Glow_{sx}_{sy}", 0.2, 0.05, (sx, sy, 0.52), col, mats['teal_neon'], vertices=12)


def build_road_network(col, mats):
    """Constructs the intersecting road avenues, sidewalks, curbs, zebra crossings, and lane stripes."""
    # Roads are 6.0 units wide, centered on X and Y axes
    # North-South Avenue: X in [-3, 3], Y in [-19, 19]
    add_box("Road_NorthSouth_Asphalt", (6.0, 38.0, 0.08), (0.0, 0.0, 0.04), col, mats['road'])
    # East-West Street: Y in [-3, 3], X in [-19, 19]
    add_box("Road_EastWest_Asphalt", (38.0, 6.0, 0.08), (0.0, 0.0, 0.04), col, mats['road'])
    
    # Sidewalks: 1.6 units wide on all street borders, elevated by 0.12 units
    # Quadrant sidewalks
    # NW: X in [-19, -3.2], Y in [3.2, 19]
    add_box("Sidewalk_NW_Rim", (15.8, 15.8, 0.14), (-11.1, 11.1, 0.07), col, mats['sidewalk'], bevel=0.03)
    # NE: X in [3.2, 19], Y in [3.2, 19]
    add_box("Sidewalk_NE_Rim", (15.8, 15.8, 0.14), (11.1, 11.1, 0.07), col, mats['sidewalk'], bevel=0.03)
    # SW: X in [-19, -3.2], Y in [-19, -3.2]
    add_box("Sidewalk_SW_Rim", (15.8, 15.8, 0.14), (-11.1, -11.1, 0.07), col, mats['sidewalk'], bevel=0.03)
    # SE: X in [3.2, 19], Y in [-19, -3.2]
    add_box("Sidewalk_SE_Rim", (15.8, 15.8, 0.14), (11.1, -11.1, 0.07), col, mats['sidewalk'], bevel=0.03)
    
    # Curbs (granite borders between sidewalk and road)
    curb_w = 0.18
    # NS Curbs
    add_box("Curb_NS_West_N", (curb_w, 15.8, 0.16), (-3.1, 11.1, 0.08), col, mats['curb'])
    add_box("Curb_NS_East_N", (curb_w, 15.8, 0.16), (3.1, 11.1, 0.08), col, mats['curb'])
    add_box("Curb_NS_West_S", (curb_w, 15.8, 0.16), (-3.1, -11.1, 0.08), col, mats['curb'])
    add_box("Curb_NS_East_S", (curb_w, 15.8, 0.16), (3.1, -11.1, 0.08), col, mats['curb'])
    
    # EW Curbs
    add_box("Curb_EW_North_W", (15.8, curb_w, 0.16), (-11.1, 3.1, 0.08), col, mats['curb'])
    add_box("Curb_EW_South_W", (15.8, curb_w, 0.16), (-11.1, -3.1, 0.08), col, mats['curb'])
    add_box("Curb_EW_North_E", (15.8, curb_w, 0.16), (11.1, 3.1, 0.08), col, mats['curb'])
    add_box("Curb_EW_South_E", (15.8, curb_w, 0.16), (11.1, -3.1, 0.08), col, mats['curb'])
    
    # Lane Markings (White dashed lines along roads)
    # North segment: Y in [4.5, 18.5]
    for y in [5.5, 8.5, 11.5, 14.5, 17.5]:
        add_box(f"Lane_Dash_N_{y}", (0.15, 1.8, 0.01), (0.0, y, 0.09), col, mats['marking_white'])
    # South segment: Y in [-18.5, -4.5]
    for y in [-5.5, -8.5, -11.5, -14.5, -17.5]:
        add_box(f"Lane_Dash_S_{y}", (0.15, 1.8, 0.01), (0.0, y, 0.09), col, mats['marking_white'])
    # East segment: X in [4.5, 18.5]
    for x in [5.5, 8.5, 11.5, 14.5, 17.5]:
        add_box(f"Lane_Dash_E_{x}", (1.8, 0.15, 0.01), (x, 0.0, 0.09), col, mats['marking_white'])
    # West segment: X in [-18.5, -4.5]
    for x in [-5.5, -8.5, -11.5, -14.5, -17.5]:
        add_box(f"Lane_Dash_W_{x}", (1.8, 0.15, 0.01), (x, 0.0, 0.09), col, mats['marking_white'])
        
    # Zebra Crossings at all 4 intersection approaches (Width = 5.2, length = 1.4)
    def add_crosswalk(name, cx, cy, is_horizontal):
        stripe_count = 8
        span = 4.8
        step = span / (stripe_count - 1)
        for i in range(stripe_count):
            offset = -span/2 + i * step
            if is_horizontal:
                # Stripes running along Y for horizontal road crossing (North & South of intersection)
                add_box(f"{name}_stripe_{i}", (0.35, 1.5, 0.01), (cx + offset, cy, 0.09), col, mats['marking_white'])
            else:
                # Stripes running along X for vertical road crossing (East & West of intersection)
                add_box(f"{name}_stripe_{i}", (1.5, 0.35, 0.01), (cx, cy + offset, 0.09), col, mats['marking_white'])
                
    add_crosswalk("Crosswalk_North", 0.0, 3.8, True)
    add_crosswalk("Crosswalk_South", 0.0, -3.8, True)
    add_crosswalk("Crosswalk_East", 3.8, 0.0, False)
    add_crosswalk("Crosswalk_West", -3.8, 0.0, False)
    
    # Modern Roundabout / Smart Central Nexus circle at (0,0)
    add_cylinder("Intersection_Nexus_Core", 1.2, 0.02, (0.0, 0.0, 0.09), col, mats['bldg_dark'], vertices=32)
    add_cylinder("Intersection_Nexus_Glow", 0.95, 0.025, (0.0, 0.0, 0.095), col, mats['teal_neon'], vertices=32)
    add_cylinder("Intersection_Nexus_Center", 0.55, 0.03, (0.0, 0.0, 0.10), col, mats['bldg_dark'], vertices=24)


def build_zone_a_business_district(col, mats):
    """
    Zone A: 3 Modern Architectural Skyscrapers with distinct silhouettes,
    glass facades, repeated window ribs, cantilevered tiers, and rooftop equipment.
    Located in North-West quadrant: X in [-18, -4.5], Y in [4.5, 18].
    """
    # -------------------------------------------------------------
    # Skyscraper 1: "The Apex Spire" (Tallest hero tower, height ~21.0)
    # Position: (-12.0, 13.0)
    # -------------------------------------------------------------
    base_x, base_y = -12.0, 13.0
    
    # Tier 1 - Lobby & Base
    add_box("Skyscraper1_Lobby", (6.0, 6.0, 3.0), (base_x, base_y, 1.5), col, mats['bldg_white'], bevel=0.1)
    add_box("Skyscraper1_Lobby_Glass", (5.2, 6.05, 2.2), (base_x, base_y, 1.4), col, mats['glass'])
    add_box("Skyscraper1_Lobby_Entrance_Glow", (2.2, 6.1, 0.2), (base_x, base_y, 0.5), col, mats['teal_neon'])
    
    # Tier 2 - Mid Body (Stepped with vertical structural fins)
    add_box("Skyscraper1_Mid_Core", (5.2, 5.2, 8.0), (base_x, base_y, 7.0), col, mats['bldg_white'])
    add_box("Skyscraper1_Mid_Glass", (5.3, 4.4, 7.4), (base_x, base_y, 7.0), col, mats['glass'])
    # Horizontal window sunshades / louvers
    for z in [4.5, 6.0, 7.5, 9.0, 10.5]:
        add_box(f"Skyscraper1_Louver_{z}", (5.5, 5.5, 0.15), (base_x, base_y, z), col, mats['bldg_grey'])
        
    # Tier 3 - Upper Tapered Crown
    add_box("Skyscraper1_Upper_Core", (4.2, 4.2, 6.0), (base_x, base_y, 14.0), col, mats['bldg_white'], bevel=0.08)
    add_box("Skyscraper1_Upper_Glass", (4.3, 3.4, 5.4), (base_x, base_y, 14.0), col, mats['glass'])
    
    # Tier 4 - Slanted Crown & Spire
    add_box("Skyscraper1_Crown", (3.2, 3.2, 2.5), (base_x, base_y, 18.25), col, mats['bldg_dark'], bevel=0.05)
    add_box("Skyscraper1_Crown_Accent", (3.3, 3.3, 0.2), (base_x, base_y, 17.2), col, mats['teal_neon'])
    
    # Telecommunication Spire / Antennae
    add_cylinder("Skyscraper1_Antenna_Base", 0.4, 1.5, (base_x, base_y, 20.25), col, mats['metal_pole'], vertices=16)
    add_cylinder("Skyscraper1_Antenna_Mast", 0.12, 3.2, (base_x, base_y, 22.0), col, mats['metal_pole'], vertices=12)
    add_cylinder("Skyscraper1_Antenna_Beacon", 0.25, 0.25, (base_x, base_y, 23.6), col, mats['orange_neon'], vertices=12)

    # -------------------------------------------------------------
    # Skyscraper 2: "The Eco-Facet Tower" (Height ~16.5)
    # Chamfered angular silhouette with diagonal architectural bracing
    # Position: (-6.5, 12.5)
    # -------------------------------------------------------------
    b2_x, b2_y = -6.5, 12.5
    
    # Main Tower Body with heavy bevel creating faceted octagonal profile
    b2_body = add_box("Skyscraper2_Body", (4.8, 4.8, 14.0), (b2_x, b2_y, 7.0), col, mats['glass'], bevel=0.8)
    # White structural exoskeleton ribs
    for z in [2.5, 5.5, 8.5, 11.5]:
        add_box(f"Skyscraper2_Rib_{z}", (5.0, 5.0, 0.3), (b2_x, b2_y, z), col, mats['bldg_white'], bevel=0.05)
    # Diagonal corner bracing trusses
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)
        cx = b2_x + 2.4 * math.cos(rad)
        cy = b2_y + 2.4 * math.sin(rad)
        add_box(f"Skyscraper2_Column_{angle}", (0.35, 0.35, 14.2), (cx, cy, 7.1), col, mats['bldg_white'])
        
    # Cantilevered Mid-Rise Sky Garden
    add_box("Skyscraper2_SkyGarden_Deck", (5.8, 3.0, 0.4), (b2_x, b2_y + 1.2, 9.0), col, mats['bldg_dark'])
    add_box("Skyscraper2_SkyGarden_Grass", (5.4, 2.6, 0.1), (b2_x, b2_y + 1.2, 9.25), col, mats['grass'])
    # Miniature sky-garden trees
    for tx in [-1.5, 0.0, 1.5]:
        add_cylinder(f"SkyGarden_TreeTrunk_{tx}", 0.08, 0.6, (b2_x + tx, b2_y + 1.2, 9.6), col, mats['bark'], vertices=8)
        add_cylinder(f"SkyGarden_TreeFoliage_{tx}", 0.4, 0.6, (b2_x + tx, b2_y + 1.2, 10.1), col, mats['foliage_light'], vertices=10)
        
    # Rooftop Crown & Observation Deck
    add_box("Skyscraper2_Roof_Crown", (4.2, 4.2, 1.8), (b2_x, b2_y, 14.9), col, mats['bldg_white'], bevel=0.05)
    add_box("Skyscraper2_Roof_GlassRing", (4.3, 4.3, 0.8), (b2_x, b2_y, 14.8), col, mats['teal_neon'])

    # -------------------------------------------------------------
    # Skyscraper 3: "Nexus Plaza Tower" (Cantilevered modern block, height ~13.5)
    # Interlocking volumetric blocks with rooftop helipad
    # Position: (-12.5, 6.5)
    # -------------------------------------------------------------
    b3_x, b3_y = -12.5, 6.5
    
    # Lower Section
    add_box("Skyscraper3_Lower", (5.4, 4.6, 5.0), (b3_x, b3_y, 2.5), col, mats['bldg_grey'], bevel=0.08)
    add_box("Skyscraper3_Lower_WindowBand", (5.5, 4.2, 1.2), (b3_x, b3_y, 2.5), col, mats['window_glow'])
    
    # Cantilevered Upper Section (offset to the east toward the avenue)
    add_box("Skyscraper3_Upper_Cantilever", (4.8, 5.0, 6.0), (b3_x + 0.6, b3_y, 8.0), col, mats['bldg_white'], bevel=0.1)
    add_box("Skyscraper3_Upper_GlassBand", (4.9, 4.4, 3.2), (b3_x + 0.6, b3_y, 8.2), col, mats['glass'])
    
    # Rooftop Helipad
    add_cylinder("Skyscraper3_Helipad_Base", 2.2, 0.25, (b3_x + 0.6, b3_y, 11.15), col, mats['bldg_dark'], vertices=32)
    add_cylinder("Skyscraper3_Helipad_Ring", 2.0, 0.02, (b3_x + 0.6, b3_y, 11.28), col, mats['marking_yellow'], vertices=32)
    # Helipad 'H' letter
    add_box("Helipad_H_Left", (0.2, 1.2, 0.03), (b3_x + 0.1, b3_y, 11.3), col, mats['marking_white'])
    add_box("Helipad_H_Right", (0.2, 1.2, 0.03), (b3_x + 1.1, b3_y, 11.3), col, mats['marking_white'])
    add_box("Helipad_H_Cross", (1.0, 0.2, 0.03), (b3_x + 0.6, b3_y, 11.3), col, mats['marking_white'])
    
    # Rooftop HVAC Chillers & Equipment
    add_box("Skyscraper3_HVAC_1", (1.2, 0.8, 0.8), (b3_x - 1.2, b3_y - 1.2, 11.4), col, mats['bldg_grey'])
    add_box("Skyscraper3_HVAC_2", (0.9, 0.9, 0.7), (b3_x - 1.2, b3_y + 1.2, 11.35), col, mats['bldg_grey'])
    add_cylinder("Skyscraper3_VentFan", 0.35, 0.15, (b3_x - 1.2, b3_y - 1.2, 11.85), col, mats['bldg_dark'], vertices=16)

    # Plaza connection: Paved courtyard between the 3 towers with modern ground benches
    add_box("Business_Plaza_Paving", (8.0, 8.0, 0.06), (-9.5, 9.5, 0.14), col, mats['sidewalk'])
    add_box("Business_Plaza_WaterMirror", (3.2, 3.2, 0.08), (-9.5, 9.5, 0.16), col, mats['water'])
    add_box("Business_Plaza_WaterRim", (3.6, 3.6, 0.09), (-9.5, 9.5, 0.15), col, mats['stone'], bevel=0.04)


def build_zone_b_residential_district(col, mats):
    """
    Zone B: 3 Sustainable Apartment Buildings with stepped green terraces,
    balconies, modular pods, entrance landscaping, and rooftop gardens.
    Located in South-East quadrant: X in [4.5, 18], Y in [-18, -4.5].
    """
    # -------------------------------------------------------------
    # Residential 1: "Verdant Terraces" (Stepped biophilic apartments, height ~10.0)
    # Position: (13.0, -12.5)
    # -------------------------------------------------------------
    r1_x, r1_y = 13.0, -12.5
    
    # Step 1 (Ground & 1st floor)
    add_box("Res1_Step1", (6.5, 6.0, 3.0), (r1_x, r1_y, 1.5), col, mats['bldg_white'], bevel=0.08)
    add_box("Res1_Step1_Balcony_Glass", (6.6, 5.2, 0.6), (r1_x, r1_y, 2.8), col, mats['glass'])
    
    # Step 2 (Middle)
    add_box("Res1_Step2", (5.2, 6.0, 3.0), (r1_x - 0.65, r1_y, 4.5), col, mats['bldg_white'], bevel=0.08)
    add_box("Res1_Step2_Balcony_Glass", (5.3, 5.2, 0.6), (r1_x - 0.65, r1_y, 5.8), col, mats['glass'])
    # Terrace 1 Garden
    add_box("Res1_Terrace1_Green", (1.2, 5.6, 0.1), (r1_x + 2.5, r1_y, 3.05), col, mats['grass'])
    for ty in [-2.0, 0.0, 2.0]:
        add_cylinder(f"Res1_TerraceBush_{ty}", 0.25, 0.4, (r1_x + 2.5, r1_y + ty, 3.3), col, mats['foliage_light'], vertices=10)
        
    # Step 3 (Top tier)
    add_box("Res1_Step3", (3.8, 6.0, 3.0), (r1_x - 1.35, r1_y, 7.5), col, mats['bldg_white'], bevel=0.08)
    add_box("Res1_Terrace2_Green", (1.2, 5.6, 0.1), (r1_x + 1.2, r1_y, 6.05), col, mats['grass'])
    
    # Rooftop Pergola & Solar Canopy
    add_box("Res1_Rooftop_Canopy", (3.2, 4.5, 0.15), (r1_x - 1.35, r1_y, 9.6), col, mats['solar'])
    for px in [-2.5, -0.2]:
        for py in [-1.8, 1.8]:
            add_cylinder(f"Pergola_Post_{px}_{py}", 0.06, 1.2, (r1_x + px, r1_y + py, 9.0), col, mats['metal_pole'], vertices=8)

    # -------------------------------------------------------------
    # Residential 2: "Skyline Modular Apartments" (Height ~11.5)
    # Alternating protruding window pods and warm balcony insets
    # Position: (6.8, -12.5)
    # -------------------------------------------------------------
    r2_x, r2_y = 6.8, -12.5
    
    # Main Tower Core
    add_box("Res2_Main_Core", (4.4, 5.2, 11.0), (r2_x, r2_y, 5.5), col, mats['bldg_grey'], bevel=0.08)
    
    # Protruding modular white living pods on front & rear
    for floor_z in [2.5, 5.0, 7.5, 9.5]:
        # Alternating left and right shift
        shift = 0.5 if (floor_z in [2.5, 7.5]) else -0.5
        pod = add_box(f"Res2_Pod_{floor_z}", (3.6, 5.6, 1.8), (r2_x + shift, r2_y, floor_z), col, mats['bldg_white'], bevel=0.05)
        # Windows with warm golden interior glow
        add_box(f"Res2_Window_Glow_{floor_z}", (3.0, 5.7, 0.8), (r2_x + shift, r2_y, floor_z), col, mats['window_glow'])
        # Balcony rail
        add_box(f"Res2_Balcony_Rail_{floor_z}", (3.4, 0.1, 0.6), (r2_x + shift, r2_y + 2.85, floor_z - 0.4), col, mats['glass'])
        
    # Entrance canopy at street level
    add_box("Res2_Entrance_Canopy", (2.8, 1.5, 0.12), (r2_x, r2_y + 3.2, 1.8), col, mats['bldg_dark'])
    add_cylinder("Res2_Canopy_Pillar_L", 0.06, 1.8, (r2_x - 1.2, r2_y + 3.8, 0.9), col, mats['metal_pole'], vertices=8)
    add_cylinder("Res2_Canopy_Pillar_R", 0.06, 1.8, (r2_x + 1.2, r2_y + 3.8, 0.9), col, mats['metal_pole'], vertices=8)

    # -------------------------------------------------------------
    # Residential 3: "Eco-Lofts & Communal Garden" (Height ~7.5)
    # Low-rise sustainable urban community with angled green roof
    # Position: (11.5, -6.5)
    # -------------------------------------------------------------
    r3_x, r3_y = 11.5, -6.5
    
    add_box("Res3_Building_Body", (5.2, 4.4, 6.0), (r3_x, r3_y, 3.0), col, mats['bldg_white'], bevel=0.08)
    # Horizontal glass ribbons
    for z in [1.5, 3.2, 4.8]:
        add_box(f"Res3_GlassRibbon_{z}", (5.3, 3.8, 0.7), (r3_x, r3_y, z), col, mats['glass_warm'])
        
    # Angled Green Roof with Solar Array
    add_box("Res3_Roof_Base", (5.0, 4.2, 0.4), (r3_x, r3_y, 6.2), col, mats['grass'])
    for sx in [-1.5, 0.0, 1.5]:
        solar = add_box(f"Res3_SolarPanel_{sx}", (1.2, 3.2, 0.08), (r3_x + sx, r3_y, 6.6), col, mats['solar'])
        solar.rotation_euler = (math.radians(15), 0, 0)
        
    # Courtyard Landscaping between Residential Blocks
    add_box("Res_Courtyard_Path", (4.0, 4.0, 0.02), (7.5, -7.0, 0.14), col, mats['sidewalk'])
    # Modern Community Benches
    add_box("Res_Bench_1", (1.4, 0.45, 0.35), (7.5, -6.0, 0.32), col, mats['stone'])
    add_box("Res_Bench_2", (1.4, 0.45, 0.35), (7.5, -8.0, 0.32), col, mats['stone'])
    # Central Courtyard Tree
    add_cylinder("Res_Courtyard_Tree_Trunk", 0.15, 1.8, (7.5, -7.0, 1.0), col, mats['bark'], vertices=10)
    add_cylinder("Res_Courtyard_Tree_Crown", 1.0, 1.4, (7.5, -7.0, 2.4), col, mats['foliage_deep'], vertices=12)


def build_zone_c_central_park(col, mats):
    """
    Zone C: Central Urban Park with organic terrain, reflecting water feature / pond,
    arched footbridge, walking trails, multiple tree varieties, shrubs, and park benches.
    Located in North-East quadrant: X in [4.5, 18], Y in [4.5, 18].
    """
    # Park Base Green Turf
    add_box("Park_Main_Lawn", (14.5, 14.5, 0.16), (11.5, 11.5, 0.08), col, mats['grass'])
    
    # Curved Stone Walking Pathways (Meandering cross layout)
    add_box("Park_Path_Diag1", (16.0, 1.4, 0.03), (11.5, 11.5, 0.18), col, mats['sidewalk']).rotation_euler = (0, 0, math.radians(45))
    add_box("Park_Path_Diag2", (16.0, 1.4, 0.03), (11.5, 11.5, 0.18), col, mats['sidewalk']).rotation_euler = (0, 0, math.radians(-45))
    
    # Central Pond / Water Feature
    pond_x, pond_y = 11.5, 11.5
    # Stone Outer Basin Rim
    add_cylinder("Park_Pond_OuterRim", 3.2, 0.22, (pond_x, pond_y, 0.18), col, mats['stone'], vertices=32)
    # Reflective Turquoise Water Disk
    add_cylinder("Park_Pond_Water", 2.8, 0.15, (pond_x, pond_y, 0.22), col, mats['water'], vertices=32)
    # Stepped Fountain Core in Pond Center
    add_cylinder("Park_Fountain_Tier1", 1.0, 0.45, (pond_x, pond_y, 0.35), col, mats['stone'], vertices=16)
    add_cylinder("Park_Fountain_Tier2", 0.5, 0.35, (pond_x, pond_y, 0.65), col, mats['stone'], vertices=16)
    add_cylinder("Park_Fountain_JetGlow", 0.15, 0.3, (pond_x, pond_y, 0.9), col, mats['teal_neon'], vertices=12)
    
    # Modern Pedestrian Footbridge across Pond Edge
    bridge = add_box("Park_Footbridge", (1.0, 4.2, 0.18), (pond_x + 1.8, pond_y, 0.38), col, mats['bldg_white'], bevel=0.04)
    bridge.rotation_euler = (0, math.radians(4), math.radians(15))
    # Bridge Handrails
    add_cylinder("Bridge_Rail_L", 0.04, 4.2, (pond_x + 1.35, pond_y, 0.65), col, mats['metal_pole'], vertices=8, rotation=(math.radians(75), 0, 0))
    add_cylinder("Bridge_Rail_R", 0.04, 4.2, (pond_x + 2.25, pond_y, 0.65), col, mats['metal_pole'], vertices=8, rotation=(math.radians(75), 0, 0))

    # Tree Builder Helpers
    def plant_deciduous_tree(name, x, y, scale=1.0):
        # Organic multi-tier sphere tree
        add_cylinder(f"{name}_Trunk", 0.12 * scale, 1.6 * scale, (x, y, 0.8 * scale), col, mats['bark'], vertices=10)
        # Foliage cluster
        add_cylinder(f"{name}_CrownMain", 1.1 * scale, 1.2 * scale, (x, y, 1.8 * scale), col, mats['foliage_deep'], vertices=14)
        add_cylinder(f"{name}_CrownTop", 0.75 * scale, 0.9 * scale, (x, y, 2.5 * scale), col, mats['foliage_light'], vertices=12)

    def plant_conifer_tree(name, x, y, scale=1.0):
        # Stepped cone pine tree
        add_cylinder(f"{name}_Trunk", 0.10 * scale, 1.8 * scale, (x, y, 0.9 * scale), col, mats['bark'], vertices=8)
        for i, (r, z) in enumerate([(1.1, 1.4), (0.85, 2.1), (0.55, 2.7)]):
            cone = add_cylinder(f"{name}_Cone_{i}", r * scale, 0.8 * scale, (x, y, z * scale), col, mats['foliage_deep'], vertices=10)

    # Distribute 14 trees in visually balanced groves
    tree_coords = [
        # Northwest of pond
        ("Tree_D1", 6.8, 15.5, 1.1, "deciduous"),
        ("Tree_P1", 8.5, 16.5, 1.2, "conifer"),
        ("Tree_D2", 7.2, 13.5, 0.85, "deciduous"),
        # Northeast of pond
        ("Tree_P2", 15.5, 16.0, 1.3, "conifer"),
        ("Tree_D3", 16.5, 14.0, 1.0, "deciduous"),
        ("Tree_D4", 14.0, 15.8, 0.9, "deciduous"),
        # Southeast of pond
        ("Tree_P3", 16.5, 7.5, 1.15, "conifer"),
        ("Tree_D5", 15.0, 8.5, 1.25, "deciduous"),
        ("Tree_D6", 16.0, 6.0, 0.8, "deciduous"),
        # Southwest of pond
        ("Tree_D7", 6.8, 7.2, 1.05, "deciduous"),
        ("Tree_P4", 8.2, 6.0, 1.2, "conifer"),
        ("Tree_D8", 6.2, 9.2, 0.75, "deciduous"),
        # Near Pond accents
        ("Tree_Acc1", 14.5, 11.5, 0.9, "deciduous"),
        ("Tree_Acc2", 8.5, 11.5, 0.95, "conifer"),
    ]
    for name, tx, ty, sc, ttype in tree_coords:
        if ttype == "deciduous":
            plant_deciduous_tree(name, tx, ty, sc)
        else:
            plant_conifer_tree(name, tx, ty, sc)
            
    # Park Benches (4 benches surrounding pathways)
    for i, (bx, by, rot) in enumerate([
        (9.5, 14.0, 45), (14.0, 13.8, -45), (13.8, 9.2, 45), (9.2, 9.5, -45)
    ]):
        bench = add_box(f"Park_Bench_{i}", (1.3, 0.45, 0.35), (bx, by, 0.32), col, mats['stone'])
        bench.rotation_euler = (0, 0, math.radians(rot))

    # Flower Beds / Shrubbery
    for i, (fx, fy) in enumerate([(10.2, 6.8), (15.5, 11.5), (7.5, 11.8), (11.5, 15.8)]):
        add_box(f"FlowerBed_{i}", (1.8, 1.0, 0.25), (fx, fy, 0.25), col, mats['stone'], bevel=0.03)
        add_box(f"FlowerBloom_{i}", (1.6, 0.8, 0.1), (fx, fy, 0.38), col, mats['flowers'])


def build_zone_f_civic_centre(col, mats):
    """
    Zone F: Modern Public Civic Centre / Innovation Hall with distinctive
    curved sweeping geometry, grand glass atrium, forecourt plaza, and public monument.
    Located in South-West quadrant: X in [-18, -4.5], Y in [-18, -4.5].
    """
    c_x, c_y = -10.5, -10.5
    
    # Main Civic Auditorium / Wing 1
    add_box("Civic_Auditorium_Wing", (8.0, 5.0, 5.5), (c_x, c_y - 1.0, 2.75), col, mats['bldg_white'], bevel=0.15)
    
    # Grand Glass Atrium (Curved facade facing the central intersection)
    add_box("Civic_Glass_Atrium", (6.5, 4.0, 6.5), (c_x + 1.2, c_y + 1.5, 3.25), col, mats['glass'], bevel=0.2)
    # Structural Atrium Mullions / Louver Brids
    for z in [1.5, 3.2, 4.8, 6.2]:
        add_box(f"Civic_Atrium_Rib_{z}", (6.7, 4.2, 0.12), (c_x + 1.2, c_y + 1.5, z), col, mats['bldg_white'])
        
    # Cantilevered Aerodynamic Canopy Roof (Sweeps up toward the intersection)
    canopy = add_box("Civic_Canopy_Roof", (8.5, 8.5, 0.4), (c_x + 0.6, c_y + 0.5, 6.8), col, mats['bldg_white'], bevel=0.08)
    canopy.rotation_euler = (math.radians(-4), math.radians(4), 0)
    
    # Glowing Teal Civic Crest / Digital Signage
    add_box("Civic_Digital_Sign", (3.2, 0.1, 0.6), (c_x + 1.2, c_y + 3.6, 5.5), col, mats['teal_neon'])
    
    # Public Plaza Forecourt with Geometric Art Monument
    plaza_x, plaza_y = -6.0, -6.0
    add_box("Civic_Plaza_Paving", (5.0, 5.0, 0.04), (plaza_x, plaza_y, 0.14), col, mats['sidewalk'])
    # Circular Pedestal
    add_cylinder("Plaza_Monument_Base", 1.2, 0.3, (plaza_x, plaza_y, 0.28), col, mats['stone'], vertices=24)
    # Futuristic Kinetic / Mobius Sculpture Rings
    r1 = add_cylinder("Monument_Ring1", 0.9, 0.12, (plaza_x, plaza_y, 1.1), col, mats['alloy'], vertices=20)
    r1.rotation_euler = (math.radians(45), math.radians(25), 0)
    r2 = add_cylinder("Monument_Ring2", 0.7, 0.10, (plaza_x, plaza_y, 1.1), col, mats['teal_neon'], vertices=20)
    r2.rotation_euler = (math.radians(-35), math.radians(55), 0)
    add_cylinder("Monument_CoreSphere", 0.35, 0.35, (plaza_x, plaza_y, 1.1), col, mats['orange_neon'], vertices=16)


def build_zone_e_renewable_energy(col, mats):
    """
    Zone E: Renewable Energy Infrastructure including Ground Solar Photovoltaic Array,
    Sleek 3-blade Smart Wind Turbine, Rainwater Harvesting Tank, and Battery Energy Storage.
    Located in South-West quadrant perimeter: X in [-16.5, -6.0], Y in [-16.5, -14.0].
    """
    # -------------------------------------------------------------
    # Smart Wind Turbine (Height ~11.5 units)
    # Position: (-15.5, -6.5)
    # -------------------------------------------------------------
    wt_x, wt_y = -15.5, -6.5
    
    # Foundation
    add_cylinder("WindTurbine_Foundation", 1.2, 0.3, (wt_x, wt_y, 0.25), col, mats['stone'], vertices=20)
    # Tapered Steel Mast
    add_cylinder("WindTurbine_Mast", 0.28, 9.5, (wt_x, wt_y, 5.0), col, mats['bldg_white'], vertices=16)
    # Aerodynamic Nacelle
    add_box("WindTurbine_Nacelle", (1.4, 0.7, 0.7), (wt_x, wt_y, 9.8), col, mats['bldg_white'], bevel=0.08)
    add_cylinder("WindTurbine_Nacelle_StatusRing", 0.38, 0.1, (wt_x - 0.75, wt_y, 9.8), col, mats['teal_neon'], vertices=16, rotation=(0, math.radians(90), 0))
    # Rotor Hub (Empty parent for animation)
    hub = add_cylinder("WindTurbine_RotorHub", 0.35, 0.5, (wt_x + 0.7, wt_y, 9.8), col, mats['bldg_dark'], vertices=16, rotation=(0, math.radians(90), 0))
    
    # 3 Aerodynamic Blades properly centered on Hub
    blade_length = 3.6
    for b_idx in range(3):
        blade_angle = math.radians(b_idx * 120)
        bx = wt_x + 0.75
        by = wt_y + (blade_length / 2) * math.sin(blade_angle)
        bz = 9.8 + (blade_length / 2) * math.cos(blade_angle)
        blade = add_box(f"WindTurbine_Blade_{b_idx}", (0.08, 0.25, blade_length), (bx, by, bz), col, mats['bldg_white'], bevel=0.03)
        blade.rotation_euler = (blade_angle, math.radians(10), 0)
        # Use matrix_parent_inverse to maintain exact world transform
        bpy.context.view_layer.update()
        blade.parent = hub
        blade.matrix_parent_inverse = hub.matrix_world.inverted()

    # -------------------------------------------------------------
    # Solar Photovoltaic Ground Array (Dual-axis tracker banks)
    # Position: (-15.5, -14.5)
    # -------------------------------------------------------------
    for i, sx in enumerate([-16.0, -14.0, -12.0]):
        # Mounting frame
        add_cylinder(f"Solar_Pylon_{i}", 0.08, 1.2, (sx, -15.0, 0.6), col, mats['metal_pole'], vertices=8)
        # Angled Solar Collector Panel (Facing south-east toward the sun)
        panel = add_box(f"Solar_Panel_Array_{i}", (1.5, 2.4, 0.08), (sx, -15.0, 1.3), col, mats['solar'], bevel=0.02)
        panel.rotation_euler = (math.radians(25), 0, math.radians(-15))
        # Support bracket
        add_cylinder(f"Solar_Bracket_{i}", 0.04, 1.6, (sx, -15.2, 0.85), col, mats['metal_pole'], vertices=6, rotation=(math.radians(35), 0, 0))

    # -------------------------------------------------------------
    # Battery Energy Storage System (BESS) Container Unit
    # Position: (-15.0, -11.0)
    # -------------------------------------------------------------
    add_box("BESS_Container", (3.2, 1.8, 1.6), (-15.0, -11.0, 0.95), col, mats['bldg_grey'], bevel=0.05)
    # Digital Status LED telemetry bar
    add_box("BESS_Telemetry_Bar", (2.6, 0.08, 0.15), (-15.0, -10.05, 1.4), col, mats['teal_neon'])
    # Cooling fan vents
    for vx in [-15.8, -15.0, -14.2]:
        add_cylinder(f"BESS_Fan_{vx}", 0.25, 0.05, (vx, -10.05, 0.8), col, mats['bldg_dark'], vertices=12, rotation=(math.radians(90), 0, 0))

    # -------------------------------------------------------------
    # Rainwater Harvesting & Dual Cylindrical Filtration Tanks
    # Position: (-6.5, -15.5)
    # -------------------------------------------------------------
    add_box("Rainwater_Pad", (3.6, 2.2, 0.2), (-6.5, -15.5, 0.2), col, mats['stone'])
    for ti, tx in enumerate([-7.3, -5.7]):
        # Tank cylinder
        add_cylinder(f"Rainwater_Tank_{ti}", 0.65, 2.0, (tx, -15.5, 1.2), col, mats['tank_metal'], vertices=24)
        # Stainless steel structural bands
        for bz in [0.7, 1.2, 1.7]:
            add_cylinder(f"Tank_{ti}_Band_{bz}", 0.67, 0.06, (tx, -15.5, bz), col, mats['bldg_dark'], vertices=24)
        # Transparent illuminated water level gauge tube
        add_cylinder(f"Tank_{ti}_Gauge", 0.06, 1.4, (tx + 0.66, -15.5, 1.2), col, mats['water_gauge'], vertices=8)
    # Interconnecting Delivery Pipes
    add_cylinder("Rainwater_Pipe_Bridge", 0.06, 1.6, (-6.5, -15.5, 1.8), col, mats['metal_pole'], vertices=8, rotation=(0, math.radians(90), 0))


def build_zone_d_smart_transport(col, mats):
    """
    Zone D: Hero Electric City Bus, Autonomous Smart Pod Cars,
    Modern Glass Transit Bus Stop, EV Fast-Charging Hub, Smart Streetlights,
    and Intersection Traffic Signal Gantries.
    """
    # -------------------------------------------------------------
    # HERO ASSET: Electric City Bus ("FUTURE TRANSIT - 2050")
    # Positioned on North-South Avenue: centered at (1.5, -4.0, 0.0)
    # Dimensions: Length 5.4, Width 2.1, Height 2.2
    # -------------------------------------------------------------
    bus_x, bus_y = 1.5, -3.5
    
    # 1. Main Aerodynamic Chassis / Body
    bus_body = add_box("Hero_Bus_Body", (2.0, 5.2, 1.8), (bus_x, bus_y, 1.25), col, mats['bus_body'], bevel=0.18)
    
    # 2. Lower Teal Smart Electric Livery Stripe
    bus_stripe = add_box("Hero_Bus_Teal_Stripe", (2.04, 5.24, 0.35), (bus_x, bus_y, 0.65), col, mats['bus_teal'])
    
    # 3. Panoramic Wrap-Around Tinted Windscreen (Front & Rear)
    # Front windscreen (facing North towards intersection)
    add_box("Hero_Bus_Windscreen_Front", (1.92, 0.3, 0.85), (bus_x, bus_y + 2.5, 1.45), col, mats['glass'], bevel=0.08)
    # Rear window
    add_box("Hero_Bus_Window_Rear", (1.8, 0.2, 0.7), (bus_x, bus_y - 2.52, 1.45), col, mats['glass'], bevel=0.05)
    
    # 4. Side Passenger Windows (3 large bays on each side)
    for wy in [-1.5, 0.0, 1.5]:
        add_box(f"Hero_Bus_SideWindow_L_{wy}", (2.06, 1.2, 0.75), (bus_x, bus_y + wy, 1.45), col, mats['glass'])
        
    # 5. Dual Passenger Doors on Curbside (East side: X + 1.02)
    add_box("Hero_Bus_Doors", (0.05, 1.1, 1.5), (bus_x + 1.03, bus_y + 0.8, 1.05), col, mats['bus_black'])
    
    # 6. Roof-Mounted Smart Battery Pack & Air Filtration
    add_box("Hero_Bus_BatteryPack", (1.4, 3.2, 0.35), (bus_x, bus_y - 0.2, 2.25), col, mats['bldg_dark'], bevel=0.06)
    add_box("Hero_Bus_Battery_CoolingGrill", (1.2, 0.8, 0.08), (bus_x, bus_y + 1.0, 2.45), col, mats['bus_teal'])
    
    # 7. Front Digital LED Destination Matrix
    add_box("Hero_Bus_Dest_Display", (1.4, 0.08, 0.22), (bus_x, bus_y + 2.62, 1.95), col, mats['led_display'])
    
    # 8. LED Headlights & Taillights
    # Dual Headlights (Front, White LED)
    add_box("Hero_Bus_Headlight_L", (0.35, 0.08, 0.15), (bus_x - 0.65, bus_y + 2.62, 0.72), col, mats['headlight'])
    add_box("Hero_Bus_Headlight_R", (0.35, 0.08, 0.15), (bus_x + 0.65, bus_y + 2.62, 0.72), col, mats['headlight'])
    # Daytime LED Running Light Strip
    add_box("Hero_Bus_DRL_Strip", (1.6, 0.06, 0.04), (bus_x, bus_y + 2.63, 0.6), col, mats['teal_neon'])
    # Full-width Rear Ruby Red LED Light Bar
    add_box("Hero_Bus_Taillight_Bar", (1.8, 0.08, 0.12), (bus_x, bus_y - 2.62, 0.8), col, mats['taillight'])
    
    # 9. Aerodynamic Digital Side Mirrors
    add_box("Hero_Bus_Mirror_L", (0.35, 0.12, 0.08), (bus_x - 1.15, bus_y + 2.2, 1.5), col, mats['bus_black'])
    add_box("Hero_Bus_Mirror_R", (0.35, 0.12, 0.08), (bus_x + 1.15, bus_y + 2.2, 1.5), col, mats['bus_black'])
    
    # 10. 4 Detailed Wheels (Rubber Tires + Alloy Rims)
    wheel_y_positions = [bus_y + 1.6, bus_y - 1.6]
    for wy in wheel_y_positions:
        for wx, side in [(bus_x - 1.02, "Left"), (bus_x + 1.02, "Right")]:
            # Rubber Tire
            add_cylinder(f"Hero_Bus_Tire_{side}_{wy}", 0.42, 0.26, (wx, wy, 0.42), col, mats['tire'], vertices=24, rotation=(0, math.radians(90), 0))
            # Silver Alloy Rim
            add_cylinder(f"Hero_Bus_Rim_{side}_{wy}", 0.28, 0.28, (wx, wy, 0.42), col, mats['alloy'], vertices=16, rotation=(0, math.radians(90), 0))
            # Glowing Teal Hubcap
            add_cylinder(f"Hero_Bus_Hub_{side}_{wy}", 0.1, 0.30, (wx, wy, 0.42), col, mats['teal_neon'], vertices=12, rotation=(0, math.radians(90), 0))

    # -------------------------------------------------------------
    # Autonomous Smart Pod Cars (2 compact vehicles)
    # -------------------------------------------------------------
    # Car 1: Cruising on East-West road heading East: (8.0, 1.5)
    car1_x, car1_y = 8.0, 1.5
    add_box("SmartCar1_Chassis", (2.4, 1.4, 0.7), (car1_x, car1_y, 0.55), col, mats['bus_body'], bevel=0.1)
    add_box("SmartCar1_BubbleGlass", (1.6, 1.25, 0.55), (car1_x, car1_y, 0.95), col, mats['glass'], bevel=0.15)
    add_box("SmartCar1_Headlight", (0.06, 1.1, 0.08), (car1_x + 1.22, car1_y, 0.5), col, mats['headlight'])
    add_box("SmartCar1_Taillight", (0.06, 1.1, 0.08), (car1_x - 1.22, car1_y, 0.5), col, mats['taillight'])
    for cy in [car1_y - 0.7, car1_y + 0.7]:
        for cx in [car1_x - 0.7, car1_x + 0.7]:
            add_cylinder(f"SmartCar1_Wheel_{cx}_{cy}", 0.25, 0.18, (cx, cy, 0.25), col, mats['tire'], vertices=16, rotation=(math.radians(90), 0, 0))

    # Car 2: Parked in EV charging bay: (-1.5, 9.0)
    car2_x, car2_y = -1.5, 9.0
    add_box("SmartCar2_Chassis", (1.4, 2.4, 0.7), (car2_x, car2_y, 0.55), col, mats['orange_neon'], bevel=0.1)
    add_box("SmartCar2_BubbleGlass", (1.25, 1.6, 0.55), (car2_x, car2_y, 0.95), col, mats['glass'], bevel=0.15)
    for cx in [car2_x - 0.7, car2_x + 0.7]:
        for cy in [car2_y - 0.7, car2_y + 0.7]:
            add_cylinder(f"SmartCar2_Wheel_{cx}_{cy}", 0.25, 0.18, (cx, cy, 0.25), col, mats['tire'], vertices=16, rotation=(0, math.radians(90), 0))

    # -------------------------------------------------------------
    # Modern Glass Bus Transit Station / Shelter
    # Position: Curbside East of Bus at (3.8, -3.5)
    # -------------------------------------------------------------
    bs_x, bs_y = 3.9, -3.5
    # Shelter Base Paving
    add_box("BusStop_Paving", (1.4, 4.0, 0.04), (bs_x + 0.4, bs_y, 0.14), col, mats['sidewalk'])
    # Cantilevered Structural Glass Canopy
    add_box("BusStop_GlassCanopy", (1.6, 3.8, 0.08), (bs_x + 0.3, bs_y, 2.4), col, mats['glass'], bevel=0.02)
    # Rear Windscreen Glass Panel
    add_box("BusStop_RearGlass", (0.06, 3.6, 2.0), (bs_x + 1.1, bs_y, 1.25), col, mats['glass'])
    # Steel Support Posts
    add_cylinder("BusStop_Post_1", 0.06, 2.4, (bs_x + 1.05, bs_y - 1.6, 1.2), col, mats['metal_pole'], vertices=8)
    add_cylinder("BusStop_Post_2", 0.06, 2.4, (bs_x + 1.05, bs_y + 1.6, 1.2), col, mats['metal_pole'], vertices=8)
    # Integrated Waiting Bench
    add_box("BusStop_Bench", (0.45, 2.2, 0.35), (bs_x + 0.7, bs_y, 0.35), col, mats['stone'])
    # Digital Arrival Times Screen
    add_box("BusStop_DigitalScreen", (0.05, 0.7, 0.45), (bs_x + 1.05, bs_y - 1.2, 1.7), col, mats['teal_neon'])

    # -------------------------------------------------------------
    # EV Fast-Charging Hub
    # Position: West Sidewalk of North Avenue at (-3.9, 9.0)
    # -------------------------------------------------------------
    ev_x, ev_y = -3.9, 9.0
    for idx, ey in enumerate([ev_y - 1.0, ev_y + 1.0]):
        # Charging Pedestal
        add_box(f"EV_Station_{idx}", (0.4, 0.5, 1.4), (ev_x - 0.4, ey, 0.8), col, mats['bldg_white'], bevel=0.04)
        # Status Screen
        add_box(f"EV_Screen_{idx}", (0.04, 0.3, 0.25), (ev_x - 0.18, ey, 1.1), col, mats['teal_neon'])
        # Glowing LED charging cable holster
        add_cylinder(f"EV_Holster_{idx}", 0.05, 0.4, (ev_x - 0.18, ey - 0.15, 0.7), col, mats['teal_neon'], vertices=8)

    # -------------------------------------------------------------
    # Smart Streetlights (8 poles along sidewalks)
    # -------------------------------------------------------------
    streetlight_coords = [
        (-3.8, 6.0), (-3.8, 14.0), (3.8, 6.0), (3.8, 14.0),
        (-3.8, -6.0), (-3.8, -14.0), (3.8, -6.0), (3.8, -14.0)
    ]
    for idx, (lx, ly) in enumerate(streetlight_coords):
        # Vertical Pole
        add_cylinder(f"Streetlight_Pole_{idx}", 0.07, 3.4, (lx, ly, 1.7), col, mats['metal_pole'], vertices=8)
        # Curved Horizontal Arm pointing toward road
        arm_dir = 1.0 if lx < 0 else -1.0
        add_box(f"Streetlight_Arm_{idx}", (0.8, 0.08, 0.08), (lx + arm_dir * 0.4, ly, 3.4), col, mats['metal_pole'])
        # Downward LED Lamp Fixture
        add_box(f"Streetlight_Lamp_{idx}", (0.35, 0.18, 0.06), (lx + arm_dir * 0.75, ly, 3.35), col, mats['streetlight_glow'])

    # -------------------------------------------------------------
    # 4 Intersection Traffic Signal Gantries
    # Position: at corners of the intersection
    # -------------------------------------------------------------
    for idx, (tx, ty) in enumerate([(-3.8, 3.8), (3.8, 3.8), (3.8, -3.8), (-3.8, -3.8)]):
        add_cylinder(f"TrafficSignal_Post_{idx}", 0.08, 3.0, (tx, ty, 1.5), col, mats['metal_pole'], vertices=8)
        # Signal Box
        add_box(f"TrafficSignal_Box_{idx}", (0.22, 0.22, 0.65), (tx, ty, 2.8), col, mats['bldg_dark'])
        # Green & Red Signal Indicators
        add_cylinder(f"TrafficSignal_Green_{idx}", 0.07, 0.05, (tx, ty + 0.12, 2.65), col, mats['traffic_green'], vertices=10, rotation=(math.radians(90), 0, 0))
        add_cylinder(f"TrafficSignal_Red_{idx}", 0.07, 0.05, (tx, ty + 0.12, 2.95), col, mats['traffic_red'], vertices=10, rotation=(math.radians(90), 0, 0))


def setup_lighting(col):
    """
    Sets up a golden-hour architectural lighting environment:
    - Directional Warm Sun Light (crisp architectural shadows)
    - Soft Sky Area Light (fills crevices with cool ambient sky tone)
    - Ground Bounce Fill Light
    """
    # 1. Warm Sun Light (Golden Hour: ~4200K warm sunlight)
    sun_data = bpy.data.lights.new(name="GoldenHour_Sun", type='SUN')
    sun_data.energy = 4.8
    sun_data.color = (1.0, 0.90, 0.78)
    sun_data.angle = math.radians(12.0)  # Soft shadow penumbra
    sun_obj = bpy.data.objects.new(name="GoldenHour_Sun", object_data=sun_data)
    sun_obj.location = (25.0, -25.0, 32.0)
    # Point downward at ~45 degree angle towards center
    sun_obj.rotation_euler = (math.radians(52.0), math.radians(18.0), math.radians(-38.0))
    col.objects.link(sun_obj)
    
    # 2. Cool Sky Area Light (Ambient fill)
    sky_data = bpy.data.lights.new(name="Sky_Ambient_Fill", type='AREA')
    sky_data.shape = 'RECTANGLE'
    sky_data.size = 42.0
    sky_data.size_y = 42.0
    sky_data.energy = 280.0
    sky_data.color = (0.75, 0.85, 1.0)
    sky_obj = bpy.data.objects.new(name="Sky_Ambient_Fill", object_data=sky_data)
    sky_obj.location = (0.0, 0.0, 26.0)
    sky_obj.rotation_euler = (0, 0, 0)
    col.objects.link(sky_obj)

    # 3. Subtle Warm Ground Accent Light for Business Plaza
    plaza_light_data = bpy.data.lights.new(name="Plaza_Accent_Light", type='POINT')
    plaza_light_data.energy = 60.0
    plaza_light_data.color = (1.0, 0.85, 0.65)
    plaza_light_data.shadow_soft_size = 1.5
    plaza_light_obj = bpy.data.objects.new(name="Plaza_Accent_Light", object_data=plaza_light_data)
    plaza_light_obj.location = (-9.5, 9.5, 4.0)
    col.objects.link(plaza_light_obj)


def setup_camera(col):
    """
    Configures two architectural cameras:
    1. Master Isometric Orthographic Camera (framing full 40x40 diorama)
    2. Hero Close-Up Perspective Camera (focusing on the electric bus & intersection)
    """
    # 1. Master Isometric Camera
    cam_data = bpy.data.cameras.new("Isometric_Master_Camera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 62.0
    cam_data.shift_y = 0.16
    cam_data.shift_x = -0.04
    cam_data.clip_start = 0.5
    cam_data.clip_end = 350.0
    
    cam_obj = bpy.data.objects.new("Isometric_Master_Camera", cam_data)
    cam_obj.location = (44.0, -44.0, 38.0)
    cam_obj.rotation_euler = (math.radians(58.0), 0.0, math.radians(45.0))
    col.objects.link(cam_obj)
    
    # 2. Hero Transit Close-Up Camera with Track To constraint
    close_data = bpy.data.cameras.new("Hero_CloseUp_Camera")
    close_data.type = 'PERSP'
    close_data.lens = 45.0
    close_data.clip_start = 0.5
    close_data.clip_end = 250.0
    
    close_obj = bpy.data.objects.new("Hero_CloseUp_Camera", close_data)
    close_obj.location = (11.0, -14.0, 7.5)
    
    # Add Track To constraint targeting the bus area (1.5, -3.5, 1.5)
    bus_target = bpy.data.objects.new("Cam_Bus_Target", None)
    bus_target.location = (1.5, -3.5, 1.5)
    col.objects.link(bus_target)
    
    tt = close_obj.constraints.new(type='TRACK_TO')
    tt.target = bus_target
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'
    
    col.objects.link(close_obj)
    
    bpy.context.scene.camera = cam_obj
    return cam_obj


def safe_set_interpolation(obj, interp='BEZIER'):
    """Safely adjusts keyframe interpolation across Blender versions."""
    try:
        if not obj.animation_data or not obj.animation_data.action:
            return
        action = obj.animation_data.action
        if hasattr(action, "fcurves"):
            for fc in action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = interp
        elif hasattr(action, "layers"):
            for layer in action.layers:
                for strip in getattr(layer, "strips", []):
                    for ch in getattr(strip, "channelbags", []):
                        for fc in getattr(ch, "fcurves", []):
                            for kp in fc.keyframe_points:
                                kp.interpolation = interp
    except Exception:
        pass

def setup_animation(bus_name="Hero_Bus_Body", turbine_hub_name="WindTurbine_RotorHub", cam_obj=None):
    """
    Creates a smooth 240-frame (10 second at 24fps) animation:
    1. Hero Bus smoothly accelerates and cruises along the North-South Avenue.
    2. Wind Turbine rotor spins continuously.
    3. Subtle parallax camera motion enhancing 3D depth.
    """
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 240
    scene.render.fps = 24
    
    # 1. Bus Movement Animation (Cruising from Y = -12.0 to Y = 10.0 along the avenue)
    # Link all bus components to a parent Empty for smooth unified motion
    bus_parts = [o for o in bpy.data.objects if o.name.startswith("Hero_Bus_")]
    if bus_parts:
        bus_root = bpy.data.objects.new("Hero_Bus_Root", None)
        bpy.context.scene.collection.objects.link(bus_root)
        bus_root.location = (0, 0, 0)
        
        for part in bus_parts:
            part.parent = bus_root
            
        # Animate bus root Y position
        bus_root.location = (0, -8.0, 0)
        bus_root.keyframe_insert(data_path="location", frame=1)
        
        bus_root.location = (0, 10.0, 0)
        bus_root.keyframe_insert(data_path="location", frame=240)
        safe_set_interpolation(bus_root, 'BEZIER')
                    
    # 2. Wind Turbine Rotation
    hub = bpy.data.objects.get(turbine_hub_name)
    if hub:
        hub.rotation_euler = (0, math.radians(90), 0)
        hub.keyframe_insert(data_path="rotation_euler", frame=1)
        
        # 4 full rotations over 240 frames
        hub.rotation_euler = (math.radians(360 * 4), math.radians(90), 0)
        hub.keyframe_insert(data_path="rotation_euler", frame=240)
        safe_set_interpolation(hub, 'LINEAR')
                    
    # 3. Camera subtle drift
    if cam_obj:
        cam_obj.location = (42.0, -42.0, 35.0)
        cam_obj.keyframe_insert(data_path="location", frame=1)
        
        # Gentle cinematic pan across the scene
        cam_obj.location = (39.0, -45.0, 35.0)
        cam_obj.keyframe_insert(data_path="location", frame=240)
        safe_set_interpolation(cam_obj, 'BEZIER')


def configure_render_settings():
    """Configures high-quality Eevee render settings, resolution, and color management."""
    scene = bpy.context.scene
    
    # 1. Render Engine & Output
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    
    # 2. Color Management (Filmic / AgX with Medium High Contrast for punchy architectural look)
    scene.view_settings.view_transform = 'Standard' if 'Standard' in [v.name for v in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    try:
        scene.view_settings.look = 'Medium High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = 0.15
    scene.view_settings.gamma = 1.0
    
    # 3. World Ambient Lighting
    world = bpy.context.scene.world or bpy.data.worlds.new("World_FutureScape")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        # Deep architectural midnight slate background
        bg_node.inputs["Color"].default_value = (0.05, 0.06, 0.08, 1.0)
        bg_node.inputs["Strength"].default_value = 0.85


def main():
    print("=" * 60)
    print("Starting FUTURESCAPE 2050 Master Project Generation...")
    print("=" * 60)
    
    clear_scene()
    
    # Create Structured Collections
    cols = {
        'BASE': get_collection("BASE"),
        'ROADS': get_collection("ROADS"),
        'BUILDINGS': get_collection("BUILDINGS"),
        'VEGETATION': get_collection("VEGETATION"),
        'VEHICLES': get_collection("VEHICLES"),
        'SMART_INFRASTRUCTURE': get_collection("SMART_INFRASTRUCTURE"),
        'LIGHTS': get_collection("LIGHTS"),
        'CAMERA': get_collection("CAMERA"),
    }
    
    # 1. Material Palette
    print("--> Setting up Materials...")
    mats = setup_materials()
    
    # 2. Base Platform
    print("--> Building Base Platform...")
    build_platform(cols['BASE'], mats)
    
    # 3. Road Network
    print("--> Building Road Network & Sidewalks...")
    build_road_network(cols['ROADS'], mats)
    
    # 4. Zone A: Business District Skyscrapers
    print("--> Building Zone A: Business District Skyscrapers...")
    build_zone_a_business_district(cols['BUILDINGS'], mats)
    
    # 5. Zone B: Residential District
    print("--> Building Zone B: Residential District Apartments...")
    build_zone_b_residential_district(cols['BUILDINGS'], mats)
    
    # 6. Zone C: Central Urban Park
    print("--> Building Zone C: Central Urban Park & Water Feature...")
    build_zone_c_central_park(cols['VEGETATION'], mats)
    
    # 7. Zone F: Civic Centre
    print("--> Building Zone F: Civic Centre & Public Monument...")
    build_zone_f_civic_centre(cols['BUILDINGS'], mats)
    
    # 8. Zone E: Renewable Energy Infrastructure
    print("--> Building Zone E: Renewable Energy Hub & Wind Turbine...")
    build_zone_e_renewable_energy(cols['SMART_INFRASTRUCTURE'], mats)
    
    # 9. Zone D: Smart Transportation & Hero Bus
    print("--> Building Zone D: Smart Mobility, Bus & Infrastructure...")
    build_zone_d_smart_transport(cols['VEHICLES'], mats)
    
    # 10. Lighting & Environment
    print("--> Configuring Lighting...")
    setup_lighting(cols['LIGHTS'])
    
    # 11. Isometric Camera
    print("--> Setting up Isometric Camera...")
    cam = setup_camera(cols['CAMERA'])
    
    # 12. Animation
    print("--> Adding Keyframe Animation...")
    setup_animation(cam_obj=cam)
    
    # 13. Render Configuration
    print("--> Configuring Render Settings...")
    configure_render_settings()
    
    # Save .blend file
    blend_path = os.path.abspath("futurescape_2050.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"--> Saved master Blender file to: {blend_path}")
    print("=" * 60)
    print("FUTURESCAPE 2050 Generation Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
