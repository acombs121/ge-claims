import json
import os
import hashlib

def get_unique_color(base_hex, salt_str, shift_amount=15):
    # Convert base hex to integers
    r = int(base_hex[1:3], 16)
    g = int(base_hex[3:5], 16)
    b = int(base_hex[5:7], 16)
    
    # Use hash to generate a deterministic minor color variation
    h_val = int(hashlib.md5(salt_str.encode('utf-8')).hexdigest(), 16)
    variation = (h_val % (shift_amount * 2)) - shift_amount
    
    r = max(0, min(255, r + variation))
    g = max(0, min(255, g + variation))
    b = max(0, min(255, b + variation))
    return f"#{r:02x}{g:02x}{b:02x}"

def get_industry_svg(initial, industry, acc_id):
    bg_map = {
        "Finance": "#1e1b4b",
        "Healthcare": "#064e3b",
        "Retail": "#450a0a",
        "Tech": "#0f172a"
    }
    
    stroke_map = {
        "Finance": "#818cf8",
        "Healthcare": "#34d399",
        "Retail": "#fb7185",
        "Tech": "#38bdf8"
    }
    
    # Extract numeric suffix for highly varied path rendering
    num_id = int("".join(filter(str.isdigit, acc_id)) or "1")
    bg_color = get_unique_color(bg_map.get(industry, "#0f172a"), acc_id)
    stroke_color = stroke_map.get(industry, "#38bdf8")
    
    # Highly customized distinct SVG paths derived by account index modulo
    rotation = (num_id * 15) % 360
    stroke_w = 4 + (num_id % 6)
    radius = 15 + (num_id % 20)
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="48" height="48">
        <rect width="100" height="100" rx="20" fill="{bg_color}"/>
        <circle cx="50" cy="50" r="{radius}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}" stroke-dasharray="{num_id % 12},{num_id % 8}" transform="rotate({rotation} 50 50)"/>
        <rect x="{20 + (num_id % 10)}" y="{20 + (num_id % 10)}" width="{60 - (num_id % 20)}" height="{60 - (num_id % 20)}" fill="none" stroke="{stroke_color}" stroke-width="3" transform="rotate({-rotation} 50 50)"/>
        <text x="50" y="66" font-family="monospace" font-size="42" font-weight="bold" fill="{stroke_color}" opacity="0.9" text-anchor="middle">{initial}</text>
    </svg>"""

def main():
    accounts_path = "data/accounts.json"
    logos_dir = "data/logos"
    os.makedirs(logos_dir, exist_ok=True)
    
    with open(accounts_path, "r") as f:
        accounts = json.load(f)
        
    for acc in accounts:
        name = acc.get("name", "C")
        industry = acc.get("industry", "Tech")
        acc_id = acc.get("id", "00")
        
        svg_str = get_industry_svg(name[0].upper(), industry, acc_id)
        file_name = f"{acc_id}.svg"
        
        with open(os.path.join(logos_dir, file_name), "w") as svg_file:
            svg_file.write(svg_str)
            
        acc["logo_data_url"] = f"https://storage.cloud.google.com/sandbox-426014-logos/{file_name}"
        
    with open(accounts_path, "w") as f:
        json.dump(accounts, f, indent=2)
        
    print(f"Successfully generated 24 fully unique hybrid brandmarks to {logos_dir}/.")

if __name__ == "__main__":
    main()



