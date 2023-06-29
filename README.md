<div align="center" markdown>
<img src="media/poster.png"/>

# Import Metadata


<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>

[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-metadata)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/import-metadata.png)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/import-metadata.png)](https://supervise.ly)

</div>

## Overview

All images in Supervisely have metadata by default. It contains base information about image in dataset such as: time when image was created or modified by user, pixel area, image size, resolution. But there's also an ability to store your own custom metadata for an image.
In this example we store some additional information about image, which helps to match images from one database with another, such as IMDB.

<img src="media/ov.png"/>


## Preparation

Your data folder with `json` files have to contain only directories with names that are exactly matching project dataset names. You can also upload a `.tar` archive with a data folder inside.
Look at the examples for Directory and Archive below:

```text
1) Directory                          2) Archive
.                                     .
├── DataFolder                        ├── Metadata.tar
    |── dataset01                         |── DataFolder
    |    ├── IMG_521.json                     |── dataset01
    |    ├── IMG_522.json                     |    ├── IMG_521.json  
    |    └── . . .                            |    ├── IMG_522.json    
    └── dataset02                             |    └── . . .       
        ├── IMG_4561.json                     └── dataset02     
        ├── IMG_4562.json                         ├── IMG_4561.json  
        └──  . . .                                ├── IMG_4562.json  
                                                  └──  . . .      
```


## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-metadata) if it is not there.

**Step 2**: Open context menu of your project -> `Run App` -> `Import Metadata`

<img src="media/htr2.png"/>


## How to use

**Step 1** Drag and drop you folder or `tar` archive with data to Team Files.

**Step 2** Right click on your data to open context menu and choose `copy path` option. 
**Important notice: copy path of your project folder instead of dataset folder**.

<img src="media/htu2.png"/>

**Step 3** Run application from project context menu and paste path to your data. 

<img src="media/htu3.png"/>
<img src="media/htu3a.png"/>

**Step 4** After running the application, you will be redirected to the tasks page. Once application processing has finished, you can go to your project to see the results.
<img src="media/htu4.png"/>
