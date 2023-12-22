import argparse
import os
import shutil
import subprocess
import re


def clean(repo_path, deleted_remote=False, local_only=False, dry_run=True):
    os.chdir(repo_path)

    # Call external command 'git branch -vv' and get the command output
    cmd = 'git branch -vv'
    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    print(output)
    # Split the output by line
    lines = output.split('\n')
    # Loop through each line
    branch_list = []
    for line in lines:
        if line.strip() == '':
            continue
        branch_pattern = re.compile(r'[*+\s]\s'
                                    r'(?P<local_branch>\S+?)\s+'
                                    r'(?P<commit>\S+?)\s'
                                    r'(?:\((?P<local_path>\S+)\)\s)?'
                                    r'(?:\[(?P<remote_branch>\S+)(?::\s(?P<remote_status>\S+?))?])?.+')
        branch_match = re.match(branch_pattern, line)
        if not branch_match:
            raise Exception('Failed to parse branch: {}'.format(line))
        # branch_list.append(GitBranch(branch_match.group('local_branch'),
        #                              branch_match.group('commit'),
        #                              branch_match.group('local_path'),
        #                              branch_match.group('remote_branch'),
        #                              branch_match.group('remote_status') == 'gone'))
        need_delete = False
        if deleted_remote and branch_match.group('remote_status') == 'gone':
            need_delete = True
        if not need_delete and local_only and branch_match.group('remote_branch') is None:
            need_delete = True
        if need_delete:
            branch_list.append(branch_match.group('local_branch'))
            local_path = branch_match.group('local_path')
            if local_path is not None:
                if dry_run:
                    print('Would delete local path: {}'.format(local_path))
                else:
                    print('Deleting......: {}'.format(local_path))
                    shutil.rmtree(local_path)
    if dry_run:
        print('Would delete branches: {}'.format(' '.join(branch_list)))
    else:
        print('Deleting......: {}'.format(' '.join(branch_list)))
        subprocess.check_output('git worktree prune', shell=True)
        subprocess.check_output('git branch -D {}'.format(' '.join(branch_list)), shell=True)


if __name__ == '__main__':
    # use ArgumentParser to define an argument -l or --include-local to include local dependencies
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-p', '--repo-path', action='store', help='the directory where the git repo is located')
    parser.add_argument('-g', '--gone-remote', action='store_true',
                        help='clean branches deleted on remote', default=False)
    parser.add_argument('-l', '--local-only', action='store_true',
                        help='clean branches only exists locally', default=False)
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='clean branches only exists locally', default=False)
    args = parser.parse_args()
    if args.repo_path is None:
        print('Repo path not provided.')
        exit(1)
    clean(args.repo_path, args.gone_remote, args.local_only, args.dry_run)
