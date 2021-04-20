import os
import tarfile

import supervisely_lib as sly
from supervisely_lib.io.json import load_json_file

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
INPUT_PATH = os.environ["modal.state.inputPath"]
RESOLVE = os.environ["modal.state.resolve"]


def add_meta_to_images(api, path_to_files, dataset_id, app_logger):
    path_to_images = [sly.fs.get_file_name(json_name) for json_name in os.listdir(path_to_files)]
    images = api.image.get_list(dataset_id)
    image_names = [image_info.name for image_info in images]
    matches = list(set(path_to_images) & set(image_names))
    if not len(path_to_images) != len(matches):
        app_logger.info('Find {} metadata files, {} matches in dataset'.format(len(path_to_images), len(matches)))

    progress = sly.Progress('Uploading metadata to image', len(images),
                            app_logger)
    for batch in sly.batched(images):
        for image_info in batch:
            if image_info.name not in path_to_images:
                app_logger.warn('No image with name {} in directory {}'.format(image_info.name, path_to_files))
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


@my_app.callback("import_images_metadata")
@sly.timeit
def import_images_metadata(api: sly.Api, task_id, context, state, app_logger):
    storage_dir = my_app.data_dir
    if not INPUT_PATH.endswith('.tar'):
        archive_path = os.path.join(storage_dir, INPUT_PATH.strip('/') + ".tar")
    else:
        archive_path = os.path.join(storage_dir, INPUT_PATH.lstrip('/'))

    api.file.download(TEAM_ID, INPUT_PATH, archive_path)
    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as archive:
             extract_dir = os.path.join(storage_dir, INPUT_PATH.strip('/'))
             extract_dir = os.path.abspath(os.path.join(os.path.dirname(extract_dir), '.'))
             archive.extractall(extract_dir)
    else:
        raise ValueError("No such file {}".format(INPUT_PATH))

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
        add_meta_to_images(api, path_to_files, dataset.id, app_logger)

    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
        "PROJECT_ID": PROJECT_ID
    })

    # Run application service
    my_app.run(initial_events=[{"command": "import_images_metadata"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)