### Use Case Description
TODO: Write this

### Quick Setup
NOTE: This setup guide assumes a basic understanding of python / pip.

* `cd` to the root of this project in your shell of choice.
* Edit the `config.py` file updating the `REPOSITORIES` list
    * Owner - The owner of the repository to report on. In this case it would be "fritogotlayed"
    * Name - The name of the repository to report on. In this case it would be "pyReleaseUtility"
    * EnterpriseUrl - If you are running an enterprise github you would enter the short url here. (http://github.company.com)
    * ApiKey - The api key associated with the Owner/Name repository.
* NOTE: Now would be a good time to set up a virtualenv for the project. It is not necessary.
* Next you should install the requirements by running `pip install -r requirements.txt`
* Start the web server by running `python ./web_dashboard/__main__.py`
