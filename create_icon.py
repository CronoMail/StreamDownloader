import base64
import os

def create_icon_file():
    """Create an icon file from the Base64 data"""
    base64_file = os.path.join("resources", "icon.base64")
    icon_file = os.path.join("resources", "icon.ico")
    
    if not os.path.exists(base64_file):
        print(f"Base64 file not found: {base64_file}")
        return False
    
    # Read the base64 file, stripping comments and whitespace
    with open(base64_file, 'r') as f:
        content = f.read()
    
    # Strip comments and whitespace
    lines = content.split('\n')
    data_lines = []
    for line in lines:
        if line.startswith('/*') or line.endswith('*/') or not line.strip():
            continue
        data_lines.append(line.strip())
    
    base64_data = ''.join(data_lines)
    
    # Decode the base64 data
    try:
        icon_data = base64.b64decode(base64_data)
        
        # Write the icon file
        with open(icon_file, 'wb') as f:
            f.write(icon_data)
        
        print(f"Icon file created: {icon_file}")
        return True
    except Exception as e:
        print(f"Error creating icon file: {str(e)}")
        return False

if __name__ == "__main__":
    create_icon_file()
