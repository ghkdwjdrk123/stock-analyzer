"""
Check Kiwoom OpenAPI OCX registration status
"""
import winreg

try:
    # Check ProgID -> CLSID mapping
    key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'KHOPENAPI.KHOpenAPICtrl.1\CLSID')
    clsid = winreg.QueryValue(key, '')
    print(f'[OK] ProgID registered')
    print(f'     CLSID: {clsid}')

    # Check CLSID exists
    key2 = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f'CLSID\\{clsid}')
    print(f'[OK] CLSID exists in registry')

    # Check InprocServer32 (DLL path)
    try:
        key3 = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f'CLSID\\{clsid}\\InprocServer32')
        dll_path = winreg.QueryValue(key3, '')
        print(f'[OK] DLL Path registered: {dll_path}')

        # Check if file exists
        import os
        if os.path.exists(dll_path):
            print(f'[OK] DLL file exists')
        else:
            print(f'[ERROR] DLL file not found at: {dll_path}')

    except FileNotFoundError:
        print(f'[ERROR] InprocServer32 key not found')
        print(f'[ERROR] OCX is NOT properly registered!')
        print(f'\nTo fix:')
        print(f'  Run as Administrator:')
        print(f'  regsvr32 C:\\OpenAPI\\khopenapi.ocx')

except Exception as e:
    print(f'[ERROR] Failed to check registration: {e}')
