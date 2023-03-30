import sys
import os
import shutil
import re
import tempfile
import subprocess

def main(filename, output_folder):
    with open(filename, 'r') as file:
        content = file.read()
    split_passes = content.split('\n\n')
    passes = []
    for maybe_pass in split_passes:
        maybe_pass = maybe_pass.strip(' \n\t')
        if maybe_pass:
            passes.append(maybe_pass)
    
    pass_names = []
    for apass in passes:
        first_line = apass.split('\n', maxsplit=1)[0]
        match = re.match('.+\((.+)\)', first_line)
        if match:
            pass_names.append(match.group(1))
        else:
            print(f'Warning: could not extract pass name from:\n"{first_line}"')

    defult_tmp_dir = tempfile._get_default_tempdir()
    tmp1  = defult_tmp_dir + '/' + next(tempfile._get_candidate_names())
    tmp2  = defult_tmp_dir + '/' + next(tempfile._get_candidate_names())

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    for n in range(1, len(passes)):
        before = passes[n - 1]
        after = passes[n]
        with open(tmp1, 'w+') as file:
            file.write(before)
        with open(tmp2, 'w+') as file:
            file.write(after)
        output = subprocess.run(['git', 'diff', '--unified=1000', '--minimal', tmp1, tmp2], capture_output = True)
        # Split and reconstruct the first 4 lines to more appropriately name the diff'ed files.
        _, index_line, _, _, diff = output.stdout.split(b'\n', maxsplit=4)
        first_line = bytes(f'diff --git {pass_names[n-1]} {pass_names[n]}\n', encoding='utf8')
        third_fourth_line = bytes(f'\n--- a/{pass_names[n-1]}\n+++ b/{pass_names[n]}\n', encoding='utf8')
        diff = first_line + index_line + third_fourth_line + diff.split(b'\n', maxsplit=1)[1]
        output_name = f'{n:04}-{pass_names[n]}.diff'
        output_path = os.path.join(output_folder, output_name)
        with open(output_path, 'wb+') as file:
            file.write(diff)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("""Usage: diff_passes mlir_pass_dump output_folder
    Note: the contents of folder output_folder will be erased.
        """)
    else:
        main(filename=sys.argv[1], output_folder=sys.argv[2])

