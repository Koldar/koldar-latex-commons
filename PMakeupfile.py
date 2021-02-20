require_pmakeup_version("1.14.14")


read_variables_from_properties("variables.properties")

ensure_has_variable("LATEX_COMPILER")
ensure_has_variable("BUILD_DIRECTORY")
ensure_has_variable("INS_FILE")
ensure_has_variable("DTX_FILE")

echo(f"computing sty file from ins \"{variables.INS_FILE}\" (type {type(variables.INS_FILE)})...", foreground="BLUE")
echo(f"ins file file without extensions \"{get_file_without_extension(variables.INS_FILE)}\" (type {type(get_file_without_extension(variables.INS_FILE))})", foreground="BLUE")
set_variable_in_cache("STY_FILE", get_file_without_extension(variables.INS_FILE) + ".sty", overwrite_if_exists=True)
echo("computed sty file!", foreground="BLUE")

def clean():
    echo("cleaning", foreground="BLUE")
    remove_tree("build", ignore_if_not_exists=True)

    if has_variable_in_cache("STY_FILE"):
        remove_file(path(cwd(), get_basename(get_variable_in_cache("STY_FILE"))))
    echo("done cleaning", foreground="GREEN")



def build():
    sty_file = get_basename(get_variable_in_cache("STY_FILE"))

    remove_file(path(variables.BUILD_DIRECTORY, sty_file), ignore_if_not_exists=True)
    echo(f"building sty. The name will be {sty_file}", foreground="BLUE")
    execute_stdout_on_screen(f"""{variables.LATEX_COMPILER} --aux-directory={variables.BUILD_DIRECTORY} --c-style-errors --halt-on-error --include-directory=. --output-directory={variables.BUILD_DIRECTORY} --shell-escape --interaction=batchmode "{variables.INS_FILE}" """, check_exit_code=True)
    #echo(f"copying .sty file {sty_file} into cwd")
    #copy_file(src=path(variables.BUILD_DIRECTORY, sty_file), dst=sty_file)

def build_doc():
    echo("building dtx. Since there may be references  (e.g. citations or table of contents), we need to compile dtx 2 times", foreground="BLUE")
    execute_stdout_on_screen(f"""{variables.LATEX_COMPILER} --aux-directory={variables.BUILD_DIRECTORY} --c-style-errors --halt-on-error --include-directory=. --output-directory={variables.BUILD_DIRECTORY} --shell-escape --interaction=batchmode "{variables.DTX_FILE}" """, check_exit_code=True)
    execute_stdout_on_screen(f"""{variables.LATEX_COMPILER} --aux-directory={variables.BUILD_DIRECTORY} --c-style-errors --halt-on-error --include-directory=. --output-directory={variables.BUILD_DIRECTORY} --shell-escape --interaction=batchmode "{variables.DTX_FILE}" """, check_exit_code=True)

def update_version():
    ensure_has_variable("NEW_VERSION")

    # \ProvidesPackage{koldar-latex-commons.dtx}[2021/01/12 v1.0.0 Set of utilities I find useful]
    replace_regex_in_file(
        name=variables.DTX_FILE, 
        regex=r"\\ProvidesPackage\{" + variables.DTX_FILE + r"\}" + r"\[(?P<date>\d{4}/\d{2}\\d{2})\s+v(?P<version>\d+\.\d+\.\d+)\s+(?P<description>.+)\]", 
        replacement=r"\\ProvidesPackage{" + variables.DTX_FILE + r"}" + r"[(?P=date) v" + variables.NEW_VERSION + r" (?P=description)]",
        count=1,
    )

def upload():
    echo("uploading to CTAN")


declare_target(target_name="clean", f=clean, requires=None, description="Clean build files")
declare_target(target_name="update-version", f=update_version, requires=None, description="Update the version of the file. Use it before building the document. Requires the user to pass NEW_VERSION variable (e.g., 1.1.2)")
declare_target(target_name="build", f=build, requires=None, description="Build the latex project. Requires latex compiler. Sty is put in the build folder")
declare_target(target_name="doc", f=build_doc, requires=["build"], description="Build the latex pdf documentation. Requires latex compiler. Doc is put in the build folder")
declare_target(target_name="upload", f=upload, requires=["update-version", "build", "doc"], description="Upload the package to CTAN")

process_targets()