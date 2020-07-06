# formify

# Python3

###### This is a static flask form app inspired by google forms

###### It is built with the google sheets api 

###### if the form is submited, the data is automatically saved in your created google sheet which is saved in your google drive 

## requirements:

    1.pip install the requirements in your activated environment

    2.client_secret.json -- this can be obtained from console.cloud.google.com after creating a project and creating an Oauth2 client

      save it here 'static/'

    3.the google sheets api must be activated in your project

    4.Google Account
  
## to start using:
    1.  run "python3 app.py"
### Running it for the first time:
    ***. In a different terminal/CMD/Shell run "python3 -i -m g_api" also

      it will ask to follow a certain link in in order to authorize
      then, it will ask you whether to create a new sheet - input y(for yes) or n(for no):
        if n:
          it will ask for a sheet_id in your google drive
         else:
          it will ask you to input a title
        
###### you can change the sheet_id anytime by running the function "set_sheet_id(id)" in g_api.py


###### if you want a sheet run "create_sheet(title)" it will automatically update the sheet_id in g_api.py

# !!!!ENJOY!!!!
      
        
  
  
