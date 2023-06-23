
# Parts of this code are based on code provided by ChatGPT by OpenAI.

import subprocess
import os

def run_command(command, arguments, answers, **kwargs):
    """
    This function runs a command with arguments and interactive answers.
    :param command: The command to be executed.
    :param arguments: The arguments to be passed to the command.
    :param answers: A dictionary of prompts and their corresponding answers.
    :return: The return code of the process.
    """

    if arguments == ['']:
        cmdlist = command
    else:
        cmdlist = [command] + arguments

    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True, bufsize=1)

    current_line = ""
    while True:
        output_char = process.stdout.read(1)
        print(output_char, end='', flush=True)  # Output to console
        current_line += output_char

        if output_char == '' and process.poll() is not None:
            break

        for question, answer in answers.items():
            if question in current_line:
                print(' ' + answer + '\n')
                process.stdin.write(answer + '\n')
                process.stdin.flush()
                current_line = ""
                break

    rc = process.poll()

    return rc

def clone(git_url="",clone_dir="",**kwargs):
    """
    This function clones a git repository.
    :param git_url: url of the repository
    :param clone dir: directory name of the clone
    :return: The return code of the clone process.
    """
    # Run git clone
    return run_command('git',['clone', git_url, clone_dir], {})

def configure(configure_opt="", option_number="34", nesting="1"):
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
    answers = {'Enter selection': option_number,'Compile for nesting':nesting}
    
    return run_command(command, arguments, answers)

def compile(build):
    """
    This function runs the compile part of the WRF build process.
    :param build: The build string to be passed to the ./compile script.
    :return: The return code of the compile process.
    """
    command = './compile'
    arguments = [build]

    return run_command(command, arguments, {})

def build_wrf(configure_opt="", option_number="1", nesting="1", build="em_fire", **kwargs):
    """
    This function orchestrates the WRF build process by first running configuration and then compile. 
    :param configure_opt: The configuration options to be passed to the ./configure script.
    :param option_number: The option to be selected when the configure script prompts for selection.
    :param build: The build string to be passed to the ./compile script.
    :return: None.
    """
    configure_log = configure(configure_opt=configure_opt, option_number=option_number, nesting=nesting)
    
    # Check if the configure.wrf file exists after running configure
    if configure_log != 0 or not os.path.exists('configure.wrf'):
        print("Error in configuration. Exiting...")
        return

    if build is None:
        print("Build not requested. Exiting...")
        return

    compile_log = compile(build)
    if compile_log != 0:
        print("Error in compile. Exiting...")
        return

    with open('compile.log', 'r') as f:
        lines = f.readlines()

    if 'Executables successfully built' not in lines[-1]:
        print("Build was not successful.")
    else:
        print("Build was successful.")

# __main__ entry point for testing
if __name__ == "__main__":

    conf = {
            "git_url" : "https://github.com/openwfm/WRF-SFIRE",
            "clone_dir" : "wrf-sfire-local",
            "commit" : "master",
            "configure_opt" : "-d",
            "option_number" : "34",
            "nesting" : "1",
            "build" : "em_fire"
            } 

    clone(**conf) 
    os.chdir(conf['clone_dir'])
    build_wrf(**conf)
