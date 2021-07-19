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

### Environment Set-Up 

* Clone the project to the desired server from the [https://igit.soton.ac.uk/Blackboard/collaborate-2-panopto appropriate iGit repository] 
* Install Python 3.9
* Obtain the most appropriate version of the [https://docs.conda.io/en/latest/miniconda.html package manager miniconda] for Python 3.9
* Ensure that Python [https://pip.pypa.io/en/stable/installing/ package manager 'Pip'] is installed on the server 

Once the above steps have been completed, navigate to the root directory of the project and run:

`conda env create -f environment.yml`

This will create a virtual environment and download all packages used by the application (and their dependancies) into it. Should any errors occurs during this step, conda will provide instructive error messages that should enable the problem to be solved. Dependancies can also be examined manually by viewing the environment.yml file.

On successful completion of the above, activate the project's environment by running:

`conda activate collaborate-to-panopto`

### API & SSL Config.

Collab-2-Panopto interacts with two external REST API services: namely the Blackboard Collaborate REST API, and the Panopto 
REST API. It also requires configuration details to enable successful sending of alert emails to service owners and maintainers. 
To enable this process, a configuration template <code>ConfigTemplate.py</code> is provided in the <code> /config/</code> folder. 

`credentials = {
    "verify_certs": "True",
    "collab_key": "Collab Key",
    "collab_secret": "Collab Secret",
    "collab_base_url": "us.bbcollab.com/collab/api/csa",
    "ppto_server": "panoptoServer",
    "ppto_client_id": "panoptoClientId",
    "ppto_client_secret": "panoptoClientSecret",
    "ppto_username": "panoptoUserName",
    "ppto_password": "panoptoPassword",
    "email_smtp_tls_port": "587",  # For SSL
    "smtp_server": "smtp.office365.com",
    "sender_email": "sender@url.com",
    "receiver_info_email": "receiver_info@url.com",
    "receiver_alert_email": "receiver_alert@url.com"
  }`

Please copy this into a new file, fill out the relevant details, and save the file as <code>Config.py</code> within the same directory.

### Config.py

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
    

Miniconda is used to manage dependancies - please ensure it's installed before proceeding. 

```bash 
conda env create -f environment.yml
conda activate collaborate-to-panopto
```

## High-Level Overview 



You'll need to obtain all of the BB and Panopto credentials given in the ConfigTemplate.py. Copy the template into a new file called Config.py and fill out accordingly.
(Note that your own specific Config.py will be included in the .gitignore).




