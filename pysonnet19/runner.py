import sys
import os
import subprocess


def run_macro_command_file(macro_command_file_path, new_sonnet_file_path):
    #Load the sonnet directory
    if os.environ.get("SONNET_DIR") is not None:
        sonnet_path = os.environ.get("SONNET_DIR") + "/bin/"
        run_macro =  sonnet_path + "runmacro"
    else:
        raise EnvironmentalError(f"Sonnet path is not correctly configured.")
    if sys.platform.startswith('win'):
        run_macro += ".exe"

    print("Running macro command file: " + macro_command_file_path)

    # Add "-v" to macro_command_line if you want the macro language to generate output and uncomment stdout print statement
    macro_command_line = [run_macro, macro_command_file_path]
    result = subprocess.run(macro_command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='UTF-8')

    print("************************      CREATED " + new_sonnet_file_path +
          "      ************************")
    print("Return code:", result.returncode)
    # Uncomment if "-v" argument is present
    # print("Macro Output:", result.stdout)
    if result.stderr != "":
        print("Error:", result.stderr)


    #Work around for now, because the analyze() function has a bug
    subprocess.call(sonnet_path + "sonnet -analyze -Run -CloseWhenDone {}".format(new_sonnet_file_path), shell = True)
