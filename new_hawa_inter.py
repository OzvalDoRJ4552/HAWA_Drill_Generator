import csv
import os
import ezdxf
import svgwrite

# -------------------- USER INPUTS --------------------
print("=== HAWA Drill Template Generator ===")

door_w_mm = float(input("Enter door width (mm): "))
door_h_mm = float(input("Enter door height (mm): "))
cabinet_depth_mm = float(input("Enter cabinet depth (mm): "))
door_thickness_in = float(input("Enter door thickness (inches): "))

# Optional with defaults
center_gap_mm = input("Enter center gap between doors (mm) [default 3.175 mm = 1/8\"]: ")
center_gap_mm = float(center_gap_mm) if center_gap_mm else 3.175

top_pivot_offset_mm = input("Top pivot offset from top (mm) [default 70]: ")
top_pivot_offset_mm = float(top_pivot_offset_mm) if top_pivot_offset_mm else 70.0

side_pivot_offset_mm = input("Side pivot offset from edge (mm) [default 40]: ")
side_pivot_offset_mm = float(side_pivot_offset_mm) if side_pivot_offset_mm else 40.0

carriage_offset_from_front_mm = input("Carriage hole offset from front (mm) [default 20]: ")
carriage_offset_from_front_mm = float(carriage_offset_from_front_mm) if carriage_offset_from_front_mm else 20.0

carriage_spacing_mm = input("Carriage hole spacing (mm) [default 40]: ")
carriage_spacing_mm = float(carriage_spacing_mm) if carriage_spacing_mm else 40.0
# -----------------------------------------------------

# -------------------- CALCULATIONS -------------------
MM_TO_IN = 25.4
door_w_in = door_w_mm / MM_TO_IN
door_h_in = door_h_mm / MM_TO_IN
cabinet_depth_in = cabinet_depth_mm / MM_TO_IN

frame_offset_in = (76.5 + (door_thickness_in * MM_TO_IN)) / MM_TO_IN
pocket_depth_in = cabinet_depth_in - door_thickness_in

# Drill coordinates (example logic)
pivots = [
    (side_pivot_offset_mm / MM_TO_IN, top_pivot_offset_mm / MM_TO_IN),  # top-left pivot
    (door_w_in - side_pivot_offset_mm / MM_TO_IN, top_pivot_offset_mm / MM_TO_IN)  # top-right pivot
]

carriages = [
    (carriage_offset_from_front_mm / MM_TO_IN, door_h_in - 2.0),
    (carriage_offset_from_front_mm / MM_TO_IN + carriage_spacing_mm / MM_TO_IN, door_h_in - 2.0)
]
# -----------------------------------------------------

# -------------------- OUTPUT FOLDER ------------------
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)
# -----------------------------------------------------

# -------------------- SAVE CSV -----------------------
csv_path = os.path.join(output_dir, "hawa_drill_coords.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Type", "X (in)", "Y (in)"])
    for (x, y) in pivots:
        writer.writerow(["Pivot", x, y])
    for (x, y) in carriages:
        writer.writerow(["Carriage", x, y])
print(f"✅ CSV saved to {csv_path}")
# -----------------------------------------------------

# -------------------- SAVE TXT -----------------------
txt_path = os.path.join(output_dir, "hawa_drill_coords.txt")
with open(txt_path, "w") as f:
    f.write("HAWA Drill Coordinates (inches)\n")
    f.write(f"Door W={door_w_in:.3f}, H={door_h_in:.3f}, Thickness={door_thickness_in:.3f}\n")
    f.write(f"Cabinet depth={cabinet_depth_in:.3f}, Frame offset={frame_offset_in:.3f}, Pocket depth={pocket_depth_in:.3f}\n\n")
    for (x, y) in pivots:
        f.write(f"Pivot hole @ ({x:.3f}, {y:.3f})\n")
    for (x, y) in carriages:
        f.write(f"Carriage hole @ ({x:.3f}, {y:.3f})\n")
print(f"✅ TXT saved to {txt_path}")
# -----------------------------------------------------

# -------------------- SAVE SVG -----------------------
svg_path = os.path.join(output_dir, "hawa_template_preview.svg")
dwg = svgwrite.Drawing(svg_path, profile="tiny", size=(f"{door_w_in*50}px", f"{door_h_in*50}px"))

# Door outline
dwg.add(dwg.rect(insert=(0, 0), size=(door_w_in*50, door_h_in*50),
                 stroke="black", fill="none", stroke_width=2))

# Holes
for (x, y) in pivots + carriages:
    dwg.add(dwg.circle(center=(x*50, y*50), r=5, stroke="red", fill="none", stroke_width=2))

dwg.save()
print(f"✅ SVG saved to {svg_path}")
# -----------------------------------------------------

# -------------------- SAVE DXF -----------------------
def export_dxf(coords, door_w_in, door_h_in, output_dir="outputs"):
    dxf_path = os.path.join(output_dir, "hawa_drill_template.dxf")
    doc = ezdxf.new(dxfversion="R2018")  # AutoCAD 2018 format (works in 2022+)
    msp = doc.modelspace()

    # Layers
    doc.layers.new(name="OUTLINE", dxfattribs={"color": 7})
    doc.layers.new(name="DRILL_HOLES", dxfattribs={"color": 1})
    doc.layers.new(name="TEXT", dxfattribs={"color": 3})
    doc.layers.new(name="CENTERLINES", dxfattribs={"color": 5})
    doc.layers.new(name="DIMENSIONS", dxfattribs={"color": 2})

    # Door outline
    msp.add_lwpolyline([
        (0, 0),
        (door_w_in, 0),
        (door_w_in, door_h_in),
        (0, door_h_in),
        (0, 0)
    ], dxfattribs={"layer": "OUTLINE"})

    # Centerlines
    msp.add_line((0, door_h_in/2), (door_w_in, door_h_in/2), dxfattribs={"layer": "CENTERLINES"})
    msp.add_line((door_w_in/2, 0), (door_w_in/2, door_h_in), dxfattribs={"layer": "CENTERLINES"})

    # Drill holes
    for (x, y) in coords:
        msp.add_circle((x, y), 0.1, dxfattribs={"layer": "DRILL_HOLES"})
        msp.add_line((x-0.2, y), (x+0.2, y), dxfattribs={"layer": "DRILL_HOLES"})
        msp.add_line((x, y-0.2), (x, y+0.2), dxfattribs={"layer": "DRILL_HOLES"})
        msp.add_text(
            f"Hole ({x:.2f}, {y:.2f}) in",
            dxfattribs={"height": 0.25, "layer": "TEXT"}
        ).set_pos((x+0.3, y+0.3))

    # Dimension style
    dimstyle = doc.dimstyles.get("EZDXF")
    dimstyle.dxf.dimtxt = 0.25
    dimstyle.dxf.dimasz = 0.18

    # Door width dimension
    msp.add_linear_dim(
        base=(0, -0.75),
        p1=(0, 0), p2=(door_w_in, 0),
        dimstyle="EZDXF"
    ).render(msp, dxfattribs={"layer": "DIMENSIONS"})

    # Door height dimension
    msp.add_linear_dim(
        base=(-0.75, 0),
        p1=(0, 0), p2=(0, door_h_in),
        angle=90, dimstyle="EZDXF"
    ).render(msp, dxfattribs={"layer": "DIMENSIONS"})

    # Save
    doc.saveas(dxf_path)
    print(f"✅ DXF saved to {dxf_path} (detailed w/ AutoCAD-style dimensions)")

export_dxf(pivots + carriages, door_w_in, door_h_in, output_dir)
# -----------------------------------------------------
