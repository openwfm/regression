# Parts of this code are based on code provided by ChatGPT by OpenAI.

import subprocess
import shutil
import os
import os.path as osp
import f90nml
import logging


def ensure_dir(path):
    """
    Ensure all directories in path if a file exist, for convenience return path itself.

    :param path: the path whose directories should exist
    :return: the path back for convenience
    """
    if not osp.isdir(path):
        path_dir = osp.dirname(path)
    else:
        path_dir = path
    if not osp.exists(path_dir):
        os.makedirs(path_dir)
    return path


def force_symlink(link_tgt, link_loc):
    """
    Create a symlink at link_loc pointing to link_tgt and delete if the file already exists.

    :param link_tgt: link target
    :param link_loc: link location
    """
    logging.info("Linking %s -> %s" % (link_loc, link_tgt))
    if osp.isfile(link_tgt) or osp.isdir(link_tgt):
        if not osp.lexists(link_loc):
            os.symlink(link_tgt, link_loc)
        else:
            os.remove(link_loc)
            os.symlink(link_tgt, link_loc)
    else:
        logging.error("Link target %s does not exist" % link_tgt)


def run_command(command, arguments, answers, **kwargs):
    """
    This function runs a command with arguments and interactive answers.
    :param command: The command to be executed.
    :param arguments: The arguments to be passed to the command.
    :param answers: A dictionary of prompts and their corresponding answers.
    :return: The return code of the process.
    """

    if arguments == [""]:
        cmdlist = command
    else:
        cmdlist = [command] + arguments
        
    logging.info("running command: {}".format(' '.join(cmdlist)))
    process = subprocess.Popen(
        cmdlist, stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True, bufsize=1
    )

    process_output = ""
    current_line = ""
    while True:
        output_char = process.stdout.read(1)
        #print(output_char, end="", flush=True)  # Output to console
        current_line += output_char
        process_output += output_char
        rc = process.poll()

        if output_char == "" and rc is not None:
            break

        for question, answer in answers.items():
            if question in current_line:
                logging.info(f" {answer}\n")
                process.stdin.write(f"{answer}\n")
                process.stdin.flush()
                current_line = ""
                break

    return {"code": rc, "output": process_output}


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
    arguments = ["clone", git_url, clone_dir]
    return run_command("git", arguments, {})


def checkout(commit="", **kwargs):
    """
    This function checks out git branch.
    :param commit: branch or commit to checkout.
    :param clone_dir: directory name of the clone.
    :return: The return code of the clone process.
    """
    # Run git checkout
    return run_command("git", ["checkout", commit], {})


def configure(config_optim="", config_option="34", nesting="1"):
    """
    This function runs the configuration part of the WRF build process.
    :param config_optim: The configuration options to be passed to the ./configure script.
    :param config_option: The option to be selected when the configure script prompts for selection.
    :return: The return code of the configure process.
    """
    # Run ./clean -a before configure
    run_command("./clean", ["-a"], {})

    command = "./configure"
    arguments = [config_optim]
    answers = {"Enter selection": config_option, "Compile for nesting": nesting}

    return run_command(command, arguments, answers)


def compile(build):
    """
    This function runs the compile part of the WRF build process.
    :param build: The build string to be passed to the ./compile script.
    :return: The return code of the compile process.
    """
    command = "./compile"
    arguments = [build]

    return run_command(command, arguments, {})

def retrieve_commit(path) -> str:
    """
    Retrieve commit ID from current repository

    Returns:
        str: commit ID string
    """
    cwd = osp.abspath(".")
    os.chdir(path)
    result = run_command("git", ["log"], {})
    commit_id = result['output'].split('\n')[0].split(' ')[-1]
    os.chdir(cwd)
    return commit_id

def build_wrf(
    commit, config_optim="", config_option="1", nesting="1", build="em_fire", clone_dir="", **kwargs
):
    """
    This function orchestrates the WRF build process by first running configuration and then compile.
    :param commit: The branch or commit to checkout before building the code.
    :param config_optim: The configuration options to be passed to the ./configure script.
    :param config_option: The option to be selected when the configure script prompts for selection.
    :param build: The build string to be passed to the ./compile script.
    :param clone_dir: directory to the clone.
    :return: None.
    """

    logging.info("Building in " + clone_dir)
    os.chdir(clone_dir)
    
    # checking out commit
    checkout(commit)

    configure_return = configure(config_optim=config_optim, config_option=config_option, nesting=nesting)
    # Check if the configure.wrf file exists after running configure
    if configure_return["code"] != 0 or not os.path.exists("configure.wrf"):
        logging.error("Error in configuration. Exiting...")
        return

    if build is None:
        logging.error("Build not requested. Exiting...")
        return 1

    compile_return = compile(build)

    if compile_return["code"] != 0:
        logging.error("Error in compile. Exiting...")
        return 1

    compile_out = compile_return["output"]
    if "Executables successfully built" in compile_out:
        logging.info("Build was successful.")
        return
    else:
        logging.error("Build was not successful.")
        return 1


def copy_test(test_path, run_path, namelist_input_params={}, namelist_fire_params={}, input_files=[]):
    """
    This function creates run test folder from original test case.
    :param test_path: path to already existing test case.
    :param run_path: path to new run test case.
    :param namelist_input_params: parameters to be changed in namelist input.
    :param namelist_fire_params: parameters to be changed in namelist fire.
    :param input_files: files to be added to the run test folder.
    :return: None.
    """
    if osp.exists(run_path):
        shutil.rmtree(run_path)
    try:
        shutil.copytree(test_path, run_path)
    except:
        logging.warning('some error while running copytree, normally caused by dangling symlinks')
    if len(namelist_input_params):
        nml_path = osp.join(run_path, "namelist.input")
        logging.debug(f"adding options to namelist input {nml_path}")
        nml_info = f90nml.read(nml_path)
        for s, d in namelist_input_params.items():
            for k, v in d.items():
                nml_info[s][k] = v
        f90nml.write(nml_info, nml_path, force=True)
    if len(namelist_fire_params):
        nml_path = osp.join(run_path, "namelist.fire")
        logging.debug(f"adding options to namelist fire {nml_path}")
        nml_info = f90nml.read(nml_path)
        for s, d in namelist_fire_params.items():
            for k, v in d.items():
                nml_info[s][k] = v
        f90nml.write(nml_info, nml_path, force=True)
    if len(input_files):
        logging.debug("adding additional files")
        for k, v in input_files:
            fpath = osp.join(run_path, k)
            if osp.exists(fpath):
                os.remove(fpath)
            shutil.copyfile(v, fpath)


def run_local(clone_dir, n_proc="1", dmpar=True, **kwargs):
    logging.error("option not supported")


def run_wrf_sub(clone_dir, n_proc="1", wall_time_hrs="2", **kwargs):
    """
    This function runs WRF case.
    :param clone_dir: The configuration options to be passed to the ./configure script.
    :param wall_time_hrs: Clock time hours to run in the cluster.
    :param n_proc: Number of processors to run in the cluster.
    :return: None.
    """
    sub_tmpl_path = kwargs.get("sub_tmpl_path")
    case_path = kwargs.get("case_path", "")
    test_path = kwargs.get("test_path")
    test_name = kwargs.get("test_name")
    namelist_input_params = kwargs.get("namelist_input_params", {})
    namelist_fire_params = kwargs.get("namelist_fire_params", {})
    input_files = kwargs.get("input_files", {})
    real = kwargs.get("real", False)
    # Copy test case
    if osp.isabs(test_path):
        orig_path = test_path
    else:
        orig_path = osp.join(clone_dir, test_path)
    logging.info(f"cloning test case {case_path} from {orig_path}")
    copy_test(
        orig_path,
        case_path,
        namelist_input_params=namelist_input_params,
        namelist_fire_params=namelist_fire_params,
        input_files=input_files
    )
    # Link executables
    if real:
        logging.info("linking executables real.exe and wrf.exe")
        force_symlink(osp.join(clone_dir, "main", "real.exe"), osp.join(case_path, "real.exe"))
    else:
        logging.info("linking executables ideal.exe and wrf.exe")
        force_symlink(osp.join(clone_dir, "main", "ideal.exe"), osp.join(case_path, "ideal.exe"))
    force_symlink(osp.join(clone_dir, "main", "wrf.exe"), osp.join(case_path, "wrf.exe"))
    # Create sub file from template
    logging.info("create sub file and run sbatch job")
    script_tmpl = open(sub_tmpl_path).read()
    args = {"test_case": test_name, "wall_time_hrs": int(wall_time_hrs), "np": int(n_proc)}
    with open(osp.join(case_path, osp.basename(sub_tmpl_path)), "w") as f:
        f.write(script_tmpl % args)
    os.chdir(case_path)
    # Run job
    run_return = run_command("sbatch", [osp.basename(sub_tmpl_path)], {})
    if run_return["code"] != 0:
        logging.error("Error in submiting. Exiting...")
        return {}
    job_id = run_return["output"].split('\n')[0].split(' ')[-1]
    return job_id

# __main__ entry point for testing
if __name__ == "__main__":
    conf = {
        "git_url": "https://github.com/openwfm/WRF-SFIRE",
        "clone_dir": "wrf-sfire-local",
        "run_path": ".",
        "commit": "develop-61",
        "config_optim": "-d",
        "config_option": 34,
        "nesting": 1,
        "build": "em_fire",
        "sub_tmpl_path": "/tmp/aws_mpi.sub",
        "test_name": "hill_rothermel",
        "test_path": "test/em_fire/hill",
        "wall_time_hrs": 2,
        "n_proc": 32,
    }
    conf["clone_dir"] = osp.abspath(osp.join(conf["run_path"], "build", conf["clone_dir"]))

    clone(**conf)
    build_wrf(**conf)
    run_wrf_sub(**conf)
