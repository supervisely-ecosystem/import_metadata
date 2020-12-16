import os
import tarfile

import supervisely_lib as sly
from supervisely_lib.io.json import load_json_file
from supervisely_lib.api.module_api import ApiField

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
INPUT_PATH = os.environ["modal.state.inputPath"]
RESOLVE = os.environ["modal.state.resolve"]


def add_meta_to_imgs(api, path_to_files, dataset_id, app_logger):
    images_metas = [json_name[:-5] for json_name in os.listdir(path_to_files)]
    images = api.image.get_list(dataset_id)
    image_names = [image_info.name for image_info in images]
    matches = list(set(images_metas) & set(image_names))
    sly.logger.warn('Find {} files with new meta data, {} matches in dataset'.format(len(images_metas), len(matches)))

    for batch in sly.batched(images):
        progress = sly.Progress('Uploading metadata to image', len(images),
                                app_logger)
        for image_info in batch:
            if image_info.name not in images_metas:
                sly.logger.warn('No image with name {} in directory {}'.format(image_info.name, path_to_files))
                continue


            meta = load_json_file(os.path.join(path_to_files, image_info.name + '.json'))
            if RESOLVE == "merge":
                meta = {**image_info.meta, **meta}

            api.image.update_meta(image_info.id, meta)
            progress.iter_done_report()


@my_app.callback("add_metadata_to_image")
@sly.timeit
def add_metadata_to_image(api: sly.Api, task_id, context, state, app_logger):
    storage_dir = my_app.data_dir
    if not INPUT_PATH.endswith('.tar'):
        cur_files_path = INPUT_PATH
        archive_path = storage_dir + (cur_files_path.rstrip("/") + ".tar")
    else:
        cur_files_path = INPUT_PATH
        archive_path = storage_dir + cur_files_path

    api.file.download(TEAM_ID, cur_files_path, archive_path)
    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as archive:
             extract_dir = storage_dir + cur_files_path
             extract_dir = os.path.abspath(os.path.join(os.path.dirname(extract_dir), '.'))
             archive.extractall(extract_dir)
    else:
        raise ValueError("No such file {}".format(INPUT_PATH))

    input_dir = extract_dir
    if len(sly.fs.get_subdirs(input_dir)) != 1:
        raise Exception(f"1 Project Directory required. You have {len(sly.fs.get_subdirs(input_dir))}")

    scan_dir = sly.fs.get_subdirs(input_dir)[0]
    input_dir = extract_dir + "/" + scan_dir

    datasets_in_dir = [subdir for subdir in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, subdir))]
    datasets = api.dataset.get_list(PROJECT_ID)
    for dataset in datasets:
        if dataset.name not in datasets_in_dir:
            sly.logger.warn('No dataset with name {} in input directory'.format(dataset.name))
            continue
        path_to_files = os.path.join(input_dir, dataset.name)
        add_meta_to_imgs(api, path_to_files, dataset.id, app_logger)

    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
        "PROJECT_ID": PROJECT_ID
    })

    # Run application service
    my_app.run(initial_events=[{"command": "add_metadata_to_image"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)