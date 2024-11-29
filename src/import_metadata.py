import os
import tarfile

import supervisely_lib as sly
from supervisely_lib.io.json import load_json_file

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
INPUT_PATH = os.environ.get("modal.state.inputPath")
RESOLVE = os.environ["modal.state.resolve"]


def add_metadata_to_images(api, path_to_files, dataset_id, app_logger):
    path_to_images = [sly.fs.get_file_name(json_name) for json_name in os.listdir(path_to_files)]
    images = api.image.get_list(dataset_id)
    image_names = [image_info.name for image_info in images]
    matches = list(set(path_to_images) & set(image_names))
    if len(path_to_images) != len(matches):
        app_logger.warn('{} metadata files were given, {} matches image names in dataset'.format(len(path_to_images), len(matches)))

    progress = sly.Progress('Uploading metadata to images', len(images),
                            app_logger)
    for batch in sly.batched(images):
        for image_info in batch:
            if image_info.name not in path_to_images:
                app_logger.warn('Metadata file for image {} was not found in directory {}'.format(image_info.name, path_to_files))
                continue

            meta = load_json_file(os.path.join(path_to_files, image_info.name + '.json'))
            if RESOLVE == "merge":
                meta_copy = meta.copy()
                for key in meta.keys():
                    if key in image_info.meta:
                        meta_copy[key + "-original"] = image_info.meta[key]

                meta = {**image_info.meta, **meta_copy}

            api.image.update_meta(image_info.id, meta)
        progress.iters_done_report(len(batch))


@my_app.callback("import_metadata")
@sly.timeit
def import_metadata(api: sly.Api, task_id, context, state, app_logger):
    storage_dir = my_app.data_dir
    if INPUT_PATH is None or INPUT_PATH.strip() == "":
        raise Exception("Please specify input path in modal window")
    if not INPUT_PATH.endswith('.tar'):
        archive_path = os.path.join(storage_dir, INPUT_PATH.strip('/') + ".tar")
    else:
        archive_path = os.path.join(storage_dir, INPUT_PATH.lstrip('/'))

    try:
        api.file.download(TEAM_ID, INPUT_PATH, archive_path)
    except Exception as e:
        raise Exception("Can not download input data from Team files") from e
    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as archive:
             extract_dir = os.path.join(storage_dir, INPUT_PATH.strip('/'))
             extract_dir = os.path.abspath(os.path.join(os.path.dirname(extract_dir), '.'))
             def is_within_directory(directory, target):
                 
                 abs_directory = os.path.abspath(directory)
                 abs_target = os.path.abspath(target)
             
                 prefix = os.path.commonprefix([abs_directory, abs_target])
                 
                 return prefix == abs_directory
             
             def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
             
                 for member in tar.getmembers():
                     member_path = os.path.join(path, member.name)
                     if not is_within_directory(path, member_path):
                         raise Exception("Attempted Path Traversal in Tar File")
             
                 tar.extractall(path, members, numeric_owner=numeric_owner) 
                 
             
             safe_extract(archive, extract_dir)
    else:
        raise Exception(f"Archive {INPUT_PATH} is not a .tar file")

    input_dir = extract_dir
    if len(sly.fs.get_subdirs(input_dir)) != 1:
        raise Exception(f"1 Project Directory required. You have {len(sly.fs.get_subdirs(input_dir))}")

    scan_dir = sly.fs.get_subdirs(input_dir)[0]
    input_dir = os.path.join(extract_dir, scan_dir)
    datasets_in_dir = [subdir for subdir in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, subdir))]
    datasets = api.dataset.get_list(PROJECT_ID)
    for dataset in datasets:
        if dataset.name not in datasets_in_dir:
            sly.logger.warn('No dataset with name {} in input directory'.format(dataset.name))
            continue
        path_to_files = os.path.join(input_dir, dataset.name)
        add_metadata_to_images(api, path_to_files, dataset.id, app_logger)

    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
        "PROJECT_ID": PROJECT_ID
    })

    # Run application service
    my_app.run(initial_events=[{"command": "import_metadata"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main, log_for_agent=False)
