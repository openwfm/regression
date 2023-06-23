
# Parts of this code are based on code provided by ChatGPT by OpenAI.

import subprocess
import shutil
import os
import os.path as osp

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

    process_output = ""
    current_line = ""
    while True:
        output_char = process.stdout.read(1)
        print(output_char, end='', flush=True)  # Output to console
        current_line += output_char
        process_output += output_char
        rc = process.poll()

        if output_char == '' and rc is not None:
            break

        for question, answer in answers.items():
            if question in current_line:
                print(' ' + answer + '\n')
                process.stdin.write(answer + '\n')
                process.stdin.flush()
                current_line = ""
                break

    return {'code': rc, 'output': process_output}

def clone(git_url="", clone_dir="", **kwargs):
    """
    This function clones a git repository.
    :param git_url: url of the repository
    :param clone dir: directory name of the clone
    :return: The return code of the clone process.
    """
    # Clean clone directory
    if osp.exists(clone_dir):
        shutil.rmtree(clone_dir)
    # Run git clone
    arguments = ['clone', git_url, clone_dir]
    print('cloning: ', arguments)
    return run_command('git',arguments, {})

def checkout(commit="", **kwargs):
    """
    This function checks out git branch.
    :param commit: branch or commit to checkout.
    :param clone_dir: directory name of the clone.
    :return: The return code of the clone process.
    """
    # Run git checkout
    return run_command('git',['checkout', commit], {})

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

def build_wrf(commit, configure_opt="", option_number="1", nesting="1", 
              build="em_fire", clone_dir="", **kwargs):
    """
    This function orchestrates the WRF build process by first running configuration and then compile. 
    :param commit: The branch or commit to checkout before building the code.
    :param configure_opt: The configuration options to be passed to the ./configure script.
    :param option_number: The option to be selected when the configure script prompts for selection.
    :param build: The build string to be passed to the ./compile script.
    :param clone_dir: directory to the clone.
    :return: None.
    """

    print('Building in ' + clone_dir)
    os.chdir(clone_dir)

    # checking out commit
    checkout(commit)

    configure_return = configure(configure_opt=configure_opt,
                              option_number=option_number,
                              nesting=nesting)
    # Check if the configure.wrf file exists after running configure
    if configure_return['code'] != 0 or not os.path.exists('configure.wrf'):
        print("Error in configuration. Exiting...")
        return

    if build is None:
        print("Build not requested. Exiting...")
        return 1
    
    compile_return = compile(build)

    if compile_return['code'] != 0:
        print("Error in compile. Exiting...")
        return 1

    compile_out = compile_return['output']

    if 'Executables successfully built' not in compile_out[-1]:
        print("Build was not successful.")
        return 1
    else:
        print("Build was successful.")

def run_local(clone_dir, n_proc="1", dmpar=True, **kwargs):
    print('not done yet')

def run_wrf_sub(clone_dir, n_proc="1", dmpar=True, **kwargs):
    """
    This function runs WRF case.
    :param clone_dir: The configuration options to be passed to the ./configure script.
    :param option_number: The option to be selected when the configure script prompts for selection.
    :param build: The build string to be passed to the ./compile script.
    :return: None.
    """
    print('not done yet')

# __main__ entry point for testing
if __name__ == "__main__":

    conf = {
            "git_url" : "https://github.com/openwfm/WRF-SFIRE",
            "clone_dir" : "wrf-sfire-local",
            "commit" : "develop-61",
            "configure_opt" : "-d",
            "option_number" : "34",
            "nesting" : "1",
            "build" : "em_fire",
            "qsub": "/tmp/aws_mpi.sub"
            } 

    conf['clone_dir'] = osp.abspath(conf['clone_dir']) 

    clone(**conf) 
    build_wrf(**conf)
