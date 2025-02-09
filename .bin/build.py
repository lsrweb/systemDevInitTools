import os
import subprocess

try:
    import PyInstaller.__main__
except ImportError:
    print("PyInstaller is not installed. Please install it using 'pip install pyinstaller'")
    exit()

try:
    from PIL import Image
except ImportError:
    print("Pillow (PIL) is not installed. Please install it using 'pip install Pillow'")
    exit()

# Main application file
main_file = 'MainApplication.py'

# Application icon
icon_file = 'public/app.ico'

# Metadata
app_name = "EnvConfigTool"
app_version = "1.0.0"
app_author = "Your Name"
app_description = "A tool for configuring environment variables."
company_name = "Your Company"
copyright_notice = f"Copyright (c) {company_name} {app_version}"

# Build the executable using PyInstaller
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))

    args = [
        main_file,
        '--onefile',
        '--noconsole',  # Remove this if you want a console window
        '--name', app_name,
        '--icon', icon_file,
    ]

    # Create version file
    version_file_content = f"""# UTF-8 encoding
#
# For more details about fixed file info 'ffi' see:
# https://msdn.microsoft.com/en-us/library/windows/desktop/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 0, 0, 0)
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    OS=0x40004,
    # The general type of file.
    fileType=0x1,
    # The function performed by this file.
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904b0',
        [StringStruct(u'CompanyName', u'{company_name}'),
        StringStruct(u'FileDescription', u'{app_description}'),
        StringStruct(u'FileVersion', u'{app_version}'),
        StringStruct(u'InternalName', u'{app_name}'),
        StringStruct(u'LegalCopyright', u'{copyright_notice}'),
        StringStruct(u'OriginalFilename', u'{app_name}.exe'),
        StringStruct(u'ProductName', u'{app_name}'),
        StringStruct(u'ProductVersion', u'{app_version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    version_file_content = version_file_content.format(
        company_name=company_name,
        app_description=app_description,
        app_version=app_version,
        app_name=app_name,
        copyright_notice=copyright_notice
    )

    with open("version.rc", "w", encoding="utf-8") as f:
        f.write(version_file_content)

    args.append('--version-file=version.rc')

    PyInstaller.__main__.run(args)

    # Clean up version file
    os.remove("version.rc")