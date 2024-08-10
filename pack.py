# User settings
modpack_name = "Test"
version = "0.0.1-beta"
authors = "Oganesson897"

package_overrides = [
    'addons',
    'config',
    'CustomSkinLoader',
    'fontfiles',
    'journeymap',
    'oresources',
    'resources',
    'resourcepacks',
    'shaderpacks',
    'scripts',
    'groovy',
    'options.txt',
    'optionsof.txt'
]

# Script ↓
import os
import toml
import json
import shutil
import zipfile
import requests

metadata_dir = os.path.join('.minecraft', 'mods', '.index')

names = []
no_meta_mods = []
file_ids = []
prj_ids = []

# Prism metadata loader
for filename in os.listdir(metadata_dir):
    if filename.endswith('pw.toml'):
        file_path = os.path.join(metadata_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = toml.load(file)
                names.append(data['filename'])
                file_ids.append(data['update']['curseforge']['file-id'])
                prj_ids.append(data['update']['curseforge']['project-id'])
                
        except Exception as e:
            print(f"Error for reading {filename}: {e}")

# Modlist
api_key = "$2a$10$ZS5BrrbTqsJdNOKmlZCozuCo49ULIeuq7qvgwQP3fBeJ5SJWHGck2"
markdown = []
for projectId in prj_ids:
    headers = {
        'Accept': 'application/json',
        'x-api-key': api_key
    }
    response = requests.get(f'https://api.curseforge.com/v1/mods/{projectId}', headers = headers).json()
    
    mod_name = response['data']['name']
    links = response['data']['links']['websiteUrl']
    author = response['data']['authors'][0]['name']
    logo_link = response['data']['logo']['thumbnailUrl']

    markdown.append(f'[![Logo]({logo_link})]({links}) **{mod_name} (by {author})**')

with open('modlist.md', 'w', encoding='utf-8') as file:
    file.writelines(markdown)


# Manifest
data = {}

with open('manifest.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

    data['name'] = modpack_name
    data['version'] = version
    data['author'] = authors

    files = []

    for fileId, projectId in zip(file_ids, prj_ids):
        d = {'projectID': projectId, 'fileID': fileId, 'required': True}
        files.append(d)

    data['files'] = files

with open('manifest.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4, ensure_ascii=True)

# Unmetated mod
mod_dir = os.path.join('.minecraft', 'mods')
for modname in os.listdir(mod_dir):
    if modname.endswith('.jar'):
        if not modname in names:
            no_meta_mods.append(modname)

def zip_directory(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, relative_path)

# Package Curse
curse_dir = 'curse/overrides'
os.makedirs('curse', exist_ok=True)

if os.path.isfile('README.md'): shutil.copy('README.md', 'curse/README.md')
if os.path.isfile('LICENSE'): shutil.copy('LICENSE', 'curse/LICENSE')
if os.path.isfile('manifest.json'): shutil.copy('manifest.json', 'curse/manifest.json')
if os.path.isfile('modlist.md'): shutil.copy('modlist.md', 'curse/modlist.md')

for filename in os.listdir('.minecraft'):
    if filename in package_overrides:
        if os.path.isdir(os.path.join('.minecraft', filename)): shutil.copytree(os.path.join('.minecraft', filename), os.path.join(curse_dir, filename))
        if os.path.isfile(os.path.join('.minecraft', filename)): shutil.copy(os.path.join('.minecraft', filename), os.path.join(curse_dir, filename))

for no_meta_mod in no_meta_mods:
    os.makedirs(os.path.join(curse_dir, 'mods'), exist_ok=True)
    shutil.copy(os.path.join('.minecraft/mods', no_meta_mod), os.path.join(curse_dir, 'mods', no_meta_mod))

os.makedirs('export', exist_ok=True)
zip_directory('curse', 'export/' + f'{modpack_name}-{version}-CURSE.zip')
shutil.rmtree('curse')

# Package MMC
mmc_dir = 'mmc/.minecraft'
os.makedirs('mmc', exist_ok=True)

if os.path.isdir('libraries'): shutil.copytree('libraries', 'mmc/libraries')
if os.path.isdir('patches'): shutil.copytree('patches', 'mmc/patches')

if os.path.isfile('.packignore'): shutil.copy('.packignore', 'mmc/.packignore')
if os.path.isfile('instance.cfg'): shutil.copy('cfg.cfg', 'mmc/instance.cfg')
if os.path.isfile('mmc-pack.json'): shutil.copy('mmc-pack.json', 'mmc/mmc-pack.json')
if os.path.isfile('modlist.md'): shutil.copy('modlist.md', 'mmc/modlist.md')
if os.path.isfile('README.md'): shutil.copy('README.md', 'mmc/README.md')
if os.path.isfile('LICENSE'): shutil.copy('LICENSE', 'mmc/LICENSE')

for filename in os.listdir('.minecraft'):
    if filename in package_overrides:
        if os.path.isdir(os.path.join('.minecraft', filename)): shutil.copytree(os.path.join('.minecraft', filename), os.path.join(mmc_dir, filename))
        if os.path.isfile(os.path.join('.minecraft', filename)): shutil.copy(os.path.join('.minecraft', filename), os.path.join(mmc_dir, filename))
shutil.copytree('.minecraft/mods', 'mmc/.minecraft/mods')

os.makedirs('export', exist_ok=True)
zip_directory('mmc', 'export/' + f'{modpack_name}-{version}-MMC.zip')
shutil.rmtree('mmc')