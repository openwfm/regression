import subprocess
import os

def run_command(command, arguments, answers):
    process = subprocess.Popen([command] + arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        print(output, end='')  # Output to console

        if output == '' and process.poll() is not None:
            break

        for question, answer in answers.items():
            if question in output:
                process.stdin.write(answer + '\n')
                process.stdin.flush()
                break

    rc = process.poll()

    return rc

def configure(configure_opt="-d", option_number="1"):
    command = './configure'
    arguments = [configure_opt]
    answers = {'Enter selection [anything] : ': option_number}
    
    return run_command(command, arguments, answers)

def compile(build):
    command = './compile'
    arguments = [build, '>&', 'compile.log']
    answers = {'Compile for nesting?': '1'}

    return run_command(command, arguments, answers)

def build_wrf(configure_opt="-d", option_number="1", build="em_real"):
    configure_log = configure(configure_opt, option_number)
    if configure_log != 0:
        print("Error in configuration. Exiting...")
        return

    compile_log = compile(build)
    if compile_log != 0:
        print("Error in compilation. Exiting...")
        return

    with open('compile.log', 'r') as f:
        lines = f.readlines()

    if 'Executables successfully built' not in lines[-1]:
        print("Build was not successful.")
    else:
        print("Build was successful.")

