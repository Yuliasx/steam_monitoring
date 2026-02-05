import winreg
import os
import time
import re

def get_steam_path():
    try:
        a = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        b, c = winreg.QueryValueEx(a, "SteamPath")
        winreg.CloseKey(a)
        return b
    except:
        try:
            a = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
            b, c = winreg.QueryValueEx(a, "InstallPath")
            winreg.CloseKey(a)
            return b
        except:
            return None

def read_log_file(path):
    log_path = os.path.join(path, "logs", "content_log.txt")
    if not os.path.exists(log_path):
        return None
    
    try:
        f = open(log_path, "r", encoding="utf-8", errors="ignore")
        lines = f.readlines()
        f.close()
        return lines
    except:
        return None

def parse_download_info(lines):
    if not lines:
        return None, None, None
    
    game = None
    speed = None
    status = None
    
    lines.reverse()
    
    for line in lines:
        if "Download" in line or "download" in line:
            parts = line.split()
            for i in range(len(parts)):
                if "MB/s" in parts[i] or "KB/s" in parts[i]:
                    speed = parts[i-1] + " " + parts[i]
                if "AppID" in parts[i]:
                    try:
                        app_id = parts[i+1].replace(",", "").replace(":", "")
                        game = app_id
                    except:
                        pass
            
            if "paused" in line.lower() or "pause" in line.lower():
                status = "paused"
            elif "complete" in line.lower():
                status = "complete"
            else:
                status = "downloading"
            
            if speed:
                break
    
    return game, speed, status

def check_downloading_folder(path):
    dl_path = os.path.join(path, "steamapps", "downloading")
    if not os.path.exists(dl_path):
        return None
    
    items = os.listdir(dl_path)
    if len(items) > 0:
        return items[0]
    return None

def get_game_name(path, app_id):
    manifest_path = os.path.join(path, "steamapps")
    if not os.path.exists(manifest_path):
        return app_id
    
    files = os.listdir(manifest_path)
    for file in files:
        if file.startswith("appmanifest_") and file.endswith(".acf"):
            if app_id in file:
                try:
                    full = os.path.join(manifest_path, file)
                    f = open(full, "r", encoding="utf-8", errors="ignore")
                    content = f.read()
                    f.close()
                    
                    match = re.search(r'"name"\s+"([^"]+)"', content)
                    if match:
                        return match.group(1)
                except:
                    pass
    
    return app_id

def main():
    print("looking for steam")
    
    steam_path = get_steam_path()
    if not steam_path:
        print("steam not found")
        return
    
    print("steam found at: " + steam_path)
    print("")
    
    count = 0
    max_count = 5
    
    while count < max_count:
        current_app = check_downloading_folder(steam_path)
        
        if current_app:
            game_name = get_game_name(steam_path, current_app)
            print("game: " + game_name)
            
            lines = read_log_file(steam_path)
            game, speed, status = parse_download_info(lines)
            
            if speed:
                print("speed: " + speed)
            else:
                print("speed: unknown")
            
            if status:
                print("status: " + status)
            else:
                print("status: downloading")
        else:
            print("no active downloads")
        
        print("")
        count = count + 1
        
        if count < max_count:
            time.sleep(60)
    
    print("done")

if __name__ == "__main__":
    main()