from autofill import file_to_json, add_url, registered_subprocess
import threading
import subprocess
import json

def unit_test():
    forms = file_to_json('forms.py')
    add_url(forms)

    for form in forms:
        form_json= json.dumps(form)
        # print(form_json)
        t = threading.Thread(target=registered_subprocess, args=(form_json,'token.txt'))
        t.start()

def main():
    forms = file_to_json('forms.py')
    add_url(forms)

    for form in forms:
        form_json = 'test'#json.dumps(form)
        token_path = 'token.txt'
        print(form_json)
        cmd = f'start cmd /k "python autofill.py {form_json} {token_path}"'
        subprocess.Popen(cmd, shell=True)

if __name__ == "__main__":
    main()