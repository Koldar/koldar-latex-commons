require_pmakeup_version("1.14.14")

import semver

read_variables_from_properties("variables.properties")

ensure_has_variable("LATEX_COMPILER")
ensure_has_variable("BUILD_DIRECTORY")
ensure_has_variable("PKG_NAME")

global ins_basename
global sty_basename
global dtx_basename
global pdf_basename

ins_basename = variables.PKG_NAME + ".ins"
sty_basename = variables.PKG_NAME + ".sty"
dtx_basename = variables.PKG_NAME + ".dtx"
pdf_basename = variables.PKG_NAME + ".pdf"

def clean():
    echo("cleaning", foreground="BLUE")
    remove_tree("build", ignore_if_not_exists=True)

    remove_file(path(cwd(), sty_basename))
    echo("done cleaning", foreground="GREEN")



def build():

    remove_file(path(variables.BUILD_DIRECTORY, sty_basename), ignore_if_not_exists=True)
    echo(f"building sty. The name will be {sty_basename}", foreground="BLUE")
    execute_stdout_on_screen(f"""{variables.LATEX_COMPILER} --aux-directory={variables.BUILD_DIRECTORY} --c-style-errors --halt-on-error --include-directory=. --output-directory={variables.BUILD_DIRECTORY} --shell-escape --interaction=batchmode "{ins_basename}" """, check_exit_code=True)

def build_doc():
    echo("building dtx. Since there may be references  (e.g. citations or table of contents), we need to compile dtx 2 times", foreground="BLUE")
    execute_stdout_on_screen(f"""{variables.LATEX_COMPILER} --aux-directory={variables.BUILD_DIRECTORY} --c-style-errors --halt-on-error --include-directory=. --output-directory={variables.BUILD_DIRECTORY} --shell-escape --interaction=batchmode "{dtx_basename}" """, check_exit_code=True)
    execute_stdout_on_screen(f"""{variables.LATEX_COMPILER} --aux-directory={variables.BUILD_DIRECTORY} --c-style-errors --halt-on-error --include-directory=. --output-directory={variables.BUILD_DIRECTORY} --shell-escape --interaction=batchmode "{dtx_basename}" """, check_exit_code=True)

def update_version():
    ensure_has_variable("NEW_VERSION")

    # \ProvidesPackage{koldar-latex-commons.dtx}[2021/01/12 v1.0.0 Set of utilities I find useful]
    replace_regex_in_file(
        name=dtx_basename, 
        regex=r"\\ProvidesPackage\{" + variables.PKG_NAME + r"\}" + r"\[(?P<date>\d{4}/\d{2}/\d{2})\s+v(?P<version>\d+\.\d+\.\d+)\s+(?P<description>.*)\]", 
        replacement=r"\\ProvidesPackage{" + variables.PKG_NAME + r"}" + r"[\g<date> v" + variables.NEW_VERSION + " \g<description>]",
        count=1,
    )
    echo(f"Updated version in {dtx_basename}", foreground="GREEN")

def upload():
    echo("uploading to CTAN")

    m: re.Match = find_regex_match_in_file(
        r"\\ProvidesPackage\{" + variables.PKG_NAME + r"\}" + r"\[(?P<date>\d{4}/\d{2}/\d{2})\s+v(?P<version>\d+\.\d+\.\d+)\s+(?P<description>.*)\]", 
        dtx_basename
    )
    if m is None:
        raise ValueError(f"cannot fetch data from dtx file {dtx_basename}!")

    version = m.group("version")
    description = m.group("description")
    if semver.VersionInfo.parse(version).major < 1:
        raise ValueError(f"The script cannot upload pckages with major version less than 1! If this is your irst upload, use 1.0.0!")
    update = version != "1.0.0" # the first version is the 1.0.0. After that 

    # move the pdf of the documentation in the cwd: in this way it is picked up by ls_only_files
    copy_file(
        src=path(variables.BUILD_DIRECTORY, pdf_basename), dst=path(get_pmakeupfile_dirpath())
    )

    result = []
    for file in ls_only_files(get_pmakeupfile_dirpath(), generate_absolute_path=True):
        echo(f"Extension of file {file} is {get_extension(file)}", foreground="BLUE")
        if get_extension(file) in ("tex", "dtx", "ins", "md", "pdf"):
            result.append(file)
    echo(f"Putting these files in the zip: {', '.join(result)}", foreground="BLUE")
        
    zip_name = variables.PKG_NAME + ".zip"

    file_to_upload = zip_files(
        files=result, 
        zip_name=zip_name,
        zip_format="zip",
        create_folder_in_zip_file=True,
        folder_name_in_zip_file=variables.PKG_NAME
    )

    execute_stdout_on_screen(f"""curl --verbose -X POST --header "Content-Type: application/x-www-form-urlencoded" --form "author={variables.CTAN_UPLOAD_AUTHOR}" --form "description={description}" --form "email={variables.CTAN_UPLOAD_EMAIL}" --form "license={variables.CTAN_UPLOAD_LICENSE}" --form "pkg={variables.PKG_NAME}" --form "summary={description}" --form "update={update}" --form "uploader={variables.CTAN_UPLOAD_AUTHOR}" --form "version={version}" --form "home={variables.CTAN_UPLOAD_PACKAGE_HOME}" --form "repo={variables.CTAN_UPLOAD_PACKAGE_HOME}" --form "ctanPath={variables.CTAN_UPLOAD_PACKAGE_CTANPATH}" --form "announcement={description}" --form 'file=@{file_to_upload}' 'https://www.ctan.org/submit/validate' """)


declare_target(target_name="clean", f=clean, requires=None, description="Clean build files")
declare_target(target_name="update-version", f=update_version, requires=None, description="Update the version of the file. Use it before building the document. Requires the user to pass NEW_VERSION variable (e.g., 1.1.2)")
declare_target(target_name="build", f=build, requires=None, description="Build the latex project. Requires latex compiler. Sty is put in the build folder")
declare_target(target_name="doc", f=build_doc, requires=["build"], description="Build the latex pdf documentation. Requires latex compiler. Doc is put in the build folder")
declare_target(target_name="upload", f=upload, requires=["update-version", "build", "doc"], description="Upload the package to CTAN")

process_targets()