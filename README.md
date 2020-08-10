# Friends Toolkit
A simple tool based on [fbchat ](https://pypi.org/project/fbchat/) that allows to send multiple messages at the same time at own friends on Facebook.

#### UI
The user interface is web based and developed using micro framework [flask ](https://flask.palletsprojects.com/en/1.1.x/).


### Installation
First of all you need to install Python3 and pip package manager, you can download them at the [link ](https://www.python.org/downloads/).

Now, you can clone the project:


`$ git clone https://github.com/alexminichino/friends_toolkit.git`

(You can also directly donload the project end extract it)

After downloading you need to open project directory via terminal and run 
`$ pip install -e .`

If your OS is Windows you can lanch setup.bat script.

### Runing the tool

To start the tool you have to execute
`$ python main.py`

If your OS is Windows you can lanch start.bat script.

It's all, now you can use the tool.

## Usage 
After runnign to use tool you need to visit http://localhost:5000 page on your web browser.
The first time, you have to login via your facebook credentials.

Following are listed some screenshot of user interface!

<img src="/readmedia/login.png" width="100%">

After login, you can choose your frinds in list like following screen:

<img src="/readmedia/list.png" width="100%">

You can select all or select all who you not contacted before.

By clicking on "Compose message" will opening the next page in wich you can write your message:

<img src="/readmedia/message.png" width="100%">

In this are displayed selected frinds, below you can write the message to send in which you can use {{name}} to indicate complete name of your friends and {{first_name}} to indicate first name only.

The message could be like this:
Hi {{fisrt_name}}, how are you?
And th user (named for example John) will receive message with own first name:
Hi John, how are you?

Easy, right?

After, you can upload images to send after textual message, note that if you have uploaded images previously you can find them below and you can select directly without upload again.

Finally, the Minimum and Maximum waiting time are needed to define the waiting time between sending messages to user and the next one.
The waiting time is defined as random number between min_time and max_time.

When you click on "Send message" button you will redirected on friends list page, after that you can find a new button wich allow to download a report, in CSV format, in wich are reported infos like information on users, message, date and time of sended messages.

<img src="/readmedia/report.png" width="100%">

Note that frinds who are previously contacted are displayed in red in list!


## Contributing
I've created this project in few time, it can be certainly improved.
Any kind of contribute is very welcome!

Thanks a lot :heart:
