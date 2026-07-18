import k
import sys

# Device Lock စနစ်ကို အရင်စစ်ဆေးပါမယ်
if k.check_activation():
    # Activation အောင်မြင်ရင် Main Menu ကို loop ပတ်ပြီး ဖွင့်ပါမယ်
    while True:
        try:
            k.main_menu()
            choice = input(f"\n\033[1;33mSelect Option (1, 2 or 3 to Exit): \033[1;00m").strip()
            
            if choice == '1':
                k.option_adb_connect()
            elif choice == '2':
                k.option_auto_bypass()
            elif choice == '3':
                print("\n\033[1;32m[+] Goodbye!\033[1;00m")
                break
            else:
                print("\033[1;31m[-] Invalid Option!\033[1;00m")
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\033[1;32m[+] Goodbye!\033[1;00m")
            break
        except Exception as e:
            print(f"\033[1;31m[-] Error: {str(e)}\033[1;00m")
            break
