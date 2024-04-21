from build import clone, retrieve_commit, build_wrf, run_wrf_sub, ensure_dir
import os.path as osp
import json
import sys
import os
import logging

def regression_test(js):
    test_cases = []
    test_case = {
        "git_url": js.get("git_url", "https://github.com/openwfm/WRF-SFIRE"),
        "commit_ref": js.get("commit_ref", "master"),
        "rebuild_ref": js.get("rebuild_ref", True),
        "commit_dev": js.get("commit_dev", "release"),
        "rebuild_dev": js.get("rebuild_ref", True),
        "run_path": js.get("run_path", "."),
        "build": js.get("build", "em_fire"),
        "sub_tmpl_path": osp.abspath(js.get("sub_tmpl_path", "submit/aws.sub")),
        "wall_time_hrs": js.get("wall_time_hrs", 2),
    }
    run_path = osp.abspath(osp.join(test_case["run_path"], "reg_tests"))
    build_path = osp.abspath(osp.join(test_case["run_path"], "build"))
    rebuilds = [test_case["rebuild_ref"], test_case["rebuild_dev"]]
    commits = [test_case["commit_ref"], test_case["commit_dev"]]
    for commit, rebuild in zip(commits, rebuilds):
        for config_option in js.get("config_options", [34]):
            for config_optim in js.get("config_optims", [""]):
                for nesting in js.get("nestings", [1]):
                    tag_name = "_".join(
                        [
                            x
                            for x in [
                                commit,
                                str(config_option),
                                str(config_optim),
                                str(nesting)
                            ]
                            if len(x)
                        ]
                    )
                    build_dir = osp.join(
                        build_path,
                        "_".join(["wrf-sfire", tag_name])
                    )
                    test_case.update(
                        {
                            "clone_dir": build_dir,
                            "commit": commit,
                            "config_option": config_option,
                            "config_optim": config_optim,
                            "nesting": nesting,
                        }
                    )
                    if rebuild or not osp.exists(test_case["clone_dir"]):
                        clone(**test_case)
                        build_wrf(**test_case)
                    test_case.update({"commit_id": retrieve_commit()})
                    for name, opts in js.get("test_cases", {}).items():
                        path = opts.get("path", "")
                        vars = opts.get("vars", [])
                        for n_proc in opts.get("n_cpu", [1]):
                            for config in opts.get("configs", []):
                                info = config.get("info", "").lower().replace(" ", "_")
                                namelist_input_params = config.get("namelist_input_params", {})
                                namelist_fire_params = config.get("namelist_fire_params", {})
                                input_files = config.get("input_files", {})
                                test_name = "_".join(
                                    [
                                        x
                                        for x in [
                                            name.lower(), 
                                            info, 
                                            str(n_proc),
                                            str(config_option),
                                            str(config_optim),
                                            str(nesting)
                                        ]
                                        if len(x)
                                    ]
                                )
                                case_path = ensure_dir(
                                    osp.join(
                                        run_path, test_name + '_{}'.format(commit)
                                    )
                                )
                                test_case.update(
                                    {
                                        "test_id": test_name,
                                        "test_name": name,
                                        "case_name": info,
                                        "n_cpus": n_proc,
                                        "test_path": path,
                                        "case_path": case_path,
                                        "namelist_input_params": namelist_input_params,
                                        "namelist_fire_params": namelist_fire_params,
                                        "input_files": input_files,
                                        "vars": vars,
                                    }
                                )
                                job_id = run_wrf_sub(**test_case)
                                test_case.update({"job_id": job_id})
                                test_cases.append(test_case.copy())
    return test_cases


# __main__ entry point for testing
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {} reg_test_json".format(sys.argv[0]))
        sys.exit()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    cwd = osp.abspath(".")
    js = json.load(open(sys.argv[1]))
    test_cases = regression_test(js)
    os.chdir(cwd)
    json.dump(test_cases, open("reg_tests.json", "w"), indent=4, separators=(",", ": "))
