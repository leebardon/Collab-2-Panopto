# Collab-2-Panopto

Developed at the University of Southampton, Collab-2-Panopto assists in managing the rapid increase in course-related 
online content that proliferated during Covid-19 lockdown. It was inspired by - and builds upon - several Python scripts 
developed by others (see 'Credits'), with the goal of providing a robust, flexible, production-ready application
that can handle the transfer of video content between the two services automatically, and at scale.  

<b>Collab-2-Panopto:</b>
1. Finds all recordings added to Blackboard Collaborate within a time period specified by the user;
2. Finds corresponding course folders on Panopto, and sends notification emails when Panopto folders aren't found;
3. Where course Panopto folders <i>are</i> found:
    * Downloads Collab recordings to the local server
    * Uploads recording/s to corresponding Panopto folder/s;
4. Where uploads are successful:
    * Deletes recording from local server;
    * Deletes recording from Collaborate.

## Quick Start

<b>NOTE 1:</b> This project was built in RHEL 8, with miniconda as the primary package manager. Due to OS-specific 
dependency requirements, it will work best in similar Linux environments. It has not been tested 
in Windows or MacOS. To improve portability, we plan to change the current system
of managing packages and environments. 

<b>NOTE 2:</b> Development is otherwise ongoing. In particular, a recent large-scale refactor has left some unit tests 
in need of reconfiguring (as of 19th July 2021).

## Environment Set-Up 

* Clone the project to the your desired server
* Install Python 3.9
* Obtain the most appropriate version of the [https://docs.conda.io/en/latest/miniconda.html package manager miniconda] for Python 3.9
* Ensure that Python [https://pip.pypa.io/en/stable/installing/ package manager 'Pip'] is installed on the server 

Once the above steps have been completed, navigate to the root directory of the project and run:

`conda env create -f environment.yml`

This will create a virtual environment and download all packages used by the application (and their dependancies) into it. Should any errors occurs during this step, conda will provide instructive error messages that should enable the problem to be solved. Dependancies can also be examined manually by viewing the environment.yml file.

On successful completion of the above, activate the project's environment by running:

`conda activate collaborate-to-panopto`

## API & SSL Config.

Collab-2-Panopto interacts with two external REST API services: namely the Blackboard Collaborate REST API, and the Panopto 
REST API. It also requires configuration details to enable successful sending of alert emails to service owners and maintainers. 
To enable this process, a configuration template <code>ConfigTemplate.py</code> is provided in the <code> /config/</code> folder. Please 
copy this into a new file, fill out the relevant details, and save the file as <code>Config.py</code> within the same directory.

## Config.py

<b> Collaborate Settings </b>

Your university will have its own Collaborate key and secret details. 

<b> Panopto Settings </b>

For development purposes, it's instructive to create a client_id and client_secret_id via the Panopto website:

1. Sign in to Panopto website
2. Click your name in right-upper corner, and click "User Settings"
3. Select "API Clients" tab
4. Click "Create new API Client" button
5. Enter arbitrary Client Name
6. Select User Based Server Application type.
7. Enter <html>http://localhost/ into CORS Origin URL.
8. Enter <html>http://localhost:9127/redirect into Redirect URL.
9. The rest can be blank. Click "Create API Client" button.
10. Note the created Client ID and Client Secret.
  "ppto_server": "your.university.server"
  "ppto_client_id": obtained client_id
  "ppto_client_secret": obtained client_secret
    

## To Run
   
Once the environment has been successfully set-up and activated, and <code>Config.py</code> has been created and updated with the appropriate credentials, the program can be launched.

The <code>runscript.py</code> file is located in the project root directory. Here, we can set the time period over which the automatic pathway searches for recordings added to Collaborate. The period is measured in weeks, and the default period is 1 week. This is adjusted via the argument of the function call set_search_start_date() from the Utilities.py module. 

To launch, run the following from the root directory:

 ```python runscript.py```

This will print <code> -- PRESS ENTER FOR MANUAL RUN -- </code> and launch a countdown timer (default 15 seconds). If you do not press enter during this 15 second period, the automatic pathway will be launched. Otherwise, the manual pathway will be launched. The duration of the countdown timer can be adjusted via the <code>__main__</code> function in <code>runscript.py</code>.

When manual run has been selected, two options are available: <code>Enter number of weeks or 'p' for preview</code>. Entering a number <code>n</code>(can be 0) will start the application and process recordings from <code>n</code> weeks back up until now. Entering <code>p</code> instead of a number will start preview mode, detailed below. Any other input will exit the application.


## Preview Mode

Preview mode allows to launch a "dry run" where the application will simulate what it would do, without actually doing anything. This is useful when looking for information on what launching the application would do if started.

Using this mode will display this information for you: 
   * <b>Courses on Collab</b> : Lists all courses added to Collaborate between search start-date and present 
   * <b> Recordings per course </b> : Lists all recordings found for the courses listed above
   * <b> Corresponding folders on Panopto </b>: Lists all folders found on Panopto that correspond to the courses found on Collaborate. Will also list courses that do not have corresponding Panopto folders
   * <b> Planned uploads </b>: Lists all recordings that can be uploaded, and their destination folder on Panopto



### PID File locking mechanism 

Upon launching the application, a pid file is created in <code>/home/user/tmp/runscript.py.pid</code>. This stops two applications running at the same time, which would cause problems. As long as this file exists, no two instances of this application can run at the same time. If the application encounters an unexpected crash or is killed ungracefully then this pid file will remain in place and stop any further executions. This is useful to realise when something bad has happened and may be worth investigating. This pid file is safe to delete when the problem has been investigated and steps have been taken to repair what the sudden stop might have caused.


## High-Level Overview 

![](/data/Collab-2-Panopto.png)

   
## Authors

- **Lee Bardon** - Software Engineer, Uni. of Southampton - [leebardon](https://github.com/leebardon)
- **Josh Bruylant** - Software Engineer, Uni. of Southampton - [Frazic](https://github.com/Frazic)
   

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

   
   
## Credits 
   
This project was inspired by and adapted from: 
   
PyCollab: https://github.com/zerausolrac/PyCollab - MIT License

OSCELOT: https://github.com/OSCELOT/Collab-Panopto - Blackboard Open Source License
   
BulkExportBBCollaborateRecordings : https://github.com/SimonXIX/BulkExportBBCollaborateRecordings - MIT License

