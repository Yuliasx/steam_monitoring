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
    demo_mode = True  # Поставь False для реальной работы
    
    if demo_mode:
        print("DEMO MODE - using test data")
        print("steam found at: C:/Program Files/Steam")
        print("")
        
        for i in range(5):
            print("check " + str(i + 1) + "/5:")
            
            if i < 3:
                print("game: Cyberpunk 2077")
                print("speed: " + str(12 - i) + ".5 MB/s")
                print("status: downloading")
            elif i == 3:
                print("game: Cyberpunk 2077")
                print("speed: 0 MB/s")
                print("status: paused")
            else:
                print("no active downloads")
            
            print("")
            
            if i < 4:
                time.sleep(5)  # 5 секунд вместо 60 для теста
        
        print("done")
        return

if __name__ == "__main__":
    main()