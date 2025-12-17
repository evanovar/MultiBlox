
    def enable_multi_roblox(self):
        """Enable Multi Roblox + 773 fix"""
        # hello programmers! I know you're reading this code, because you want to know how did I implement this feature in Python. (and most importantly, the 773 fix)
        # because of that, I'll leave some comments here to help you understand.
        import subprocess
        import win32event
        import win32api
        
        if self.multi_roblox_handle is not None:
            self.disable_multi_roblox()
        
        # first, we check if roblox is running, this is very important.
        # if roblox is running, we cannot enable multi roblox, because the mutex is already created by the running instance.
        # so we ask the user for permission to close all roblox processes.
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq RobloxPlayerBeta.exe'], 
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW) # checks running processes
            
            if result.stdout and 'RobloxPlayerBeta.exe' in result.stdout:
                response = messagebox.askquestion( # ask user for permission
                    "Roblox Already Running",
                    "A Roblox instance is already running.\n\n"
                    "To use Multi Roblox, you need to close all Roblox instances first.\n\n"
                    "Do you want to close all Roblox instances now?",
                    icon='warning'
                )
                
                if response == 'yes':
                    subprocess.run(['taskkill', '/F', '/IM', 'RobloxPlayerBeta.exe'], 
                                 capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW) # closes roblox
                    time.sleep(1) # wait a second to ensure all processes are closed
                    messagebox.showinfo("Success", "All Roblox instances have been closed.")
                else:
                    return False
            
            # then here's the magic:
            # to enable multi roblox, we create the mutex before roblox creates it.
            # this means, when roblox starts, it cannot be created by roblox again.
            # thus, allowing multiple instances to run. Simple, right? (doesn't fix 773 yet)
            mutex = win32event.CreateMutex(None, True, "ROBLOX_singletonEvent")
            print("[INFO] Multi Roblox activated.")
            
            # check if mutex already existed (GetLastError returns ERROR_ALREADY_EXISTS = 183)
            if win32api.GetLastError() == 183:
                print("[WARNING] Mutex already exists. Taking ownership...")
            
            # now let's get over on the 773 fix part
            # first, we need to find the RobloxCookies.dat file
            cookies_path = os.path.join(
                os.getenv('LOCALAPPDATA'),
                r'Roblox\LocalStorage\RobloxCookies.dat'
            )
            
            cookie_file = None
            if os.path.exists(cookies_path):
                try:
                    # to actually apply the 773 fix, we need to lock the cookies file
                    # this prevents roblox from accessing it, which causes error 773 to not appear
                    # and there, you have it, multi roblox + 773 fix!
                    cookie_file = open(cookies_path, 'r+b')
                    msvcrt.locking(cookie_file.fileno(), msvcrt.LK_NBLCK, os.path.getsize(cookies_path))
                    print("[INFO] Error 773 fix applied.")

                except OSError:
                    print("[ERROR] Could not lock RobloxCookies.dat. It may already be locked.")

            else:
                print("[ERROR] Cookies file not found. 773 fix skipped.")

            self.multi_roblox_handle = {'mutex': mutex, 'file': cookie_file}
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable Multi Roblox: {str(e)}")
            return False