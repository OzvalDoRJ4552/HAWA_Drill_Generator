from pathlib import Path
import math, csv

# ====================================================
# HAWA Concepta-style drill coordinate generator
# Prototype adaptation for 357 mm doors
# ----------------------------------------------------
# Outputs:
#   hawa_drill_coords.csv   - raw coordinates in inches
#   hawa_drill_coords.txt   - human-readable summary
#   hawa_drill_template.dxf - simple DXF with holes
#   hawa_template_preview.svg - SVG layout preview
# ====================================================

out_dir = Path("./outputs")
out_dir.mkdir(parents=True, exist_ok=True)

MM_PER_IN = 25.4

# -------------------- USER INPUTS --------------------
door_w_mm = 357.0           # door width (mm)
door_h_mm = 1209.5          # door height (mm)
cabinet_depth_mm = 435.0    # cabinet internal depth (mm)
door_thickness_in = 0.75    # door thickness (in)
center_gap_mm = 3.175       # 1/8" gap between doors (mm)

# Assumed offsets (can be changed as needed)
top_pivot_offset_mm = 70.0
side_pivot_offset_mm = 40.0
carriage_offset_from_front_mm = 20.0
carriage_spacing_mm = 40.0
# -----------------------------------------------------

# Conversions
door_w_in = door_w_mm / MM_PER_IN
door_h_in = door_h_mm / MM_PER_IN
cabinet_depth_in = cabinet_depth_mm / MM_PER_IN
center_gap_in = center_gap_mm / MM_PER_IN
door_thickness_mm = door_thickness_in * MM_PER_IN

# HAWA formula for frame offset
frame_offset_mm = 76.5 + door_thickness_mm
frame_offset_in = frame_offset_mm / MM_PER_IN

# Pocket depth (frame offset + margin)
pocket_depth_in = frame_offset_in + 0.2

# Pivot offsets (in)
top_pivot_in = top_pivot_offset_mm / MM_PER_IN
side_pivot_in = side_pivot_offset_mm / MM_PER_IN
carriage_offset_from_front_in = carriage_offset_from_front_mm / MM_PER_IN
carriage_spacing_in = carriage_spacing_mm / MM_PER_IN

# Total opening width
total_width_in = 2 * door_w_in + center_gap_in

# Left door pivot coords
lx_top = side_pivot_in
ly_top = top_pivot_in
lx_bot = side_pivot_in
ly_bot = door_h_in - top_pivot_in

# Right door pivot coords
right_outer_edge_x = door_w_in + center_gap_in + door_w_in
rx_top = right_outer_edge_x - side_pivot_in
ry_top = top_pivot_in
rx_bot = rx_top
ry_bot = door_h_in - top_pivot_in

# Carriage holes
car1_x = carriage_offset_from_front_in
car2_x = carriage_offset_from_front_in + carriage_spacing_in
car_y = 0.08  # small offset down from top

rail_centerline_in = frame_offset_in

# -------------------- OUTPUTS ------------------------

# CSV file
csv_path = out_dir / "hawa_drill_coords.csv"
with csv_path.open("w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["feature","door","x_in","y_in","notes"])
    writer.writerow(["pivot_top","left",f"{lx_top:.4f}",f"{ly_top:.4f}","from cabinet left-top"])
    writer.writerow(["pivot_bottom","left",f"{lx_bot:.4f}",f"{ly_bot:.4f}","from cabinet left-top"])
    writer.writerow(["pivot_top","right",f"{rx_top:.4f}",f"{ry_top:.4f}","from cabinet left-top"])
    writer.writerow(["pivot_bottom","right",f"{rx_bot:.4f}",f"{ry_bot:.4f}","from cabinet left-top"])
    writer.writerow(["carriage_hole","top",f"{car1_x:.4f}",f"{car_y:.4f}","hole1 from left"])
    writer.writerow(["carriage_hole","top",f"{car2_x:.4f}",f"{car_y:.4f}","hole2 from left"])
    writer.writerow(["rail_centerline","cabinet",f"{rail_centerline_in:.4f}","","from front face"])
    writer.writerow(["pocket_depth","cabinet",f"{pocket_depth_in:.4f}","","from front face"])

# TXT summary
txt_path = out_dir / "hawa_drill_coords.txt"
with txt_path.open("w") as f:
    f.write("HAWA-style drill coordinates (inches) - prototype\n\n")
    f.write(f"Door W = {door_w_in:.4f} in, Door H = {door_h_in:.4f} in, Thickness = {door_thickness_in:.4f} in\n")
    f.write(f"Cabinet depth = {cabinet_depth_in:.4f} in, Center gap = {center_gap_in:.4f} in\n\n")
    f.write(f"Frame offset (76.5 + D mm) = {frame_offset_in:.4f} in\n")
    f.write(f"Pocket depth estimate = {pocket_depth_in:.4f} in\n\n")
    f.write("Coordinates (origin = top-left of cabinet):\n")
    f.write(f"- Left top pivot: ({lx_top:.4f}, {ly_top:.4f}) in\n")
    f.write(f"- Left bottom pivot: ({lx_bot:.4f}, {ly_bot:.4f}) in\n")
    f.write(f"- Right top pivot: ({rx_top:.4f}, {ry_top:.4f}) in\n")
    f.write(f"- Right bottom pivot: ({rx_bot:.4f}, {ry_bot:.4f}) in\n")
    f.write(f"- Carriage holes: X = {car1_x:.4f} in & {car2_x:.4f} in at Y = {car_y:.4f} in\n")
    f.write(f"- Rail centerline = {rail_centerline_in:.4f} in from front\n")

# DXF file (outline + circles)
dxf_path = out_dir / "hawa_drill_template.dxf"
with dxf_path.open("w") as f:
    f.write("0\nSECTION\n2\nENTITIES\n")
    f.write("0\nPOLYLINE\n8\nOUTLINE\n66\n1\n10\n0\n20\n0\n")
    f.write("0\nVERTEX\n10\n0\n20\n0\n")
    f.write(f"0\nVERTEX\n10\n{total_width_in}\n20\n0\n")
    f.write(f"0\nVERTEX\n10\n{total_width_in}\n20\n{door_h_in}\n")
    f.write(f"0\nVERTEX\n10\n0\n20\n{door_h_in}\n")
    f.write("0\nSEQEND\n")
    def dxf_circle(cx,cy,r=0.125):
        f.write("0\nCIRCLE\n8\nHOLES\n")
        f.write(f"10\n{cx}\n20\n{cy}\n30\n0.0\n40\n{r}\n")
    for (cx,cy) in [(lx_top,ly_top),(lx_bot,ly_bot),(rx_top,ry_top),(rx_bot,ry_bot),
                    (car1_x,car_y),(car2_x,car_y)]:
        dxf_circle(cx,cy)
    f.write("0\nENDSEC\n0\nEOF\n")

# SVG preview
svg_path = out_dir / "hawa_template_preview.svg"
with svg_path.open("w") as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width_in+2} {door_h_in+2}" '
            f'width="{(total_width_in+2)*96}" height="{(door_h_in+2)*96}">\n')
    f.write(f'<rect x="0.5" y="0.5" width="{total_width_in}" height="{door_h_in}" fill="none" stroke="black"/>\n')
    f.write(f'<rect x="0.5" y="0.5" width="{door_w_in}" height="{door_h_in}" fill="none" stroke="blue"/>\n')
    f.write(f'<rect x="{0.5+door_w_in+center_gap_in}" y="0.5" width="{door_w_in}" height="{door_h_in}" fill="none" stroke="blue"/>\n')
    for (cx,cy) in [(lx_top,ly_top),(lx_bot,ly_bot),(rx_top,ry_top),(rx_bot,ry_bot)]:
        f.write(f'<circle cx="{cx}" cy="{cy}" r="0.125" fill="red"/>\n')
    f.write(f'<circle cx="{car1_x}" cy="{car_y}" r="0.1" fill="green"/>\n')
    f.write(f'<circle cx="{car2_x}" cy="{car_y}" r="0.1" fill="green"/>\n')
    f.write(f'<line x1="{rail_centerline_in}" y1="0" x2="{rail_centerline_in}" y2="{door_h_in}" '
            f'stroke="orange" stroke-dasharray="0.1 0.1"/>\n')
    f.write('</svg>')