def rgb_to_hex(r, g, b):
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"

def hex_to_rgb(hex_str):
    hex_str = hex_str.strip().lstrip('#')
    if len(hex_str) != 6:
        return None
    try:
        return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
    except ValueError:
        return None
