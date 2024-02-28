### digitalOceanCodeTest

#### Build a tool
##### Create an application that uses the GitHub APIs (GraphQL or Rest) to view files in a GitHub repo. For frontend focused create a UI and for backend focused create a CLI.

TO DO:

* Create a GitHub API key (with no permissions) so your sample is not rate limited
* Show a list of the files in the root
* Open directories
* Pay attention to their UI choices, folding, changing views and other strategies are valid
* Handle closing a directory and returning to the main view
* Add file previews
* Edit a text like file (plain <textarea> is fine) and push a commit to Git
* Add code highlighting

---

```
$ pip install PyGithub textual "textual[syntax]" && python .\main.py
```

* First the program will download the contents of the repo to ./repo using PyGithub, which provides a wrapper around the GitHub REST API v3

* We use PyGithub's get_repo() and get_contents("") to create an iterable over each file + folder
  * Iterating over contents we first discriminate between file and folder, if it's a folder we get_contents() again at the specific folders path
  * If it's a file, we write the content.
* Next we initialize Textual with a layout containing a Header, Footer, DirectoryTree and TextArea set to the code_editor constructor.

* User can then navigate between files and folders, visually with the mouse.

* Edited files can be saved (CTRL+S) to the disk

* After a file is edited, we can commit (CTRL+O) directly to the master branch of the desired repo.

* Similarly to the folder iterator to download the repo, in the callback function for Push Commit the following takes place:
  * If the file exists at our current path initialize PyGithub, and then try the following:
  * Open the file for reading, and calculate a relative path that doesn't include our programs path or repo folder
  * Grab the main branch because we need it for determining existing files and SHA
  * If it's an existing file, include the SHA and use PyGithub's update_file() otherwise use create_file()

### Example Use Case:
#### Edit and commit a file
* First create a config.json from the example and populate the key
* Then launch the program, edit a file, and save it (CTRL+S)

![image](https://github.com/ncorv/digitalOceanCodeTest/assets/33473556/325a4e01-a05b-4089-9cae-fb6f11fd799d)


* Commit the file to the branch (CTRL+O), the cursor will reset to the top of the file if successful, if not it will display the thrown exception in the TextArea
* https://github.com/ncorv/CodeTestEditRepo/commit/137086db6d4b71c1b0ccb2be797cff9d3ff79fd2
