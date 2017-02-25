### Use Case Description
TODO: Write this

### Quick Setup
NOTE: This setup guide assumes a basic understanding of python / pip.
NOTE: This setup guide assumes npm and bower have been installed on the target machine.

* `cd` to the root of this project in your shell of choice.
* Copy the `example-repositories.yml` to `repositories.yml` file, then update the `repositories` list
    * Owner - The owner of the repository to report on. In this case it would be "fritogotlayed"
    * Name - The name of the repository to report on. In this case it would be "pyReleaseUtility"
    * EnterpriseUrl - If you are running an enterprise github you would enter the short url here. (http://github.company.com)
    * ApiKey - The api key associated with the Owner/Name repository.
* NOTE: Now would be a good time to set up a virtualenv for the project. It is not necessary.
* Next you should install the requirements by running `pip install -r requirements.txt`
* Next you can `bower install` to fetch the required javascript packages for the UI.
* Start the web server by running `python ./web_dashboard/__main__.py`
