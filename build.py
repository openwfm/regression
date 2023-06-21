import subprocess
import os

def run_command(command, arguments, answers):
    """
    This function runs a command with arguments and interactive answers.
    :param command: The command to be executed.
    :param arguments: The arguments to be passed to the command.
    :param answers: A dictionary of prompts and their corresponding answers.
    :return: The return code of the process. 
    """
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
    """
    This function runs the configuration part of the WRF build process.
    :param configure_opt: The configuration options to be passed to the ./configure script.
    :param option_number: The option to be selected when the configure script prompts for selection.
    :return: The return code of the configure process.
    """
    # Run ./clean -a before configure
    run_command('./clean', ['-a'], {})
    
    command = './configure'
    arguments = [configure_opt]
    answers = {'Enter selection [anything] : ': option_number}
    
    return run_command(command, arguments, answers)

def compile(build):
    """
    This function runs the compile part of the WRF build process.
    :param build: The build string to be passed to the ./compile script.
    :return: The return code of the compile process.
    """
    command = './compile'
    arguments = [build, '>&', 'compile.log']
    answers = {'Compile for nesting?': '1'}

    return run_command(command, arguments, answers)

def build_wrf(configure_opt="-d", option_number="1", build="em_real"):
    """
    This function orchestrates the WRF build process by first running configuration and then compile. 
    :param configure_opt: The configuration options to be passed to the ./configure script.
    :param option_number: The option to be selected when the configure script prompts for selection.
    :param build: The build string to be passed to the ./compile script.
    :return: None.
    """
    configure_log = configure(configure_opt, option_number)
    
    # Check if the configure.wrf file exists after running configure
    if configure_log != 0 or not os.path.exists('configure.wrf'):
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

# __main__ entry point for testing
if __name__ == "__main__":
    print("Testing the run_command function...")
    run_command('ls', ['-l'], {})
    
    print("\nTesting the build_wrf function...")
    build_wrf()

