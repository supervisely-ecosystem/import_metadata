<div align="center" markdown>
<img src="https://i.imgur.com/kWm6Rkk.png"/>

# Import Project Images Metadata


<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>

[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/https://github.com/supervisely-ecosystem/upload_metadata)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/https://github.com/supervisely-ecosystem/upload_metadata&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/https://github.com/supervisely-ecosystem/upload_metadata&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/https://github.com/supervisely-ecosystem/upload_metadata&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

All images in supervisely have default metadata. It contains base information about image in dataset such as: time when image was created or modified by user, pixel area, image size, resolution. But there's also an ability to store your own custom metadata for image.
In this example we store some additional information about image, which helps to match images from one database with another, such as imdb.

<img src="https://i.imgur.com/jc4i7c9.png"/>


## Preparation

Your `json` data folder have to contain only directories with dataset names. You can also upload a `tar` archive with a project folder inside.
Look at the examples for Directory and Archive below:

<img src="https://i.imgur.com/YDq0013.png"/>


## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/upload_metadata) if it is not there.

**Step 2**: Open context menu of your project -> `Run App` -> `Upload Images Metadata` 

<img src="https://i.imgur.com/dY1ARDk.png"/>


## How to use

**Step 1** Drag and drop you folder or `tar` archive with data to Team Files.

**Step 2** Right click on your data to open context menu and choose `copy path` option. 
**Important notice: copy path of your project folder instead of dataset folder**.

<img src="https://i.imgur.com/4x3hqne.png"/>

**Step 3** Run application from project context menu and paste path to your data. 

<img src="https://i.imgur.com/EvTZzsa.png"/>
<img src="https://i.imgur.com/gZ3Ldqh.png"/>

**Step 4** After running the application, you will be redirected to the tasks page. Once application processing has finished, you can go to your project to see the results.
<img src="https://i.imgur.com/e7yZ3Ez.png"/>
