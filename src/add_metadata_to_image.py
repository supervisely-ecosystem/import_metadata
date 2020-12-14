import os
from supervisely_lib.io.json import load_json_file
import supervisely_lib as sly
from supervisely_lib.api.module_api import ApiField

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
INPUT_FOLDER = os.environ.get("modal.state.slyFolder")

MERGE = True
REPLACE = False


def update_meta(api, id, meta):
    if type(meta) is not dict:
        raise TypeError('Meta must be dict, not {}'.format(type(meta)))
    response = api.post('images.editInfo', {ApiField.ID: id, ApiField.META: meta})
    return response.json()


def add_meta_to_imgs(api, path_to_files, dataset_id):
    images_metas = [json_name[:-5] for json_name in os.listdir(path_to_files)]
    images = api.image.get_list(dataset_id)
    image_names = [image_info.name for image_info in images]
    matches = list(set(images_metas) & set(image_names))
    sly.logger.warn('Find {} files with new meta data, {} matches in dataset'.format(len(images_metas), len(matches)))

    for batch in sly.batched(images):
        for image_info in batch:
            if image_info.name not in images_metas:
                sly.logger.warn('No image with name {} in directory {}'.format(image_info.name, path_to_files))
                continue

            meta = load_json_file(os.path.join(path_to_files, image_info.name + '.json'))
            if MERGE == True:
                meta = {**image_info.meta, **meta}

            update_meta(api, image_info.id, meta)


@my_app.callback("add_metadata_to_image")
@sly.timeit
def add_metadata_to_image(api: sly.Api, task_id, context, state, app_logger):
    storage_dir = my_app.data_dir
    datasets_in_dir = [subdir for subdir in os.listdir(INPUT_FOLDER) if os.path.isdir(os.path.join(INPUT_FOLDER, subdir))]
    datasets = api.dataset.get_list(PROJECT_ID)
    for dataset in datasets:
        progress = sly.Progress('Adding meta to images in dataset {}'.format(dataset.name), len(datasets), app_logger)
        if dataset.name not in datasets_in_dir:
            sly.logger.warn('No dataset with name {} in input directory'.format(dataset.name))
            continue
        path_to_files = os.path.join(INPUT_FOLDER, dataset.name)
        add_meta_to_imgs(api, path_to_files, dataset.id)

    progress.iter_done_report()
    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
        "PROJECT_ID": PROJECT_ID,
        "INPUT_FOLDER": INPUT_FOLDER
    })

    # Run application service
    my_app.run(initial_events=[{"command": "add_metadata_to_image"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)